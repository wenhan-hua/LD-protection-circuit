"""Simulate the fastest SAFE ramp-down for the two candidate designs.

  A: D1 + 1.5KE10A,            no series resistor, V+ = 8 V,  R = 0.99 ohm
  B: D1 + 1.5KE10A + 2 ohm Rs,                     V+ = 12 V, R = 2.99 ohm

"Safe" = the driver stays in regulation for the whole ramp, so the clamp never
conducts and I MON keeps reading the true coil current.  That caps the inductive
overshoot at the TVS standoff:  dV = Vwm + Vf(leakage) = 8.55 + 0.4 = 8.95 V.

Commanded linear ramp, duration T = L*I0/dV (peak LDC occurs at the end, i -> 0):
    i(t)   = I0 (1 - t/T)
    LDC(t) = V+ - i R + L I0 / T      ->  V+ at t > T
    P_drv  = LDC * i
For contrast the script also runs the clamp-assisted case (setpoint stepped to 0).
Run: .venv/bin/python scripts/sim_fastest_safe_ramp.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L, I0, FRAC = 0.38e-3, 2.5, 0.10
VWM, VBR, VF = 8.55, 10.0, 0.95        # 1.5KE10A standoff / breakdown, D1 drop at 2.5 A
DV = VWM + 0.4                          # usable inductive overshoot, clamp stays off
T = L * I0 / DV                         # commanded linear ramp duration
VCLAMP = VBR + VF                       # clamp voltage once it does fire

designs = [("A  D1 + TVS", 8.0, 0.99, 0.0, "#2a78d6"),
           ("B  2 Ω + D1 + TVS", 12.0, 2.99, 2.0, "#eb6834")]

print(f"usable overshoot dV = {DV:.2f} V   commanded ramp T = {T*1e6:.0f} us   "
      f"t to 10% = {(1-FRAC)*T*1e6:.0f} us   (same for both designs)\n")
hdr = f"{'design':20s}{'LDC steady':>11s}{'margin':>9s}{'driver P':>10s}{'Rs P':>7s}"
hdr += f"{'peak LDC':>10s}{'clamp at':>10s}{'peak P':>9s}{'avg P':>8s}{'ramp-up':>10s}{'clamp-assisted':>16s}"
print(hdr)
for nm, VP, R, RS, _ in designs:
    ldc_ss = VP - I0 * R
    p_pk = (ldc_ss + DV) * I0
    p_avg = (VP + DV) * I0 / 2 - R * I0**2 / 3
    i_f = (VP - 2.0) / R
    t_up = (L / R) * np.log(i_f / (i_f - I0))
    t_ca = (L / R) * np.log((I0 * R + VCLAMP) / (FRAC * I0 * R + VCLAMP))
    print(f"{nm:20s}{ldc_ss:9.2f} V{ldc_ss-2:7.2f} V{ldc_ss*I0:8.1f} W{I0**2*RS:5.1f} W"
          f"{VP+DV:8.1f} V{VP+VCLAMP:8.1f} V{p_pk:7.0f} W{p_avg:6.0f} W{t_up*1e6:7.0f} us"
          f"{t_ca*1e6:13.0f} us")

# ----------------------------------------------------------------- figure
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C_CA = "#1baf7a"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})

def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

t = np.linspace(-25e-6, 200e-6, 3000)
pre = t < 0
ramp = (t >= 0) & (t <= T)

def safe_current(tt):
    return np.where(tt < 0, I0, np.where(tt <= T, I0 * (1 - np.clip(tt, 0, T) / T), 0.0))

def clamp_current(tt, R):
    k = VCLAMP / R
    i = (I0 + k) * np.exp(-np.clip(tt, 0, None) / (L / R)) - k
    return np.where(tt < 0, I0, np.clip(i, 0, None))

fig, ax = plt.subplots(2, 2, figsize=(13.5, 8.6))

# (a) coil current
a = ax[0, 0]
a.plot(t * 1e6, safe_current(t), color=INK, lw=2.4, label="commanded safe ramp (both designs)")
for nm, VP, R, RS, c in designs:
    a.plot(t * 1e6, clamp_current(t, R), color=c, lw=1.8, ls=(0, (5, 3)),
           label=f"clamp-assisted, {nm.split('  ')[0]}")
a.axhline(FRAC * I0, color=INK2, lw=0.9, ls=(0, (1, 2)))
a.text(198, 0.33, "10 % of 2.5 A", ha="right", fontsize=8.5, color=INK2)
a.set_ylim(-0.1, 2.9)
style(a, "Coil current", "time [µs]", "current [A]")
a.legend(frameon=False, fontsize=8.5, loc="upper right")
a.annotate(f"{(1-FRAC)*T*1e6:.0f} µs", (((1 - FRAC) * T) * 1e6, FRAC * I0),
           textcoords="offset points", xytext=(6, 12), fontsize=9, color=INK, fontweight="bold")

# (b) LDC
b = ax[0, 1]
for nm, VP, R, RS, c in designs:
    i = safe_current(t)
    ldc = np.where(t < 0, VP - I0 * R, np.where(t <= T, VP - i * R + DV, VP))
    b.plot(t * 1e6, ldc, color=c, lw=2.2, label=f"{nm}, V+ = {VP:.0f} V")
    b.axhline(VP + VCLAMP, color=c, lw=0.9, ls=(0, (1, 2)))
    b.text(198, VP + VCLAMP + 0.4, f"clamp fires {VP+VCLAMP:.1f} V", ha="right",
           fontsize=8.5, color=c)
b.set_ylim(0, 27)
style(b, "LDC — what you would scope (differential probe)", "time [µs]", "LDC [V]")
b.legend(frameon=False, fontsize=8.5, loc="lower right")

# (c) driver dissipation
c_ = ax[1, 0]
for nm, VP, R, RS, c in designs:
    i = safe_current(t)
    ldc = np.where(t < 0, VP - I0 * R, np.where(t <= T, VP - i * R + DV, VP))
    c_.plot(t * 1e6, ldc * i, color=c, lw=2.2, label=nm)
for y, lab in ((25, "25 W no-airflow limit"), (35, "35 W with airflow")):
    c_.axhline(y, color=INK2, lw=0.9, ls=(0, (4, 3)))
    c_.text(198, y + 0.7, lab, ha="right", fontsize=8.5, color=INK2)
c_.set_ylim(0, 42)
style(c_, "Driver dissipation (brief overshoot, ~100 µs)", "time [µs]", "power [W]")
c_.legend(frameon=False, fontsize=8.5, loc="center right")

# (d) I MON
d = ax[1, 1]
d.plot(t * 1e6, safe_current(t), color=INK, lw=2.4,
       label="safe ramp: I MON = true coil current")
d.plot(t * 1e6, clamp_current(t, 0.99), color=C_CA, lw=2,
       label="clamp-assisted: true coil current")
d.plot(t * 1e6, np.where(t < 0, I0, 0.0), color=C_CA, lw=2, ls=(0, (5, 3)),
       label="clamp-assisted: what I MON reports")
d.set_ylim(-0.1, 2.9)
style(d, "What I MON reports (scaled back to amps; the pin is 2 A/V)",
      "time [µs]", "current [A]")
d.legend(frameon=False, fontsize=8.5, loc="upper right")
d.annotate("I MON collapses to 0 at t = 0,\nyet the coil conducts until ~78 µs",
           xy=(55, 0.03), xytext=(112, 0.95), textcoords="data", fontsize=9, color=C_CA,
           arrowprops=dict(arrowstyle="->", color=C_CA, lw=1.2,
                           connectionstyle="arc3,rad=0.2"))

fig.suptitle("Fastest safe ramp-down, 2.5 A → 0 — driver stays in regulation, I MON stays valid "
             "(L = 0.38 mH, 1.5KE10A clamp)", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig("docs/fastest_safe_ramp.png", dpi=150)
print("\nsaved figure")
