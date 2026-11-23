"""Fastest SAFE ramp-down, simulated separately for each candidate design.

  A: D1 + 1.5KE10A,             no series resistor, V+ = 12 V, R = 0.99 ohm
  B: D1 + 1.5KE10A + 2 ohm Rs,                      V+ = 12 V, R = 2.99 ohm

"Safe" = driver stays in regulation for the whole ramp, so the clamp never conducts
and I MON keeps reading the true coil current. That caps the inductive overshoot at
the TVS standoff: dV = Vwm + Vf(leakage) = 8.55 + 0.4 = 8.95 V.

Commanded linear ramp, duration T = L*I0/dV (peak LDC is at the end, where i -> 0):
    i(t)   = I0 (1 - t/T)
    LDC(t) = V+ - i R + L I0 / T   ->  V+ once the ramp ends
    P_drv  = LDC * i
Writes figures/ramp-sim-d1-tvs.png and figures/ramp-sim-series-resistor.png.
Run: .venv/bin/python scripts/sim_fastest_safe_ramp.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L, I0, FRAC = 0.38e-3, 2.5, 0.10
VWM, VBR, VF = 8.55, 10.0, 0.95        # 1.5KE10A standoff / breakdown, D1 drop at 2.5 A
DV = VWM + 0.4
T = L * I0 / DV
VCLAMP = VBR + VF

DESIGNS = [
    dict(key="a", fig="d1-tvs", name="A — D1 + TVS (no series resistor)", VP=12.0, R=0.99, RS=0.0, c="#2a78d6"),
    dict(key="b", fig="series-resistor", name="B — series 2 Ω + D1 + TVS", VP=12.0, R=2.99, RS=2.0, c="#eb6834"),
]

BG, INK, INK2, GRID, C_CA = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#1baf7a"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})

def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

t = np.linspace(-25e-6, 200e-6, 4000)

def safe_i(tt):
    return np.where(tt < 0, I0, np.where(tt <= T, I0 * (1 - np.clip(tt, 0, T) / T), 0.0))

def clamp_i(tt, R):
    k = VCLAMP / R
    return np.where(tt < 0, I0, np.clip((I0 + k) * np.exp(-np.clip(tt, 0, None) / (L / R)) - k, 0, None))

print(f"usable overshoot dV = {DV:.2f} V   commanded ramp T = {T*1e6:.0f} us   "
      f"t to 10 % = {(1-FRAC)*T*1e6:.0f} us   (identical for both designs)\n")

for D in DESIGNS:
    VP, R, RS, c = D["VP"], D["R"], D["RS"], D["c"]
    ldc_ss = VP - I0 * R
    i_s = safe_i(t)
    ldc = np.where(t < 0, ldc_ss, np.where(t <= T, VP - i_s * R + DV, VP))
    p = ldc * i_s
    i_c = clamp_i(t, R)
    t_ca = (L / R) * np.log((I0 * R + VCLAMP) / (FRAC * I0 * R + VCLAMP))
    i_f = (VP - 2.0) / R
    t_up = (L / R) * np.log(i_f / (i_f - I0))
    p_avg = (VP + DV) * I0 / 2 - R * I0**2 / 3

    print(f"{D['name']}")
    print(f"  V+ {VP:.0f} V, R {R:.2f} ohm | LDC steady {ldc_ss:.2f} V (margin {ldc_ss-2:.2f} V) | "
          f"driver {ldc_ss*I0:.1f} W, Rs {I0**2*RS:.1f} W")
    print(f"  ramp: LDC steps to {ldc_ss+DV:.1f} V, rises to {VP+DV:.1f} V, falls to {VP:.0f} V | "
          f"clamp fires at {VP+VCLAMP:.1f} V")
    print(f"  driver peak {p.max():.0f} W, avg over ramp {p_avg:.0f} W | ramp-up {t_up*1e6:.0f} us | "
          f"clamp-assisted would be {t_ca*1e6:.0f} us\n")

    fig, ax = plt.subplots(2, 2, figsize=(13, 8.4))
    # (a) current
    a = ax[0, 0]
    a.plot(t * 1e6, i_s, color=c, lw=2.4, label=f"commanded safe ramp, T = {T*1e6:.0f} µs")
    a.plot(t * 1e6, i_c, color=C_CA, lw=1.9, ls=(0, (5, 3)),
           label=f"clamp-assisted instead ({t_ca*1e6:.0f} µs, I MON blind)")
    a.axhline(FRAC * I0, color=INK2, lw=0.9, ls=(0, (1, 2)))
    a.text(198, 0.33, "10 % of 2.5 A", ha="right", fontsize=8.5, color=INK2)
    a.annotate(f"{(1-FRAC)*T*1e6:.0f} µs", ((1 - FRAC) * T * 1e6, FRAC * I0),
               textcoords="offset points", xytext=(8, 14), fontsize=9.5, color=c, fontweight="bold")
    a.set_ylim(-0.1, 2.95)
    style(a, "Coil current", "time [µs]", "current [A]")
    a.legend(frameon=False, fontsize=8.5, loc="upper right")
    # (b) LDC
    b = ax[0, 1]
    b.plot(t * 1e6, ldc, color=c, lw=2.4)
    b.axhline(VP + VCLAMP, color=INK2, lw=1.0, ls=(0, (4, 3)))
    b.text(198, VP + VCLAMP + 0.5, f"clamp fires at {VP+VCLAMP:.1f} V", ha="right", fontsize=9, color=INK2)
    for xx, yy, lab, dxy in ((2, ldc_ss + DV, f"① step to {ldc_ss+DV:.1f} V", (8, -4)),
                             (T * 1e6 * 0.55, VP - I0 * R * 0.45 + DV, "② rises as i·R shrinks", (-6, 10)),
                             (T * 1e6 + 3, VP, f"③ back to V+ = {VP:.0f} V", (8, -16))):
        b.annotate(lab, (xx, yy), textcoords="offset points", xytext=dxy, fontsize=9, color=INK)
    b.set_ylim(0, VP + VCLAMP + 5)
    style(b, "LDC — what you would scope (differential probe)", "time [µs]", "LDC [V]")
    # (c) power
    cc = ax[1, 0]
    cc.plot(t * 1e6, p, color=c, lw=2.4)
    for y, lab in ((25, "25 W no-airflow limit"), (35, "35 W with airflow")):
        cc.axhline(y, color=INK2, lw=0.9, ls=(0, (4, 3)))
        cc.text(198, y + 0.8, lab, ha="right", fontsize=8.5, color=INK2)
    cc.annotate(f"steady state {ldc_ss*I0:.1f} W", (-24, ldc_ss * I0), textcoords="offset points",
                xytext=(2, -15), fontsize=9, color=c, fontweight="bold")
    cc.set_ylim(0, max(43.0, p.max() * 1.22))
    style(cc, f"Driver dissipation (peak {p.max():.0f} W, avg {p_avg:.0f} W over the ramp)",
          "time [µs]", "power [W]")
    # (d) I MON
    d = ax[1, 1]
    d.plot(t * 1e6, i_s, color=c, lw=2.4, label="safe ramp: I MON = true coil current")
    d.plot(t * 1e6, i_c, color=C_CA, lw=2, label="clamp-assisted: true coil current")
    d.plot(t * 1e6, np.where(t < 0, I0, 0.0), color=C_CA, lw=2, ls=(0, (5, 3)),
           label="clamp-assisted: what I MON reports")
    d.annotate("if the clamp fires,\nI MON drops to 0 while\nthe coil still conducts",
               xy=(t_ca * 1e6 * 0.75, 0.03), xytext=(108, 1.15), textcoords="data",
               fontsize=9, color=C_CA, linespacing=1.4,
               arrowprops=dict(arrowstyle="->", color=C_CA, lw=1.2, connectionstyle="arc3,rad=0.25"))
    d.set_ylim(-0.1, 2.95)
    style(d, "What I MON reports (scaled to amps; the pin is 2 A/V)", "time [µs]", "current [A]")
    d.legend(frameon=False, fontsize=8.5, loc="upper right")

    fig.suptitle(f"{D['name']} — fastest safe ramp-down, 2.5 A → 0 at V+ = {VP:.0f} V "
                 f"(L = 0.38 mH, R = {R:.2f} Ω, 1.5KE10A)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(f"figures/ramp-sim-{D['fig']}.png", dpi=150)
print("saved both figures")
