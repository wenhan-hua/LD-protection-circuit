"""Ramp-down 2.5 A -> 0 via MOD INPUT, original config (no D1), V+ = 12 V.

Two setpoint shapes, driver assumed to track (rise/fall ~0.8 us):
  linear      i = I0 (1 - t/T)       LDC = V+ - i R + L I0 / T          peak at END of ramp
  exponential i = I0 exp(-t/tau)     LDC = V+ - i (R - L/tau)           peak at START (none if tau >= L/R)
Heat: P_drv = LDC * i.
Run: .venv/bin/python scripts/ramp_down_analysis.py -> docs/ramp_down.png, docs/ramp_down_table.md
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

L, R, VP, I0 = 0.38e-3, 0.99, 12.0, 2.5
P_NOAIR, P_AIR = 25.0, 35.0
P_SS = (VP - I0 * R) * I0
TAU_CRIT = L / R

# ---- analytic metrics --------------------------------------------------
def lin(T):
    a = L * I0 / T
    t = np.linspace(0, T, 4001); i = I0 * (1 - t / T); p = (VP - i * R + a) * i
    return dict(t10=0.9 * T, t1=0.99 * T, ldc=VP + a, p_peak=p.max())

def exp_(tau):
    k = R - L / tau                       # LDC = V+ - i k
    t = np.linspace(0, 12 * tau, 6001); i = I0 * np.exp(-t / tau); p = (VP - i * k) * i
    return dict(t10=tau * np.log(10), t1=tau * np.log(100), ldc=VP + max(0.0, -k * I0), p_peak=p.max())

# ---- tables --------------------------------------------------------------
fmt = lambda x: f"{x*1e3:.2f}".rstrip("0").rstrip(".")
tab = ("**Linear ramp**\n\n| Ramp time T | Peak LDC | Driver peak P | Time to 10 % | Verdict |\n|---|---|---|---|---|\n")
for T in np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]) * 1e-3:
    m = lin(T)
    v = ("avalanche risk (above 30 V)" if m["ldc"] > 30 else "high, unverified" if m["ldc"] > 17 else
         "moderate" if m["ldc"] > 14 else "benign")
    tab += f"| {fmt(T)} ms | {m['ldc']:.1f} V | {m['p_peak']:.0f} W | {fmt(m['t10'])} ms | {v} |\n"
tab += "\n**Exponential (RC) ramp**\n\n| τ | Peak LDC | Driver peak P | Time to 10 % | Time to 1 % | Verdict |\n|---|---|---|---|---|---|\n"
for tau in np.array([0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 2.0]) * 1e-3:
    m = exp_(tau)
    v = ("avalanche risk (above 30 V)" if m["ldc"] > 30 else "high, unverified" if m["ldc"] > 17 else
         "moderate" if m["ldc"] > 14 else "benign, no overshoot above V+" if m["ldc"] <= VP + 1e-9 else "benign")
    tab += (f"| {fmt(tau)} ms | {m['ldc']:.1f} V | {m['p_peak']:.0f} W | {fmt(m['t10'])} ms | {fmt(m['t1'])} ms | {v} |\n")
tab += (f"\nSteady 2.5 A dissipation {P_SS:.1f} W. The exponential has no overshoot above V+ when τ ≥ L/R = {TAU_CRIT*1e3:.2f} ms. "
        f"Stored coil energy ½·L·I0² = {0.5*L*I0**2*1e3:.2f} mJ.\n")
open("docs/ramp_down_table.md", "w").write(tab)
print(tab)

# ---- figure --------------------------------------------------------------
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C_LIN, C_EXP = "#2a78d6", "#eb6834"      # categorical slots 1, 2 (validated)
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})

def plain_log_x(ax):
    ax.set_xscale("log"); ax.set_xlim(0.04, 12)
    ax.xaxis.set_major_locator(FixedLocator([0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); ax.xaxis.set_minor_formatter(NullFormatter())

def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

def refline(ax, y, txt, x=0.985):
    ax.axhline(y, color=INK2, lw=0.9, ls=(0, (4, 3)))
    ax.text(x, y, txt, transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=8.5, color=INK2)

Ts = np.logspace(np.log10(0.05e-3), np.log10(10e-3), 120)
Tau = np.logspace(np.log10(0.02e-3), np.log10(4.3e-3), 120)
ml = [lin(T) for T in Ts]; me = [exp_(t) for t in Tau]
xl_ = [m["t10"] * 1e3 for m in ml]; xe_ = [m["t10"] * 1e3 for m in me]
XL = "time for the current to fall to 10 % [ms]"

fig, ax = plt.subplots(2, 2, figsize=(12, 8))
# (a) peak LDC
a = ax[0, 0]
a.plot(xl_, [m["ldc"] for m in ml], C_LIN, lw=2, label="linear ramp")
a.plot(xe_, [m["ldc"] for m in me], C_EXP, lw=2, label="exponential (RC)")
plain_log_x(a); a.set_ylim(10, 34)
refline(a, 30, "30 V max supply"); refline(a, 28, "28 V max compliance"); refline(a, 12, "V+ = 12 V (idle level)")
style(a, "Peak LDC voltage", XL, "peak LDC [V]"); a.legend(frameon=False, loc="center right", bbox_to_anchor=(1, 0.5))
# (b) peak driver power
b = ax[0, 1]
b.plot(xl_, [m["p_peak"] for m in ml], C_LIN, lw=2, label="linear ramp")
b.plot(xe_, [m["p_peak"] for m in me], C_EXP, lw=2, label="exponential (RC)")
plain_log_x(b); b.set_ylim(15, 80)
refline(b, P_AIR, "35 W limit with airflow"); refline(b, P_NOAIR, "25 W limit, no airflow")
style(b, "Peak driver heat (first instant of the ramp)", XL, "driver power [W]"); b.legend(frameon=False, loc="upper right")
# (c),(d) waveforms: linear 1 ms vs RC 0.4 ms (similar speed)
T0, tau0 = 1e-3, 0.4e-3
t = np.linspace(0, 3e-3, 1500)
i_l = np.where(t < T0, I0 * (1 - t / T0), 0.0); i_e = I0 * np.exp(-t / tau0)
ldc_l = np.where(t < T0, VP - i_l * R + L * I0 / T0, VP)
ldc_e = VP - i_e * (R - L / tau0)
c = ax[1, 0]
c.plot(t * 1e3, i_l, C_LIN, lw=2, label="linear, T = 1 ms"); c.plot(t * 1e3, i_e, C_EXP, lw=2, label="exponential, τ = 0.4 ms")
style(c, "Coil current after the setpoint starts to fall", "time [ms]", "current [A]"); c.legend(frameon=False)
d = ax[1, 1]
d.plot(t * 1e3, ldc_l, C_LIN, lw=2, label="linear, T = 1 ms"); d.plot(t * 1e3, ldc_e, C_EXP, lw=2, label="exponential, τ = 0.4 ms")
d.set_ylim(9, 14); refline(d, VP, "V+ = 12 V", x=0.985)
style(d, "LDC voltage over the same ramps", "time [ms]", "LDC [V]"); d.legend(frameon=False, loc="lower right")
fig.suptitle("Ramp-down 2.5 A → 0 through MOD INPUT, no D1, V+ = 12 V, L = 0.38 mH, R = 0.99 Ω", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96)); fig.savefig("docs/ramp_down.png", dpi=150)
