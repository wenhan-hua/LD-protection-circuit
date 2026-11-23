# I MON, and what the TVS actually does

Script: [imon_valid_sizing.py](../../scripts/imon_valid_sizing.py) · [output](../../outputs/imon-valid-sizing.txt).
Shared background for [method A](../final-design.md) and [method B](../alternatives/series-resistor.md).

## I MON reference

| | |
|---|---|
| Pin | **J3:2** (ground on J3:4) |
| Transfer function, LD5CHA | **2 A/V** in CC and CP modes — 2.5 A reads 1.25 V |
| Accuracy | **0.64 % of full scale** = ±32 mA on the 5 A model |
| Datasheet | [Wavelength LDxCHA datasheet](https://www.teamwavelength.com/download/Datasheets/LD15CHA.pdf) — pin table p. 4, transfer functions Table 2 p. 5, monitor accuracy p. 7 |
| Product page | [LD5CHA](https://www.teamwavelength.com/product/ld5cha-5-a-30-v-laser-diode-driver/) |

Note the ±32 mA: that is the monitor's own error against the transfer function, and it is much larger than any effect the clamp has. Do not expect I MON to resolve better than that.

## What the TVS is doing

> For the device physics, parameter definitions, part-number decoding, selection procedure and failure
> modes — none of it specific to this coil — see **[tvs-diodes.md](tvs-diodes.md)**.
> This section covers only what the TVS does *in this circuit*.

A TVS (transient voltage suppressor) is a zener diode built for short, high-current pulses. It has three regions:

- **Below its standoff voltage V_wm** — effectively an open circuit, leakage only.
- **Between V_wm and breakdown V_br** — begins to conduct.
- **Above V_br** — conducts hard and holds its terminal voltage roughly constant however much current flows.

It is rated in *peak pulse power* (1500 W for 1 ms in the 1.5KE family), not continuous watts.

**Its one job here is to set the voltage the coil has to push against when the driver is no longer controlling the current.** A coil sheds current at L·di/dt = the opposing voltage, so:

| Clamp | Volts the coil works against | Decay 2.5 A → 10 % (R = 0.99 Ω) |
|---|---|---|
| D1 alone | 0.95 V | 403 µs |
| D1 + 1.5KE10A | 10.9 V | 70 µs |

That voltage appears on LDC, stacked on top of V+. **So TVS voltage = speed, and equally = stress on the driver.** That is the whole trade.

### Why D1 and the TVS sit in series, cathode to cathode

| State | LDC vs LDA | D1 | TVS | Current in the clamp |
|---|---|---|---|---|
| Steady 2.5 A | LDC *below* LDA | reverse — **blocks** | forward (irrelevant) | ~0, only D1's µA leakage |
| Commanded ramp | LDC above LDA, below standoff | forward | reverse, below V_wm | leakage only |
| Fault / abrupt cut | LDC well above LDA | forward | **breakdown** | the full coil current |

D1 is what makes the clamp invisible in normal operation. Without it, the TVS would simply conduct forward and shunt the coil.

**Why a TVS and not an ordinary zener:** a 5 W zener is specified at a couple of hundred mA; at 2.5 A its dynamic resistance (~1.6 Ω) adds several volts of poorly-controlled drop. A 1.5KE part is characterised at over 100 A, so at 2.5 A it sits essentially at its breakdown voltage.

## Why I MON goes blind, and how to avoid it

**I MON measures current through the driver's internal sense element, not the current in the coil.** The moment the clamp conducts, the coil current freewheels LDC → D1 → TVS → LDA and bypasses the driver entirely, so **I MON reads ~0 while the coil is still carrying amps.** This is structural — no clamp topology avoids it, because freewheeling *means* bypassing the driver.

The fix is to **stop using the clamp as the ramp mechanism.** Size it to sit *above* the working ramp so it only fires on faults. Then the driver stays in regulation and I MON stays true.

With a commanded linear ramp of duration T and the driver in regulation:

> LDC(t) = V+ − i·R + L·I₀/T → peaks at the **end** (i → 0) at **V+ + L·I₀/T**

Keep that peak below the TVS standoff and the clamp never conducts.

| TVS | Standoff V_wm | Usable ΔV | Ramp T | t to 10 % | Leakage during the ramp |
|---|---|---|---|---|---|
| 1.5KE6.8A | 5.80 V | 6.2 V | 153 µs | 138 µs | ≤1000 µA |
| **1.5KE10A** | **8.55 V** | **9.0 V** | **106 µs** | **96 µs** | ≤5 µA |
| 1.5KE15A | 12.80 V | 13.2 V | 72 µs | 65 µs | ≤1 µA |
| 1.5KE18A | 15.30 V | 15.7 V | 61 µs | 54 µs | ≤1 µA |

Peak LDC during the ramp is V+ + ΔV, and the clamp fires at V+ + V_br + 0.95 V.

### On the 1.5KE6.8A and its leakage — a correction

An earlier version of this note said the 1.5KE6.8A's leakage disqualified it. **That overstated the case.** The reasoning is worth getting right:

- In **steady state** D1 is reverse-biased, so no TVS leakage flows at all. The coil gets exactly what the driver regulates.
- The TVS is only reverse-biased **during the ramp**, when LDC rises above LDA. There the 1.5KE6.8A can leak up to 1000 µA — 400 ppm of 2.5 A, for about 100 µs. That is negligible for the field, and well inside I MON's own ±32 mA accuracy.

**The real reason to prefer the 1.5KE10A is its standoff voltage, not its leakage:** 8.55 V vs 5.80 V, which is what sets how fast you can ramp while the clamp stays off — 96 µs vs 138 µs. A secondary reason is that the 6.8 V part's leakage climbs steeply as you approach standoff, so the boundary between "clamp off" and "clamp conducting" is mushy and the ramp less repeatable.

Leakage figures: [Vishay 1.5KE series](https://www.vishay.com/docs/88301/15ke.pdf), [Littelfuse 1.5KE series](https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_1_5ke_datasheet.pdf.pdf). Values differ slightly by manufacturer (SMC lists 5 µA for the 1.5KE15A where Vishay lists 1 µA).

## If you do need to watch the fast clamp-assisted decay

Then I MON structurally cannot give it to you, and you need an external sense: a 10–50 mΩ shunt in series with the coil (read with a differential amplifier, since neither end is at ground) or a Hall/fluxgate current probe. That also lets you use clamp-assisted decay for the extra speed without going blind.

## Caveats

- V_wm and leakage figures come from the Vishay/Littelfuse 1.5KE datasheets; confirm against the manufacturer you actually buy.
- D1's forward drop is taken as 0.4 V at leakage currents and 0.95 V at 2.5 A.
- "Driver stays in regulation" assumes its loop tracks the commanded ramp — it has ~0.8 µs rise/fall, so this should hold, but confirm on a scope that LDC never reaches the clamp during a normal ramp.
