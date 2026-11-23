# LD5CHA driving the coil directly (rev 3, V+ = 12 V)

**Original configuration** (no external protection):

![original](direct_drive.png)

Variant with an optional freewheel diode D1: [direct_drive_with_D1.png](direct_drive_with_D1.png)

Sources: [draw_direct_drive.py](../scripts/draw_direct_drive.py), [sim_direct_drive.py](../scripts/sim_direct_drive.py), [sim output](direct_drive_sim_output.txt)

## Assumptions
- Coil L = 0.38 mH, coil R = 0.19 Ω ([coil-estimate.md](coil-estimate.md)); cables add about 0.8 Ω, so R_total ≈ 1.0 Ω and τ ≈ 0.38 ms.
- V+ = 12 V, target 3 A. LDA is tied to V+ inside the driver (low-side sink). A heatsink is attached to the driver.
- The datasheet documents **no internal clamp** across the output and never mentions inductive loads ([datasheet-check.md](datasheet-check.md)). The diagrams show no D1 in the original configuration.

## How close is 12 V to the limits?
| Limit | Value at V+ = 12 V, 3 A | Margin |
|---|---|---|
| Supply range (5…30 V) | 12 V | Well inside |
| Compliance: V+ − 2 V ≥ I·R | 10 V available vs 3.0–3.1 V needed (max current ≈ 10 A, driver limit 5 A) | Large |
| Driver power dissipation (V+ − I·R)·I | **≈ 27 W** (26.7 W with a hot coil) | Datasheet ([datasheet-check.md](datasheet-check.md)): 25 W with no airflow, **35 W with 5.5 CFM airflow**, both at 25 °C ambient. So 27 W is about 8 % over the no-airflow limit and about 23 % under the airflow limit. |
| Break-even V+ for 25 W at 3 A | ≈ 11.3–11.6 V | 12 V is just beyond it |
| LDC at idle (0 A) | 12 V (= V+) | Normal operation |

**Dissipation is the only real constraint.** The datasheet requires heatsinking, and the 35 W figure assumes airflow (5.5 CFM, about a small fan). A heatsink alone isn't covered by the datasheet number. Things to do:
- Run the Wavelength SOA calculator with the actual heatsink and ambient temperature.
- Watch the driver case temperature during the first minutes at 3 A.
- If the coil runs below 3 A or pulsed, the dissipation drops. At 2.5 A it is about 24 W, and it is lower still at low duty cycle.
- If the case runs hot, dropping V+ to 11 V gives about 24 W at 3 A.

## Turn-off behaviour without D1
Stored energy at 3 A is only ½·L·I² = 1.7 mJ. What matters is how the current is interrupted:
- **Controlled ramp by the setpoint** (driver stays in regulation): LDC = V+ − I·R − L·di/dt. For a linear 3 A → 0 ramp in 1 ms the final overshoot is L·di/dt = 0.38 mH × 3 A/ms ≈ **1.1 V above V+**, with no clamp needed. A 0.5 ms ramp gives about 2.3 V. This is my own estimate and assumes the loop tracks the setpoint.
- **Abrupt interruption** (enable off, fault trip, 5 V logic loss, unplugging): the sink transistor stops conducting and LDC flies up (for example 3 A in 10 µs gives about 114 V) until the transistor avalanches or an internal clamp, if any, conducts. This is the case D1 covers.
- With D1: LDC peaks at V+ + Vf ≈ **13 V** and the current decays through D1 and the circuit resistance in about **0.6 ms**.

So D1 is inexpensive insurance against abrupt interruption. It does not affect normal operation, and it is optional if you only ever ramp by the setpoint.

## Simulated response, V+ = 12 V
- Ramp-up to 3 A with the driver saturated: **≈ 0.14 ms** (headroom is plentiful). The driver's control loop will limit it in practice.
- Ramp-down: with D1, about 0.6 ms. This is independent of V+. Higher V+ speeds up ramp-up only, and ramp-down speed is set by the clamp voltage (a series zener on D1 would speed it up).

| V+ | Ramp-up to 3 A | Driver dissipation at 3 A |
|---|---|---|
| 6 V | 0.52 ms | 9.1 W |
| 8 V | 0.26 ms | 15.1 W |
| 10 V | 0.18 ms | 21.1 W |
| 12 V | 0.14 ms | 27.1 W |

## Open items
- Verify the thermal limit with the SOA calculator for your actual heatsink and airflow; add a fan (5.5 CFM, 35 W) or lower V+ to 11 V. Operating range is 0 to 40 °C ambient.
- Confirm L and the total R with an LCR meter (the earlier whole-circuit reading was about 2 Ω).
- Decide whether to fit D1 and a series zener.
- Check LDC with a scope at the first power-up for oscillation.
