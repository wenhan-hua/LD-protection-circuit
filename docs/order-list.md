# DigiKey order list — Method A

For [method A](method-a-d1-tvs.md): D1 + TVS across the driver's J1 terminal block, V+ = 8 V, 2.5 A.

## Core parts

| Ref | Description | Manufacturer part number | Qty | Why this one |
|---|---|---|---|---|
| **TVS** | 1.5 kW unidirectional TVS, 10 V, axial DO-201 | **1.5KE10A** (Littelfuse, Vishay or onsemi) | 5 | 8.55 V standoff sets the 96 µs ramp; flat clamp at 2.5 A |
| **D1** | 4 A / 600 V ultrafast rectifier, axial DO-201AD | **MUR460** (onsemi `MUR460RLG`, or Vishay) | 5 | Blocks the clamp in normal operation; silicon, low leakage |
| — | 6-position barrier terminal block | **6-141** (Cinch) or any barrier strip | 2 | Joins D1 and the TVS cathode-to-cathode and lands on J1 |
| — | Heat-shrink assortment, 2–6 mm | any | 1 | Insulate the D1–TVS joint |

Five of each on the semiconductors because they cost well under a dollar and are the parts most likely to be damaged while you find the real ramp limit on the bench.

## Strongly recommended — TVS options for bench tuning

Step 5 of the bring-up is *shorten the ramp until the clamp fires, then back off*. The right TVS depends on what that measurement gives you, so buy the neighbours now rather than waiting on a second order:

| Part | Standoff | Ramp you can run | Peak LDC at 8 V | Clamp fires at | Qty |
|---|---|---|---|---|---|
| 1.5KE6.8A | 5.80 V | 138 µs | 14.2 V | 15.8 V | 3 |
| **1.5KE10A** | **8.55 V** | **96 µs** | **17.0 V** | **18.9 V** | **5** |
| 1.5KE15A | 12.80 V | 65 µs | 21.2 V | 23.9 V | 3 |

## Optional

| Item | Manufacturer part number | Qty | Why |
|---|---|---|---|
| 1N5408 (3 A, 1000 V rectifier) | **1N5408** (Vishay or onsemi) | 5 | Cheaper, more widely stocked fallback for D1. Slower recovery, but it turns off softly here so it is perfectly adequate |
| Current-sense shunt, 50 mΩ, 3 W, 1 % | e.g. Vishay **LVR03R0500FE73** | 2 | Only if you want to watch a clamp-assisted decay — I MON cannot see it ([why](imon-and-tvs.md)) |

## Paste-ready list

DigiKey's **bulk add / BOM Manager** accepts manufacturer part numbers:

```
1.5KE10A, 5
1.5KE6.8A, 3
1.5KE15A, 3
MUR460RLG, 5
1N5408, 5
6-141, 2
```

## Before you click order

- **Unidirectional, not bidirectional.** `1.5KE10A` is unidirectional; `1.5KE10**C**A` is bidirectional and would conduct in both directions, shorting the coil in normal operation. The absence of a `C` is the whole difference. Check it on every TVS line.
- **Several manufacturers share the 1.5KE numbering** (Littelfuse, Vishay, onsemi, SMC). Any is fine — pick one with stock. The packaging suffixes (`-E3/54`, `RL4G`, …) only set lead finish and tape/bulk, not the electrical part. Leakage specs differ slightly between manufacturers; see [imon-and-tvs.md](imon-and-tvs.md).
- **Do not substitute a Schottky for D1.** Schottky leakage reaches tens of mA when hot, and it flows in parallel with the coil, so the coil would receive measurably less current than the driver regulates.
- **Not on this list:** the 8 V / ≥3 A supply, the function generator for the MOD INPUT ramp, a differential or isolated scope probe for LDC, and the driver heatsink (Wavelength's recommended part is the MULTI-HTSK, bought from them rather than DigiKey).
- Part numbers here are manufacturer numbers, not DigiKey stock numbers. Confirm the exact orderable variant and current stock at the time you order.
