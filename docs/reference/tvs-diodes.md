# TVS diodes — background knowledge

Standalone reference for anyone picking up this project who has not worked with transient
voltage suppressors before. **Nothing here is specific to the MOT coil** — for the sizing
decisions in this design see [clamp-sizing-and-imon.md](clamp-sizing-and-imon.md), and for the design itself
see [design-summary.md](../design-summary.md).

The aim is that if the chosen part goes obsolete, or someone needs to re-pick it for a
different coil, they can do it from this document plus a manufacturer datasheet.

---

## 1. What a TVS is

A **transient voltage suppressor** is a silicon avalanche diode with a deliberately large
junction area, built to absorb short, high-current overvoltage pulses and clamp its terminal
voltage while doing so.

Physically it is a zener diode. The difference is entirely one of design intent and rating:

| | Zener | TVS |
|---|---|---|
| Rated for | **continuous** power (e.g. 5 W) | **peak pulse** power (e.g. 1500 W for 1 ms) |
| Characterised at | tens to hundreds of mA | tens to hundreds of **A** |
| Junction area | small | large |
| Dynamic resistance | high (~1.6 Ω for a 5 W part) | low (~0.05 Ω for a 1.5KE) |
| Use | voltage reference, low-current regulation | transient protection |

**This distinction is the reason a TVS is used here and not a zener.** At the 2.5 A this
circuit has to clamp, a 5 W zener's dynamic resistance would add several poorly-controlled
volts on top of its nominal breakdown. A 1.5KE part is characterised at over 100 A, so at
2.5 A it sits essentially *at* its breakdown voltage — a flat, predictable clamp.

## 2. The three operating regions

A unidirectional TVS, reverse-biased:

```
  current
     ^
     |                                    /|  <- (3) breakdown: conducts hard,
     |                                   / |      voltage ~flat
     |                                  /
     |                            ..--''    <- (2) knee: begins to conduct
     |  ____________________..--''
     +--------------------------------------> reverse voltage
     0        V_wm        V_br      V_c
         (1) standoff:
         leakage only
```

| Region | Bound | Behaviour |
|---|---|---|
| **(1) Standoff** | V < **V_wm** | Effectively open. Only leakage flows (µA). This is where the part sits in normal operation. |
| **(2) Knee** | V_wm → **V_br** | Begins to conduct. Leakage climbs steeply. **Avoid operating here** — the boundary is mushy and varies part to part. |
| **(3) Breakdown** | V > V_br | Conducts hard, holding terminal voltage roughly constant regardless of current, up to **V_c** at rated peak current. |

**Design rule that follows:** put your normal operating voltage comfortably below V_wm, and
size for the worst case at V_c. The region between is not a place to live.

## 3. The parameters that matter

