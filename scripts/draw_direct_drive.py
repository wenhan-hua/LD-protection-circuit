"""Schematics: LD5CHA driving the MOT coil directly.
  docs/direct_drive.png/.svg          original configuration (no external protection)
  docs/direct_drive_with_D1.png/.svg  same plus optional freewheel diode D1
Run: .venv/bin/python scripts/draw_direct_drive.py
"""
import schemdraw
import schemdraw.elements as elm


def draw(with_d1: bool, name: str):
    with schemdraw.Drawing(show=False) as d:
        d.config(unit=3, fontsize=11)
        d += elm.Dot().label('V+ = 12 V\nsupply', loc='top')
        d += elm.Line().right(2)
        d += elm.Dot().label('LDA\n(= V+)', loc='top')
        d += elm.Inductor2(loops=4).right(3.5).label('Coil L ≈ 0.38 mH\n(R ≈ 0.19 Ω)', loc='top')
        d += elm.Resistor().right(3).label('cables ≈ 0.8 Ω', loc='top')
        d += (ldc := elm.Dot().label('LDC', loc='top'))
        d += elm.Line().down(1.2)
        d += elm.Rect(w=2.6, h=1.6).label('LD5CHA\ncurrent sink\n(max 5 A)')
        d += elm.Line().down(1.2)
        d += elm.Ground().label('GND', loc='bottom')
        if with_d1:
            d += elm.Line().at(ldc.start).right(1.2).dot()
            d += elm.Line().up(2.2)
            d += elm.Diode().left(7.6).label('D1  1N5408 (anode at LDC, cathode at LDA)', loc='top')
            d += elm.Line().left(1.0)
            d += elm.Line().down(2.2)
    d.save(f'docs/{name}.png', dpi=200)
    d.save(f'docs/{name}.svg')


draw(False, 'direct_drive')
draw(True, 'direct_drive_with_D1')
print('saved')
