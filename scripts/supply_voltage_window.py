"""Method A (D1 + 1.5KE10A, no series resistor): what changes as V+ varies.

L = 0.38 mH, R = 0.99 ohm, I0 = 2.5 A.
  LDC steady   = V+ - I0 R                      (must stay >= 2 V, the compliance floor)
  driver P     = LDC_steady * I0                (<= 25 W no airflow, 35 W with)
  ramp-up      = (L/R) ln(i_f/(i_f - I0)),  i_f = (V+ - 2)/R
  ramp-down    = (1-FRAC) * L I0 / dV           -- set by the TVS, NOT by V+
  LDC ramp pk  = V+ + dV
  clamp fires  = V+ + Vbr + Vf
Run: .venv/bin/python scripts/supply_voltage_window.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L, R, I0, FRAC = 0.38e-3, 0.99, 2.5, 0.10
VWM, VBR, VF = 8.55, 10.0, 0.95
DV = VWM + 0.4
T_DOWN = (1 - FRAC) * L * I0 / DV
V_FLOOR = 2.0 + I0 * R                 # bare minimum V+ to hold 2.5 A at all
V_25W = 25.0 / I0 + I0 * R             # V+ at which the driver hits 25 W
V_35W = 35.0 / I0 + I0 * R

print(f"ramp-down is {T_DOWN*1e6:.0f} us at EVERY V+ (set by the 1.5KE10A standoff, not the rail)")
print(f"hard compliance floor V+ >= {V_FLOOR:.2f} V | 25 W at V+ = {V_25W:.2f} V | 35 W at V+ = {V_35W:.2f} V\n")
print(f"{'V+':>5s}{'LDC steady':>12s}{'margin':>9s}{'driver P':>10s}{'% 25W':>7s}"
      f"{'ramp-up':>10s}{'ramp-dn':>9s}{'LDC pk':>9s}{'clamp':>8s}{'verdict':>26s}")
for vp in (5, 6, 7, 8, 9, 10, 12, 14, 16):
    ldc = vp - I0 * R
    p = ldc * I0
    i_f = (vp - 2.0) / R
    t_up = (L / R) * np.log(i_f / (i_f - I0)) if i_f > I0 else np.nan
    if ldc < 2: v = "cannot reach 2.5 A"
    elif ldc < 3: v = "no compliance margin"
    elif p > 35: v = "over 35 W even with air"
    elif p > 25: v = "needs forced airflow"
    elif vp + VBR + VF > 28: v = "clamp above 28 V"
    else: v = "ok"
    print(f"{vp:4d} V{ldc:10.2f} V{ldc-2:7.2f} V{p:8.1f} W{p/25*100:6.0f}%"
          f"{t_up*1e6:8.0f} us{T_DOWN*1e6:7.0f} us{vp+DV:7.1f} V{vp+VBR+VF:6.1f} V{v:>26s}")

# ---------------------------------------------------------------- figure
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})

def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

def window(ax):
    ax.axvspan(4.5, 6.0, color=C2, alpha=0.08, lw=0)
    ax.axvspan(12.5, 17, color=C2, alpha=0.08, lw=0)
    ax.axvline(8, color=INK2, lw=1.0, ls=(0, (4, 3)))

vp = np.linspace(4.6, 17, 500)
ldc = vp - I0 * R
p = ldc * I0
i_f = (vp - 2.0) / R
t_up = np.where(i_f > I0, (L / R) * np.log(np.maximum(i_f, I0 + 1e-9) / np.maximum(i_f - I0, 1e-9)), np.nan)

fig, ax = plt.subplots(1, 3, figsize=(15.5, 5.2))

a = ax[0]
window(a)
a.plot(vp, p, color=C1, lw=2.4)
for y, lab in ((25, "25 W, no airflow"), (35, "35 W, with airflow")):
    a.axhline(y, color=INK2, lw=0.9, ls=(0, (4, 3)))
    a.text(4.8, y + 0.8, lab, ha="left", fontsize=8.5, color=INK2)
a.plot(8, (8 - I0 * R) * I0, "o", ms=9, color=C1, mec=BG, mew=2, zorder=5)
a.annotate("V+ = 8 V\n13.8 W", (8, 13.8), textcoords="offset points", xytext=(10, -6),
           fontsize=9, color=C1, fontweight="bold")
a.set_xlim(4.6, 17); a.set_ylim(0, 40)
style(a, "Driver dissipation — the upper bound", "V+ [V]", "driver power [W]")

b = ax[1]
window(b)
b.plot(vp, vp + VBR + VF, color=C3, lw=2.2, label="clamp fires here (faults)")
b.plot(vp, vp + DV, color=C2, lw=2.2, label="peak LDC during the ramp")
b.plot(vp, ldc, color=C1, lw=2.4, label="LDC steady at 2.5 A")
b.axhline(2, color=INK2, lw=1.1, ls=(0, (4, 3)))
b.text(4.8, 2.6, "2 V compliance floor", fontsize=8.5, color=INK2)
b.axhline(28, color=INK2, lw=1.1, ls=(0, (4, 3)))
b.text(4.8, 28.6, "28 V max compliance", ha="left", fontsize=8.5, color=INK2)
b.set_xlim(4.6, 17); b.set_ylim(0, 33)
style(b, "LDC voltages — both bounds at once", "V+ [V]", "LDC [V]")
b.legend(frameon=False, fontsize=8.5, loc="lower right", bbox_to_anchor=(1.0, 0.11))

c = ax[2]
window(c)
c.plot(vp, t_up * 1e6, color=C1, lw=2.4, label="ramp-up 0 → 2.5 A")
c.axhline(T_DOWN * 1e6, color=C2, lw=2.4)
c.text(9.1, 118, f"ramp-down {T_DOWN*1e6:.0f} µs — flat,\nV+ does not affect it",
       ha="left", fontsize=9, color=C2, fontweight="bold", linespacing=1.4)
c.plot(8, 204, "o", ms=9, color=C1, mec=BG, mew=2, zorder=5)
c.annotate("204 µs", (8, 204), textcoords="offset points", xytext=(10, 8),
           fontsize=9, color=C1, fontweight="bold")
c.set_xlim(4.6, 17); c.set_ylim(0, 800)
style(c, "Ramp times", "V+ [V]", "time [µs]")
c.legend(frameon=False, fontsize=8.5, loc="upper right")

fig.suptitle("Method A (D1 + 1.5KE10A): choosing V+ — usable window 6–12.5 V, recommended 8 V "
             "(L = 0.38 mH, R = 0.99 Ω, 2.5 A)", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig("figures/supply-voltage-window.png", dpi=150)
print("\nsaved figure")
