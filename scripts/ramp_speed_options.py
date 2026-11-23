"""Fastest 2.5 A -> 0 ramp-down for each method, all held to the SAME peak-LDC ceiling.

Confirmed load: L = 0.38 mH, R = 0.99 Ohm.  V+ = 12 V, I0 = 2.5 A.

The coil only sheds current when LDC rises above V+:   L di/dt = V+ - LDC - i R.
So with a ceiling LDC <= Vmax, let dV = Vmax - V+ be the voltage budget.
The fastest possible trajectory holds LDC at the ceiling for the whole ramp,
which is exactly what a constant-voltage clamp does:
    t(i_f) = (L/R) ln((I0 R + dV) / (i_f R + dV))
Any setpoint shape is at best equal to this, never better.
Run: .venv/bin/python scripts/ramp_speed_options.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

L, R, VP, I0, FRAC = 0.38e-3, 0.99, 12.0, 2.5, 0.10


def t_clamp(dV, Lh=L, Rh=R, I=I0):
    """Hold LDC at V+ + dV for the whole ramp -> time to fall to FRAC*I."""
    return (Lh / Rh) * np.log((I * Rh + dV) / (FRAC * I * Rh + dV))


def t_rc(dV):
    """Exponential setpoint. Peak LDC is at t=0 (current largest): dV = I0 (L/tau - R)."""
    tau = L * I0 / (I0 * R + dV)
    return tau * np.log(1 / FRAC)


def t_linear(dV):
    """Linear setpoint. Peak LDC is at the END of the ramp: dV = L I0 / T."""
    return (1 - FRAC) * L * I0 / dV


RS = 2.0                                  # series power resistor
L2, I2, R2 = L / 4, I0 * 2, 0.19 / 2 + 0.80   # half the turns, same ampere-turns
V_FET = 100.0                             # MOSFET route: TVS sets this, LDC never sees it

methods = [
    ("Exponential (RC) setpoint",      lambda d: t_rc(d),                       "#eda100"),
    ("Linear setpoint ramp",           lambda d: t_linear(d),                   "#1baf7a"),
    ("D1 + zener  (= best possible)",  lambda d: t_clamp(d),                    "#2a78d6"),
    ("Series 2 \u03a9 + D1 + zener",      lambda d: t_clamp(d, Rh=R + RS),         "#eb6834"),
    ("Half the turns, 5 A + clamp",    lambda d: t_clamp(d, Lh=L2, Rh=R2, I=I2), "#6250d6"),
    ("Series MOSFET + 100 V TVS",      lambda d: np.full_like(np.asarray(d, float), t_clamp(V_FET)), "#008300"),
]

ceilings = [13, 15, 18, 22, 28]
print(f"L*I0 = {L*I0*1e3:.2f} mV.s   L/R = {L/R*1e3:.3f} ms   I0*R = {I0*R:.2f} V\n")
print(f"{'method':32s}" + "".join(f"{'LDC<=' + str(c) + 'V':>11s}" for c in ceilings))
table = {}
for name, fn, _ in methods:
    vals = [float(fn(np.array([c - VP], float))[0]) if "MOSFET" in name else float(fn(c - VP)) for c in ceilings]
    table[name] = vals
    print(f"{name:32s}" + "".join(f"{v*1e6:9.0f} us" for v in vals))

# ---------------------------------------------------------------- figure
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})

def style(ax, title, xl, yl):
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")
    ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)

def plain(axis, ticks):
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    axis.set_minor_formatter(NullFormatter())

fig, (a, b) = plt.subplots(1, 2, figsize=(13.5, 5.8))

# --- A: fastest ramp vs the LDC ceiling you allow
Vmax = np.linspace(12.4, 30, 400)
lab_at = {"Exponential (RC) setpoint": 24.0, "Linear setpoint ramp": 15.6,
          "D1 + zener  (= best possible)": 20.5, "Series 2 \u03a9 + D1 + zener": 25.0,
          "Half the turns, 5 A + clamp": 18.5, "Series MOSFET + 100 V TVS": 16.5}
lab_dy = {"Exponential (RC) setpoint": 1.30, "Linear setpoint ramp": 1.30,
          "D1 + zener  (= best possible)": 1.30, "Series 2 \u03a9 + D1 + zener": 0.62,
          "Half the turns, 5 A + clamp": 0.60, "Series MOSFET + 100 V TVS": 1.35}
for name, fn, c in methods:
    y = fn(Vmax - VP) * 1e6
    a.semilogy(Vmax, y, color=c, lw=2)
    xl_ = lab_at[name]
    yl_ = float(np.interp(xl_, Vmax, y)) * lab_dy[name]
    a.text(xl_, yl_, name.replace("  (= best possible)", ""), color=c, fontsize=8.5,
           ha="center", fontweight="bold")
a.axvspan(28, 30, color="#eb6834", alpha=0.09, lw=0)
a.text(29.6, 1100, "unverified", rotation=90, va="top", ha="right", fontsize=8.5, color=INK2)
a.set_xlim(12.4, 30); a.set_ylim(5, 1500)
plain(a.yaxis, [5, 10, 30, 100, 300, 1000])
style(a, "Fastest ramp each method can do, for a ceiling you choose",
      "peak LDC voltage you are willing to allow [V]", "time for 2.5 A to fall to 10 % [µs]")
a.text(12.7, 6.2, "V+ = 12 V, so the x axis is really 'volts of headroom above the rail'",
       fontsize=9, color=INK2, style="italic")

# --- B: why the shapes differ, all tuned to the SAME 18 V ceiling
CEIL = 18.0; dV = CEIL - VP
t = np.linspace(0, 420e-6, 1200)
tau_rc = L * I0 / (I0 * R + dV); i_rc = I0 * np.exp(-t / tau_rc)
T_lin = L * I0 / dV; i_lin = np.clip(I0 * (1 - t / T_lin), 0, None)
tau = L / R; i_cl = np.clip((I0 + dV / R) * np.exp(-t / tau) - dV / R, 0, None)
cross = (tau_rc * np.log(1 / FRAC), (1 - FRAC) * T_lin,
         tau * np.log((I0 * R + dV) / (FRAC * I0 * R + dV)))
for i_, c, nm, tc, dx in ((i_rc, "#eda100", "exponential (RC)", cross[0], 0),
                          (i_lin, "#1baf7a", "linear ramp", cross[1], 20),
                          (i_cl, "#2a78d6", "clamp at the ceiling", cross[2], -18)):
    b.plot(t * 1e6, i_, color=c, lw=2, label=nm)
    b.plot(tc * 1e6, FRAC * I0, "o", ms=8, color=c, mec=BG, mew=2, zorder=5)
    b.annotate(f"{tc*1e6:.0f} \u00b5s", (tc * 1e6, FRAC * I0), textcoords="offset points",
               xytext=(dx, -18), ha="center", fontsize=8.5, color=c, fontweight="bold")
b.axhline(0.25, color=INK2, lw=0.9, ls=(0, (1, 2)))
b.text(415, 0.31, "10 % of 2.5 A", ha="right", fontsize=8.5, color=INK2)
b.set_xlim(0, 420); b.set_ylim(0, 2.65)
style(b, "Same 18 V ceiling, three ways of spending it", "time [µs]", "coil current [A]")
b.legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.30), fontsize=9)
b.text(168, 2.52,
       "All three obey LDC ≤ 18 V, but spend it differently:\n"
       "the RC spends its budget at the start (peak at t = 0),\n"
       "the linear ramp saves it for the end,\n"
       "the clamp holds the ceiling throughout — so it wins.",
       fontsize=9, color=INK2, linespacing=1.5, va="top")

fig.suptitle("Ramp-down 2.5 A → 0: every method held to the same peak-LDC ceiling "
             "(L = 0.38 mH, R = 0.99 Ω, V+ = 12 V)", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig("docs/ramp_speed_options.png", dpi=150)
