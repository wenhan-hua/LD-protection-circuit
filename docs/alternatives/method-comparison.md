# A vs B — the decision

Each method is written up on its own, with its own schematic, numbers, simulation and bring-up:

- **[Method A — D1 + TVS, no series resistor](../final-design.md)** (V+ = 12 V)
- **[Method B — series 2 Ω + D1 + TVS](series-resistor.md)** (V+ = 12 V)

Shared background: [I MON and the TVS](../reference/clamp-sizing-and-imon.md). Both use a 1.5KE10A and a commanded 106 µs linear ramp.

Both compared at the **same V+ = 12 V**, same TVS, same commanded ramp — otherwise the comparison measures the rail, not the method.

| | **A** | **B** |
|---|---|---|
| Parts added | **2 leaded** | 3, one a 50 W heatsinked resistor |
| **Safe ramp-down (I MON valid)** | **96 µs** | **96 µs** |
| Peak LDC during that ramp | **21.0 V** | **21.0 V** |
| Clamp fires at | 22.9 V | 22.9 V |
| Driver dissipation | 23.8 W (95 % of 25 W) | **11.3 W (45 %)** |
| Series resistor dissipation | — | 12.5 W |
| **Total heat in the system** | **30.0 W** | **30.0 W** |
| Compliance margin | **7.53 V** | 2.52 V |
| **Ramp-up 0 → 2.5 A** | **109 µs** | 175 µs |
| Clamp-assisted decay (I MON blind) | 70 µs | 58 µs |
| Clamp can mount at the coil | **yes** | no |

Three rows are *identical by construction*, and seeing why settles the decision:

- **Ramp-down (96 µs) and peak LDC (21.0 V).** Peak LDC during a commanded linear ramp is V+ + L·I₀/T, and that peak lands at the **end**, where i → 0 and the i·R term has vanished. **R drops out.** A series resistor cannot reduce LDC stress or buy ramp-down speed. It only speeds the clamp-assisted case — the mode you give up when I MON has to stay valid.
- **Total heat (30.0 W).** It is exactly V+ · I₀ in both cases. R_loop decides only *where* the heat lands, never how much there is. Method B relocates 12.5 W out of the driver; it does not remove it.

So B's one genuine benefit is thermal: it takes the driver from 95 % of its no-airflow rating down to 45 %. It pays for that with 66 µs of ramp-up, 5 V of compliance margin, a power resistor to mount and heatsink, and the ability to put the clamp at the coil.

**Recommendation: method A, plus a 40 mm fan.** The fan buys the same thermal headroom B offers (95 % → 68 % of limit) for a few dollars and no electrical compromise, while keeping the faster ramp-up, the wider compliance margin and the two-part build. Choose B only if forced air is impossible in your setup.

> An earlier version of this table compared A at 8 V against B at 12 V, which made B look like it reduced LDC stress and total heat. It does neither. Holding both to the same rail is what exposes that.
