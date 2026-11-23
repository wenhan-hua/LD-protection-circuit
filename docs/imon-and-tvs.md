# Keeping I MON valid — and what the TVS actually does

Script: [imon_valid_sizing.py](../scripts/imon_valid_sizing.py) · [output](imon_valid_output.txt).
Applies to both [chosen-design.md](chosen-design.md) and [alt-design-d1-zener.md](alt-design-d1-zener.md).

## What the TVS is doing

A TVS (transient voltage suppressor) is a zener diode built for short, high-current pulses. It has three regions:

- **Below its standoff voltage V_wm** it is effectively an open circuit — leakage only.
- **Between V_wm and its breakdown V_br** it begins to conduct.
- **Above V_br** it conducts hard and holds its terminal voltage roughly constant no matter how much current flows.

It is rated in *peak pulse power* (1500 W for 1 ms in the 1.5KE family), not continuous watts.

**Its one job in this circuit is to set the voltage the coil has to push against when the driver is no longer controlling the current.** A coil sheds current at a rate L·di/dt = (whatever voltage opposes it), so:

| Clamp | Volts the coil works against | Decay 2.5 A → 10 % |
|---|---|---|
| D1 alone | 0.95 V | 403 µs |
| D1 + 1.5KE10A | 10.9 V | 70 µs |

That voltage appears on LDC, stacked on top of V+. **So TVS voltage = speed, and equally TVS voltage = stress on the driver.** That is the whole trade.

### Why D1 and the TVS are in series, cathode to cathode

| State | LDC vs LDA | D1 | TVS | Current in the clamp |
|---|---|---|---|---|
| Steady 2.5 A | LDC *below* LDA | reverse — **blocks** | forward (irrelevant) | ~0, only D1's µA leakage |
| Commanded ramp, LDC above LDA but below standoff | forward | reverse, below V_wm | leakage only |
| Fault / abrupt cut | LDC well above LDA | forward | **breakdown** | the full coil current |

D1 is what makes the clamp invisible in normal operation. Without it the TVS would simply conduct forward and shunt the coil. D1 also hides the TVS's leakage in steady state, which matters — see below.

**Why a TVS and not an ordinary zener:** a 5 W zener is specified at a couple of hundred mA; at 2.5 A its dynamic resistance (~1.6 Ω) adds several volts of poorly-controlled drop. A 1.5KE part is characterised at over 100 A, so at 2.5 A it sits essentially at its breakdown voltage.

## Why I MON goes blind, and how to fix it

**I MON measures the current through the driver's internal sense element, not the current in the coil.** The moment the clamp conducts, the coil current freewheels LDC → D1 → TVS → LDA and bypasses the driver entirely. The driver sinks almost nothing, so **I MON reads ~0 while the coil is still carrying amps.** This is structural — no clamp topology can avoid it, because freewheeling *means* bypassing the driver.

The fix is to **stop using the clamp as the ramp mechanism.** Size it so it sits *above* the working ramp and only fires on faults. Then the driver stays in regulation the whole way down and I MON stays true.

With a commanded linear ramp of duration T and the driver in regulation:

> LDC(t) = V+ − i·R + L·I₀/T  → peaks at the **end** (i → 0) at **V+ + L·I₀/T**

Keep that peak below the TVS standoff and the clamp never conducts.

| TVS | Usable ΔV | Ramp T | t to 10 % | Working peak LDC at V+ = 8 V | Fault clamp | Leakage error on I MON |
|---|---|---|---|---|---|---|
| 1.5KE6.8A | 6.2 V | 153 µs | 138 µs | 14.2 V | 15.8 V | **400 ppm** |
| **1.5KE10A** | **9.0 V** | **106 µs** | **96 µs** | **17.0 V** | **18.9 V** | 2 ppm |
| 1.5KE15A | 13.2 V | 72 µs | 65 µs | 21.2 V | 23.9 V | <1 ppm |
| 1.5KE18A | 15.7 V | 61 µs | 54 µs | 23.7 V | 26.9 V | <1 ppm |

**Do not use the 1.5KE6.8A.** Low-voltage TVS parts leak badly: the 1.5KE6.8A is specified at up to **1000 µA** at its 5.80 V standoff, against the driver's ~200 ppm (0.5 mA) stability — a 400 ppm error exactly when the ramp is running. The 1.5KE15A is specified at about 1 µA. Sources: [Vishay 1.5KE series](https://www.vishay.com/docs/88301/15ke.pdf), [Littelfuse 1.5KE series](https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_1_5ke_datasheet.pdf.pdf). (That leakage only flows while LDC is above LDA, i.e. during the ramp — D1 blocks it in steady state.)

## Recommended operating point

**V+ = 8 V, D1 + 1.5KE10A, commanded linear ramp of 106 µs.**

| | |
|---|---|
| Ramp down to 10 % | **96 µs**, driver in regulation throughout |
| **I MON** | **valid the whole way** |
| Working peak LDC | 17.0 V |
| Clamp fires at | 18.9 V — faults only |
| Driver dissipation | 13.8 W (55 % of the 25 W no-airflow limit) |
| Steady LDC | 5.5 V (3.5 V above the 2 V compliance floor) |

The cost of keeping I MON valid is modest: 96 µs instead of the 70 µs you would get by letting the same TVS do the work.

## This weakens the case for the series resistor

For a **commanded linear ramp**, peak LDC occurs at i → 0, where the i·R term has vanished. So **R drops out entirely and a series resistor buys no ramp-down speed at all.** Rs still helps with:

- driver dissipation (12.5 W moved out of the driver), though lowering V+ does the same for free;
- ramp-**up** speed, since it drops LDC without dropping V+;
- clamp-assisted decay, which you are no longer using.

Given the I MON constraint, [the simpler D1 + TVS design](alt-design-d1-zener.md) at V+ = 8 V is the better choice unless ramp-up speed is critical.

## If you do need to see the fast decay

Then I MON structurally cannot give it to you, and you need an external sense: a 10–50 mΩ shunt in series with the coil (differential amplifier, since neither end is at ground) or a Hall/fluxgate current probe. That also lets you use clamp-assisted decay for the extra speed without going blind.

## Caveats

- V_wm and leakage figures are from the Vishay/Littelfuse 1.5KE datasheets; confirm against the manufacturer you actually buy, as values differ slightly (SMC lists 5 µA for the 1.5KE15A where Vishay lists 1 µA).
- The 1.5KE10A standoff (8.55 V) should be checked on the specific datasheet.
- D1's forward drop is taken as 0.4 V at leakage currents and 0.95 V at 2.5 A.
- "Driver stays in regulation" assumes its loop tracks the commanded ramp — it has ~0.8 µs rise/fall, so this should hold, but confirm on a scope that LDC never reaches the clamp during a normal ramp.
