"""Estimate inductance and resistance of a single MOT coil.

Geometry (inputs): ID 30 mm, OD 60 mm, height 15 mm, N = 100 turns, 16 AWG.
Run:  .venv/bin/python scripts/coil_estimate.py
"""
import math
import numpy as np
from scipy.special import ellipk, ellipe

MU0 = 4e-7 * math.pi

# ---------------- inputs ----------------
ID, OD, H, N = 30e-3, 60e-3, 15e-3, 100
D_BARE = 1.291e-3          # 16 AWG bare copper diameter (AWG formula: 0.127*92^((36-16)/39) mm)
D_INS = 1.35e-3            # approx. diameter incl. enamel (heavy build ~ +0.06 mm)
RHO20 = 1.724e-8           # copper resistivity at 20 C [ohm m]
ALPHA = 0.00393            # copper temp. coefficient [1/K]

# ---------------- geometry ----------------
a_in, a_out = ID / 2, OD / 2
c = a_out - a_in                    # radial build
a_mean = (a_in + a_out) / 2         # mean radius
print(f"radial build c = {c*1e3:.1f} mm, height b = {H*1e3:.1f} mm, mean radius a = {a_mean*1e3:.1f} mm")
print(f"winding window area = {c*H*1e6:.0f} mm^2; copper area = {N*math.pi*D_BARE**2/4*1e6:.0f} mm^2; "
      f"fill = {N*math.pi*D_BARE**2/4/(c*H)*100:.0f} %")
print(f"turns that fit at {D_INS*1e3:.2f} mm pitch: {int(c//D_INS)} radial x {int(H//D_INS)} axial = "
      f"{int(c//D_INS)*int(H//D_INS)} (need {N})")

# ---------------- resistance ----------------
A_cu = math.pi * D_BARE**2 / 4
length = N * 2 * math.pi * a_mean
R20 = RHO20 * length / A_cu
print(f"\nwire length = {length:.2f} m, area = {A_cu*1e6:.3f} mm^2")
print(f"R(20C) = {R20*1e3:.0f} mOhm  (check: 13.17 mOhm/m x {length:.2f} m = {13.17e-3*length*1e3:.0f} mOhm)")
for T in (40, 60, 80):
    print(f"R({T}C) = {R20*(1+ALPHA*(T-20))*1e3:.0f} mOhm")
print(f"mass of copper = {length*A_cu*8960*1e3:.0f} g")

# ---------------- inductance 1: Wheeler multilayer formula ----------------
# L[uH] = 0.8 a^2 N^2 / (6a + 9b + 10c), lengths in inches
inch = 0.0254
ai, bi, ci = a_mean / inch, H / inch, c / inch
L_wheeler = 0.8 * ai**2 * N**2 / (6 * ai + 9 * bi + 10 * ci) * 1e-6
print(f"\nWheeler: L = {L_wheeler*1e6:.0f} uH")

# ---------------- inductance 2: filament (Maxwell) sum ----------------
def mutual(r1, r2, dz):
    k2 = 4 * r1 * r2 / ((r1 + r2) ** 2 + dz**2)
    k = math.sqrt(k2)
    return MU0 * math.sqrt(r1 * r2) * ((2 / k - k) * ellipk(k2) - 2 / k * ellipe(k2))

def filament_L(nr, nz, pitch_r, pitch_z, r0):
    """Turns on an nr x nz grid, first turn centre radius r0. Return L [H] and list of turns."""
    turns = [(r0 + i * pitch_r, j * pitch_z) for i in range(nr) for j in range(nz)]
    turns = turns[:N]
    rw = D_BARE / 2
    L = 0.0
    for i, (r1, z1) in enumerate(turns):
        L += MU0 * r1 * (math.log(8 * r1 / rw) - 2 + 0.25)       # self (uniform current, GMD of round wire)
        for j, (r2, z2) in enumerate(turns):
            if i != j:
                L += mutual(r1, r2, z1 - z2)
    return L, turns

cases = {
    "tight pack 10x10 @1.35 mm": (10, 10, D_INS, D_INS),
    "fill window 10x10 @1.5 mm ": (10, 10, c / 10, H / 10),
}
print()
res = {}
for name, (nr, nz, pr, pz) in cases.items():
    r0 = a_in + pr / 2
    L, turns = filament_L(nr, nz, pr, pz, r0)
    lt = sum(2 * math.pi * r for r, _ in turns)
    res[name] = (L, lt)
    print(f"Filament sum, {name}: L = {L*1e6:.0f} uH, wire length = {lt:.2f} m, R20 = {RHO20*lt/A_cu*1e3:.0f} mOhm")

# ---------------- consequences ----------------
L = res["fill window 10x10 @1.5 mm "][0]
R = R20
print("\n--- consequences (single coil) ---")
print(f"tau = L/R = {L/R*1e3:.2f} ms")
for I in (3, 5):
    print(f"I = {I} A: V_R = {I*R:.2f} V, P = {I*I*R:.2f} W, E = {0.5*L*I*I*1e3:.2f} mJ, "
          f"ampere-turns = {N*I}")
print(f"voltage to ramp 3 A -> 0 in 1 ms: L*di/dt = {L*3/1e-3:.2f} V")
print(f"turns needed for 30 mH (L ~ N^2): N = {N*math.sqrt(30e-3/L):.0f}")