Using the **1.5KE10A** (the part in this design) as the worked example. Values from the
[Vishay 1.5KE datasheet](https://www.vishay.com/docs/88301/15ke.pdf); confirm against
whichever manufacturer you actually buy, as they differ slightly.

| Symbol | Name | 1.5KE10A | What it means |
|---|---|---|---|
| **V_wm** | Stand-off / working peak reverse voltage | **8.55 V** | Highest voltage you may apply continuously. Below this, leakage only. **This is the number that sets how fast you can ramp** while the clamp stays off. |
| **V_br** | Breakdown voltage | **9.50–10.50 V** @ 1 mA | Where real conduction starts. Quoted as a range — that range *is* the part tolerance. |
| **V_c** | Clamping voltage | **15.0 V** @ 100 A | Terminal voltage at full rated pulse current. **The worst case your protected circuit will ever see.** |
| **I_pp** | Peak pulse current | **100 A** | Current at which V_c is specified, for the rated waveform. |
| **P_pp** | Peak pulse power | **1500 W** | For a 10/1000 µs exponential pulse at 25 °C. Not a continuous rating. |
| **I_R** | Reverse leakage | **≤5 µA** @ V_wm | Leakage in the standoff region. Matters when the TVS parallels a load. |
| **C** | Junction capacitance | ~1 nF order | Large, because the die is large. Irrelevant here; critical in RF or high-speed data lines. |

Two derived quantities worth knowing:

- **Clamping factor** = V_c / V_wm ≈ **1.75** for the 1.5KE family. A lower factor is a
  tighter clamp. This is where silicon TVS devices beat MOVs badly.
- **Dynamic resistance** = (V_c − V_br) / I_pp ≈ (15.0 − 10.0) / 100 = **0.05 Ω**. This is
  what makes the clamp flat at low currents.

### Reading the part number

```
   1.5 K E   10   A
   ---------  --  --
       |       |   |
       |       |   +-- tolerance: A = +/-5%  |  (none) = +/-10%
       |       |                             CA = BIDIRECTIONAL (+/-5%)
       |       +------ stand-off voltage in volts (NOT breakdown)
       +-------------- family: 1.5 kW peak pulse power, axial
```

| Family | Peak pulse power | Package |
|---|---|---|
| **1.5KE** | 1500 W | axial leaded, DO-201AE / DO-27 |
| P6KE | 600 W | axial leaded, DO-15 |
| SMAJ | 400 W | surface mount, DO-214AC |
| SMBJ | 600 W | surface mount, DO-214AA |
| SMCJ | 1500 W | surface mount, DO-214AB |

**The `CA` trap.** A `C` in the suffix means **bidirectional** — two junctions back to back,
so it conducts in *both* directions above standoff and never blocks. In this design that
would defeat the whole point: D1's blocking action would be pointless because the TVS itself
has to be the forward-blocking element in normal operation. **Order `1.5KE10A`, never
`1.5KE10CA`.** This is called out in [order-list.md](../order-list.md) because the part numbers
differ by one character and sit next to each other in distributor search results.

## 4. Unidirectional vs bidirectional

| | Unidirectional (`10A`) | Bidirectional (`10CA`) |
|---|---|---|
| Structure | one avalanche junction | two, back to back |
| Reverse direction | clamps at V_br | clamps at V_br |
| Forward direction | **conducts like an ordinary diode at ~1 V** | clamps at V_br |
| Use on | DC rails with known polarity | AC lines, signal lines that swing both ways |

**Use unidirectional on anything with a fixed polarity**, which includes essentially every DC
supply rail and this circuit. The forward conduction of a unidirectional part is not a
defect — in many topologies it is the freewheel path you want.

## 5. Pulse ratings are not continuous ratings

**A 1500 W TVS cannot dissipate 1500 W, or even 5 W, continuously.** The rating is for a
specific pulse shape, and it derates three ways:

- **Pulse width.** The 1500 W figure is for a **10/1000 µs** waveform (10 µs rise, decay to
  half in 1000 µs). Shorter pulses allow much more power, longer pulses much less. Every
  datasheet has a log-log "peak pulse power vs pulse time" curve — **use it rather than
  interpolating by instinct.**
- **Temperature.** Rated at 25 °C, derating linearly to **zero at T_j = 175 °C**. A part in
  a warm enclosure has materially less capability.
- **Repetition.** The rating assumes a non-repetitive pulse. Repetitive pulsing requires
  derating by duty cycle, because the junction has no time to cool.

**Energy, not just power, is the honest check.** For a 1.5KE at 1 ms, the capability is
roughly 1500 W × 1 ms ≈ **1.5 J**.

> In this design the coil stores **½LI₀² = 1.19 mJ** — about **0.08 %** of that. Peak clamp
> current is **2.5 A** against a 100 A rating, **2.5 %**. The TVS is enormously
> over-specified for the energy, and that is deliberate: it was chosen for its *standoff
> voltage*, which sets the ramp speed, not for its energy capability. See
> [clamp-sizing-and-imon.md](clamp-sizing-and-imon.md) §"Why I MON goes blind".

This is the usual situation with inductive-kick clamps on small coils. The problem is
**voltage**, not energy — 1.19 mJ is harmless as heat and destructive as volts into a high
impedance.

## 6. How a TVS compares to the alternatives

| Device | Clamp flatness | Energy | Speed | Wears out? | Notes |
|---|---|---|---|---|---|
| **Silicon TVS** | **good** (factor ~1.75) | moderate | **<1 ns** | no | The default for board-level DC protection |
| Zener | good at low current, poor at high | low | <1 ns | no | Dynamic resistance ruins it above ~0.5 A |
| **MOV** (varistor) | poor (factor 2.5–4) | **very high** | ~ns | **yes — degrades every strike** | Mains surge protection; clamp voltage drifts down over life |
| **GDT** (gas tube) | crowbar, not clamp | **highest** | **slow, ~µs** | slowly | Cannot extinguish a DC arc once struck — dangerous on DC rails |
| Schottky diode | V_f only | low | fast | no | **Leakage climbs steeply when hot** — see below |
| Flyback diode (Si) | V_f only (~1 V) | depends | fast | no | Safe and cheap, but the low clamp means a *slow* decay |

**On Schottky diodes specifically** — this design uses a silicon ultrafast (MUR460) for D1,
not a Schottky, and the reason generalises. A Schottky's low forward drop is attractive, but
its **reverse leakage reaches tens of mA at elevated temperature**. Sitting in parallel with
the coil, that leakage is current the driver regulates but the coil never receives — so the
field would be quietly, temperature-dependently wrong. In a precision current application,
**prefer silicon and accept the extra 0.3 V.**

**On flyback diodes** — a plain diode across an inductor is the textbook answer and is
perfectly safe. Its weakness is speed: it clamps at its own forward drop (~0.95 V at 2.5 A),
so the current decays at essentially L/R. Here that is **403 µs versus 96 µs**. You buy ramp
speed with clamp voltage, and nothing else.

## 7. Selection procedure

For clamping an inductive kick on a DC rail, in order:

1. **Find the maximum normal operating voltage** the TVS will see, including supply
   tolerance, ripple, and any in-regulation excursion. → **V_wm must exceed this.**
2. **Find the absolute maximum the protected part can survive.** → **V_c must stay below
   this**, with margin.
3. **Check steps 1 and 2 are compatible.** V_c ≈ 1.75 × V_wm for this family, so if your
   protected maximum is less than ~1.75× your operating voltage, a single TVS cannot do it
   and you need a different topology.
4. **Compute the pulse energy** (½LI² for an inductor) and check it against the derated
   rating at your pulse width and temperature. Usually passes by orders of magnitude for
   small coils.
5. **Check the peak current** against I_pp.
6. **Check leakage** at V_wm if the part parallels a precision load.
7. **Pick the tolerance and polarity suffix.** `A` for ±5 %, no `C` unless you genuinely
   need bidirectional.

> **Step 3 is where this design very nearly failed.** The LD5CHA has **no published maximum
> LDC voltage** — so there is no number to put in step 2. The 22.9 V clamp is a judgement
> call anchored to the only nearby published figure, the 28 V compliance at a 30 V supply.
> This is the largest open question in the project; see [design-summary.md](../design-summary.md)
> §10.

## 8. Failure modes

- **A TVS normally fails short.** For a protection device this is usually the safe direction
  — the protected circuit survives — but it shorts whatever the TVS is across. **In this
  design a shorted TVS puts D1 straight across the coil**, which degrades gracefully to the
  "D1 alone" case: still safe, ramp-down drops to ~403 µs. That is a benign failure, and
  worth knowing because it will not announce itself except as a slower ramp.
- **Gross overstress can fail it open**, by blowing the bond wire. This is the dangerous
  mode: protection silently gone, no symptom until the next transient. Far outside the
  energy regime here.
- **D1 failing short** removes the blocking action, so the TVS sees forward voltage in normal
  operation and shunts the coil. That one *would* be obvious — I MON and the field disagree
  immediately.

**Neither device is in the current path during normal operation**, so neither sees wear. A
periodic check that steady-state LDC is still ≈ 9.5 V at 2.5 A would catch a shorted TVS.

## 9. Bench practice

- **Measure V_br before trusting it.** Apply reverse voltage through a current-limiting
  resistor (10 kΩ from a bench supply is plenty) and find the voltage at 1 mA. With ±5 %
  parts and a design this sensitive to standoff, the individual part matters. Buy spares and
  measure a few — [order-list.md](../order-list.md) includes bench-tuning spares for this reason.
- **Identify the cathode by the band**, then confirm with a diode-test meter — in series
  cathode-to-cathode, a reversed part gives you a forward-conducting path across the coil,
  which is a quiet and confusing failure.
- **Probe clamp voltage differentially.** In this circuit neither terminal is at ground, so a
  scope ground clip across the clamp **shorts LDC to ground**. Use a differential or isolated
  probe.
- **Expect the datasheet to be optimistic about corners.** Package inductance means a real
  clamp overshoots briefly above V_c on a fast edge. With a ~0.8 µs driver loop and leaded
  parts this is not a concern here, but it matters above a few MHz.

## 10. Sources

| | |
|---|---|
| [Vishay 1.5KE series](https://www.vishay.com/docs/88301/15ke.pdf) | Primary datasheet for the family used here |
| [Littelfuse 1.5KE series](https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_1_5ke_datasheet.pdf.pdf) | Second source; leakage figures differ slightly |
| [Wavelength LDxCHA datasheet](https://www.teamwavelength.com/download/Datasheets/LD15CHA.pdf) | The driver being protected |
| Manufacturer datasheets, §"Ratings and Characteristic Curves" | The pulse-power derating curves and the 10/1000 µs waveform definition live in the datasheets above, not in a separate note — read them there |

**Caveat on every number in this document:** parameter values are quoted from the Vishay and
Littelfuse 1.5KE datasheets as a worked example and vary between manufacturers — Vishay and
SMC disagree on leakage for some parts in the family by 5×. Confirm against the datasheet for
the part you actually order.
