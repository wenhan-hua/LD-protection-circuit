"""Chosen design: series 2 ohm + D1 + TVS clamp across BOTH, driven by the LD5CHA.

Draws figures/schematic-series-resistor-clamp.png/.svg and prints the operating point and clamp options.
Run: .venv/bin/python scripts/draw_series_resistor_clamp.py
"""
import numpy as np
import schemdraw
import schemdraw.elements as elm

L, R_COIL, R_CABLE, RS = 0.38e-3, 0.19, 0.80, 2.0
VP, I0, FRAC, VF = 12.0, 2.5, 0.10, 0.95
RT = R_COIL + R_CABLE + RS

print(f"R_total = {RT:.2f} ohm   tau = L/R = {L/RT*1e6:.0f} us")
print(f"at {I0} A: load drop = {I0*RT:.2f} V, LDC = {VP - I0*RT:.2f} V "
      f"(compliance floor 2 V -> margin {VP - I0*RT - 2:.2f} V)")
print(f"  driver dissipates {(VP - I0*RT)*I0:.1f} W   (was {(VP - I0*(R_COIL+R_CABLE))*I0:.1f} W without Rs)")
print(f"  Rs dissipates {I0**2*RS:.1f} W, cables {I0**2*R_CABLE:.1f} W, coil {I0**2*R_COIL:.1f} W\n")

def t10(Vc):
    return (L / RT) * np.log((I0 * RT + Vc) / (FRAC * I0 * RT + Vc))

i_final = (VP - 2.0) / RT
t_up = (L / RT) * np.log(i_final / (i_final - I0))
print(f"ramp-up: driver can reach {i_final:.2f} A; 0 -> {I0} A takes {t_up*1e6:.0f} us "
      f"(vs {(L/(R_COIL+R_CABLE))*np.log(((VP-2)/(R_COIL+R_CABLE))/((VP-2)/(R_COIL+R_CABLE)-I0))*1e6:.0f} us without Rs)\n")

print(f"{'clamp part':22s}{'V at 2.5 A':>12s}{'peak LDC':>10s}{'t to 10%':>10s}")
for nm, vz in (("none (D1 only)", 0.0), ("1.5KE6.8A", 6.9), ("1.5KE10A", 10.2),
               ("1.5KE15A", 15.3)):
    vc = vz + VF
    print(f"{nm:22s}{vc:10.1f} V{VP + vc:8.1f} V{t10(vc)*1e6:8.0f} us")

# ------------------------------------------------------------------ diagram
with schemdraw.Drawing(show=False) as d:
    d.config(unit=3, fontsize=11)
    d += elm.Dot().label('V+ = 12 V supply', loc='left')
    d += elm.Line().right(1.8)
    d += (lda := elm.Dot().label('LDA (= V+)', loc='bottom'))
    d += elm.Inductor2(loops=4).right(3.4).label('MOT coil\n0.38 mH / 0.19 \u03a9', loc='top')
    d += elm.Line().right(0.5)
    d += elm.Resistor().right(2.6).label('Rs  2 \u03a9 / 50 W\nnon-inductive', loc='top')
    d += elm.Line().right(0.5)
    d += elm.Resistor().right(2.6).label('cables \u2248 0.8 \u03a9', loc='top')
    d += elm.Line().right(0.6)
    d += (ldc := elm.Dot().label('LDC', loc='top'))

    d += elm.Line().down(1.4)
    d += elm.Rect(w=2.9, h=1.8).label('LD5CHA\ncurrent sink')
    d += elm.Line().down(1.4)
    d += elm.Ground().label('GND', loc='bottom')

    # clamp spans coil AND Rs AND cables: LDC -> D1 -> TVS -> LDA
    d += elm.Line().at(ldc.start).right(1.3)
    d += elm.Line().up(2.6)
    d += elm.Diode().left(4.5).label('D1  MUR460\nanode at LDC', loc='top')
    d += elm.Zener().left(4.5).reverse().label('TVS  1.5KE6.8A\ncathode to D1', loc='top')
    d += elm.Line().left(2.5)
    d += elm.Line().down(2.6)

    d += elm.Label().at((6.3, -4.4)).label(
        'Clamp spans the coil, Rs and the cables \u2014 never the coil alone,\n'
        'or the freewheel current would bypass Rs.', fontsize=10)
    d += elm.Label().at((6.3, 4.3)).label(
        'turn-off path:  LDC \u2192 D1 \u2192 TVS \u2192 LDA', fontsize=10)
    d += elm.Label().at((15.2, 0)).label('4.5 V\nat 2.5 A', fontsize=9.5)

d.save('figures/schematic-series-resistor-clamp.png', dpi=200)
d.save('figures/schematic-series-resistor-clamp.svg')
print('\nsaved diagram')
