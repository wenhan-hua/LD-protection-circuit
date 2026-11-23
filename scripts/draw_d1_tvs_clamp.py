"""Simplest clamp: D1 + TVS across LDA-LDC, no series resistor.

Draws figures/schematic-d1-tvs-clamp.png/.svg and prints operating point, clamp options, mounting options.
Run: .venv/bin/python scripts/draw_d1_tvs_clamp.py
"""
import numpy as np
import schemdraw
import schemdraw.elements as elm

L, R_COIL, R_CABLE = 0.38e-3, 0.19, 0.80
I0, FRAC, VF = 2.5, 0.10, 0.95
RT = R_COIL + R_CABLE          # 0.99 ohm, clamp mounted at the driver terminals

def t10(Vc, R=RT):
    return (L / R) * np.log((I0 * R + Vc) / (FRAC * I0 * R + Vc))

def t_up(vp, R=RT):
    i_f = (vp - 2.0) / R
    return (L / R) * np.log(i_f / (i_f - I0)) if i_f > I0 else float("nan")

print(f"R_loop = {RT:.2f} ohm   tau = {L/RT*1e6:.0f} us   stored energy = {0.5*L*I0**2*1e3:.2f} mJ\n")
print(f"{'V+':>5s}{'LDC steady':>12s}{'driver P':>10s}{'% of 25 W':>11s}{'ramp-up 0->2.5 A':>19s}")
for vp in (6, 7, 8, 10, 12):
    ldc = vp - I0 * RT
    p = ldc * I0
    print(f"{vp:4d} V{ldc:10.2f} V{p:8.1f} W{p/25*100:9.0f} %{t_up(vp)*1e6:16.0f} us")

print(f"\n{'clamp part':22s}{'V at 2.5 A':>12s}{'peak LDC (V+=12)':>18s}{'t to 10%':>10s}")
for nm, vz in (("none (D1 only)", 0.0), ("1.5KE6.8A", 6.9), ("1.5KE10A", 10.2), ("1.5KE15A", 15.3)):
    vc = vz + VF
    print(f"{nm:22s}{vc:10.1f} V{12 + vc:16.1f} V{t10(vc)*1e6:8.0f} us")

print(f"\nmounting (peak LDC is the same either way; only the loop resistance differs)")
for nm, R in (("at driver terminals (cables in loop)", RT), ("at coil terminals (cables out)", R_COIL)):
    print(f"  {nm:38s} R_loop {R:.2f} ohm -> D1 only {t10(VF, R)*1e6:4.0f} us, "
          f"with 1.5KE6.8A {t10(6.9+VF, R)*1e6:4.0f} us")

# ------------------------------------------------------------------ diagram
with schemdraw.Drawing(show=False) as d:
    d.config(unit=3, fontsize=11)
    d += elm.Dot().label('V+ = 12 V supply', loc='left')
    d += elm.Line().right(1.8)
    d += (lda := elm.Dot().label('LDA (= V+)', loc='bottom'))
    d += elm.Inductor2(loops=4).right(3.6).label('MOT coil\n0.38 mH / 0.19 Ω', loc='top')
    d += elm.Line().right(0.6)
    d += elm.Resistor().right(2.8).label('cables ≈ 0.8 Ω', loc='top')
    d += elm.Line().right(0.6)
    d += (ldc := elm.Dot().label('LDC', loc='top'))

    d += elm.Line().down(1.4)
    d += elm.Rect(w=2.9, h=1.8).label('LD5CHA\ncurrent sink')
    d += elm.Line().down(1.4)
    d += elm.Ground().label('GND', loc='bottom')

    d += elm.Line().at(ldc.start).right(1.3)
    d += elm.Line().up(2.6)
    d += elm.Diode().left(4.2).label('D1  MUR460\nanode at LDC', loc='top')
    d += elm.Zener().left(4.2).reverse().label('TVS  1.5KE6.8A\ncathode to D1', loc='top')
    d += elm.Line().left(2.3)
    d += elm.Line().down(2.6)

    d += elm.Label().at((5.6, 4.3)).label('turn-off path:  LDC → D1 → TVS → LDA', fontsize=10)
    d += elm.Label().at((5.6, -4.4)).label(
        'Two leaded parts in the driver\'s J1 terminal block: D1 across J1:1–J1:2 in series with the TVS.\n'
        'No series resistor — so the driver carries the full 23.8 W at V+ = 12 V. See the supply-voltage table.',
        fontsize=9.5)
    d += elm.Label().at((14.6, 0)).label('9.5 V\nat 2.5 A', fontsize=9.5)

d.save('figures/schematic-d1-tvs-clamp.png', dpi=200)
d.save('figures/schematic-d1-tvs-clamp.svg')
print('\nsaved diagram')
