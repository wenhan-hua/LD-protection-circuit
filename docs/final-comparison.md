# A vs B — the decision

Each method is written up on its own, with its own schematic, numbers, simulation and bring-up:

- **[Method A — D1 + TVS, no series resistor](method-a-d1-tvs.md)** (V+ = 12 V)
- **[Method B — series 2 Ω + D1 + TVS](method-b-series-resistor.md)** (V+ = 12 V)

Shared background: [I MON and the TVS](imon-and-tvs.md). Both use a 1.5KE10A and a commanded 106 µs linear ramp.

| | **A** | **B** |
|---|---|---|
| Parts added | 2 leaded | 3, one a 50 W heatsinked resistor |
| **Safe ramp-down (I MON valid)** | **96 µs** | **96 µs** |
| Peak LDC during that ramp | **17.0 V** | 21.0 V |
| Clamp fires at | 18.9 V | 22.9 V |
| Driver dissipation | 13.8 W | 11.3 W |
| **Total heat in the system** | **20.0 W** | 30.0 W |
| Compliance margin | **3.5 V** | 2.5 V |
| **Ramp-up 0 → 2.5 A** | 204 µs | **175 µs** |
| Clamp-assisted decay (I MON blind) | 70 µs | 58 µs |

**The ramp-down speeds are identical**, and that is structural rather than a coincidence: peak LDC during a commanded linear ramp is V+ + L·I₀/T, and that peak lands at the end where i → 0 and the i·R term has vanished. R drops out, so a series resistor cannot help. It only speeds the clamp-assisted case, which is the mode you give up when I MON has to stay valid.

**Recommendation: method A.** Same ramp-down, 4 V less stress on an LDC pin with no published rating, 10 W less heat, a wider compliance margin, one fewer part to mount, and the clamp can be moved to the coil for cable-break protection. Choose B only if 29 µs of ramp-up is worth 12.5 W and a power resistor.
