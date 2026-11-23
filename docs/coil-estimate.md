# MOT coil inductance and resistance estimate

Script: [scripts/coil_estimate.py](../scripts/coil_estimate.py) · raw output: [coil_estimate_output.txt](coil_estimate_output.txt)

## Inputs

| Parameter | Value |
|---|---|
| Inner / outer diameter | 30 mm / 60 mm |
| Height (axial) | 15 mm |
| Turns N | 100 |
| Wire | 16 AWG, bare Ø 1.291 mm (A = 1.309 mm²), ≈ Ø 1.35 mm with enamel |
| Copper resistivity | 1.724e-8 Ω·m at 20 °C, α = 0.00393 /K |

## Geometry

- Radial build c = (60 − 30)/2 = **15 mm**; mean radius a = (15 + 30)/2 = **22.5 mm**; height b = **15 mm**.
- Winding window = 15 × 15 = 225 mm². Copper = 100 × 1.309 = 131 mm². Fill = 58 %, which is realistic for a hand-wound coil.
- Fit check: at 1.35 mm pitch, 11 × 11 = 121 turns fit, so 100 turns fit in the window.

## Resistance

- Mean turn length = 2πa = 2π × 22.5 mm = 141.4 mm
- Wire length ℓ = 100 × 0.1414 m = **14.14 m**
- R = ρℓ/A = 1.724e-8 × 14.14 / 1.309e-6 = **0.186 Ω at 20 °C**
- Cross-check with the AWG table (13.17 mΩ/m): 13.17 mΩ/m × 14.14 m = 186 mΩ.
- Hot: 0.201 Ω at 40 °C, 0.215 Ω at 60 °C, 0.230 Ω at 80 °C.
- Copper mass is about 166 g.

## Inductance

**Method 1: Wheeler's multilayer air-core formula** (lengths in inches, result in µH):

L = 0.8·a²·N² / (6a + 9b + 10c)

With a = 0.886 in, b = c = 0.591 in:

L = 0.8 × 0.785 × 10⁴ / (5.32 + 5.32 + 5.91) = **380 µH**

**Method 2: filament sum.** The 100 turns are placed on a 10 × 10 grid (radial × axial). Each turn is a circular filament.
- Self-inductance of a turn: L_s = µ0·r·(ln(8r/r_w) − 2 + ¼), with r_w the wire radius.
- Mutual inductance between turns uses Maxwell's formula with elliptic integrals.
- L = Σ L_s + Σ_{i≠j} M_ij.

| Layout | L | Wire length | R (20 °C) |
|---|---|---|---|
| Tight pack, 1.35 mm pitch | 388 µH | 13.67 m | 180 mΩ |
| Fill the window, 1.5 mm pitch | 383 µH | 14.14 m | 186 mΩ |

The two methods agree within about 2 %.

> **Confirmed:** L = 0.38 mH and a total circuit R = 0.99 Ω (0.19 Ω coil + ~0.8 Ω cables) have since been confirmed on the hardware, matching the estimate below.

## Result (single coil)

| Quantity | Estimate |
|---|---|
| **L** | **≈ 0.38 mH** (±10 % allowing for winding looseness) |
| **R** | **≈ 0.19 Ω** at 20 °C, ≈ 0.23 Ω hot |
| τ = L/R | ≈ 2.1 ms |
| At 3 A | 0.56 V, 1.7 W, 1.7 mJ, 300 A·turns |
| At 5 A | 0.93 V, 4.7 W, 4.8 mJ, 500 A·turns |
| Voltage to ramp 3 A → 0 in 1 ms | L·di/dt ≈ **1.15 V** |

## Consequences for the driver design

The earlier design in the chat history assumed **L = 30 mH and R = 2 Ω**. This coil is about **80× lower in inductance and 10× lower in resistance**. L scales as N², so 30 mH would take about 885 turns of this geometry.

- The ~100 V clamp, the series MOSFET and the Si8751 gate driver are probably not needed for a 1 ms ramp-down. Ramping down 3 A in 1 ms needs only about 1–2 V across the coil.
- A simple freewheeling diode plus a small clamp would probably be enough.
- The stored energy is tiny (a few mJ), but the kick still matters if the current is interrupted abruptly. This needs to be re-evaluated in the simulation.
- The LD5CHA headroom is also much easier: 3 A × 0.19 Ω is only about 0.6 V, so a low supply voltage keeps driver dissipation small.
- A MOT normally uses an anti-Helmholtz pair. Wired in series, the pair has about 2× L and 2× R (0.76 mH and 0.37 Ω, plus a mutual-inductance correction that depends on the separation).

## Caveats

- The geometry is idealised. Real hand-wound coils, spacers or a coil former change L by a few percent to 10 %.
- The estimate ignores the leads and the nearby metal (eddy currents), which lower the effective L at fast ramps.
- Measure L and R with an LCR meter once the coil is wound.
