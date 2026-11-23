"""Options for speeding up the 2.5 A -> 0 ramp-down, ranked by complexity.

Governing relation: the coil opposes change with L di/dt, so with V volts imposed
across it the current falls in roughly t ~ L*I0/V.  Exactly, with a clamp of
voltage Vc in series with the loop resistance R:
    i(t) = (I0 + Vc/R) exp(-t/tau) - Vc/R,  tau = L/R
    t(i_f) = tau * ln((I0 R + Vc) / (i_f R + Vc))
Run: .venv/bin/python scripts/ramp_speed_options.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

L, R0, VP, I0 = 0.38e-3, 0.99, 12.0, 2.5
VF = 0.95                      # 1N5408 forward drop at ~2.5 A


def t_decay(Vc, R=R0, frac=0.10, I=I0, Lh=L):
    """Time for current to fall from I to frac*I against clamp Vc plus i*R."""
    tau = Lh / R
    return tau * np.log((I * R + Vc) / (frac * I * R + Vc))


def t_linear_ramp(dv):
    """Linear setpoint ramp whose END overshoot above V+ is dv -> ramp time."""
    return L * I0 / dv


# name, parts, volts across coil at start, R in loop, peak LDC, note
opts = [
    ("0  Setpoint RC, tau = 0.4 ms", "none", None, None, 12.0, None),
    ("0b Setpoint linear ramp", "none", None, None, 18.0, None),
    ("1  D1 freewheel diode", "1 diode", VF, R0, VP + VF, None),
    ("2  D1 + 6 V zener", "2 leaded parts", VF + 5.1, R0, VP + VF + 5.1, None),
    ("3  D1 + 15 V TVS", "2 leaded parts", VF + 15.0, R0, VP + VF + 15.0, None),
    ("4  Series 2 ohm + D1", "resistor + diode", VF, R0 + 2.0, VP + VF, None),
    ("5  Half the turns, 5 A", "rewind coil", VF + 15.0, None, VP + VF + 15.0, None),
    ("6  Series MOSFET + 100 V TVS", "FET + gate driver", 100.0, R0, VP, None),
    ("7  Series MOSFET + 250 V TVS", "FET + gate driver", 250.0, R0, VP, None),
]

print(f"L*I0 = {L*I0*1e3:.2f} mV.s   tau = L/R = {L/R0*1e3:.3f} ms   I0*R = {I0*R0:.2f} V\n")
print(f"{'option':34s} {'V across coil':>14s} {'t to 10%':>10s} {'t to 1%':>10s} {'peak LDC':>9s}")
rows = []
for name, parts, Vc, R, ldc, _ in opts:
    if name.startswith("0 "):
        t10, t1 = 0.4e-3 * np.log(10), 0.4e-3 * np.log(100)
        Vshow = 0.0
    elif name.startswith("0b"):
        T = t_linear_ramp(ldc - VP); t10, t1, Vshow = 0.9 * T, 0.99 * T, ldc - VP
    elif name.startswith("5"):
        # half the turns at the same ampere-turns: L/4, I*2, R/2
        Lh, Ih, Rh = L / 4, I0 * 2, 0.19 / 2 + 0.80
        t10 = t_decay(Vc, Rh, 0.10, Ih, Lh); t1 = t_decay(Vc, Rh, 0.01, Ih, Lh); Vshow = Vc
    else:
        t10, t1 = t_decay(Vc, R), t_decay(Vc, R, 0.01); Vshow = Vc
    rows.append((name, parts, Vshow, t10, t1, ldc))
    print(f"{name:34s} {Vshow:12.1f} V {t10*1e6:8.0f} us {t1*1e6:8.0f} us {ldc:7.1f} V")

# ---------------------------------------------------------------- figure
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C_LIM, C_FREE = "#2a78d6", "#eb6834"
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

fig, (a, b) = plt.subplots(1, 2, figsize=(13.5, 5.6))

# --- A: master curve. Only options that keep L and R unchanged sit on it.
V = np.logspace(np.log10(0.5), np.log10(400), 300)
a.loglog(V, t_decay(V) * 1e6, C_LIM, lw=2)
on_curve = [("D1 freewheel diode", VF), ("D1 + 6 V zener", VF + 5.1),
            ("D1 + 15 V TVS", VF + 15.0), ("series MOSFET + 100 V TVS", 100.0),
            ("series MOSFET + 250 V TVS", 250.0)]
for label, Vc in on_curve:
    a.plot(Vc, t_decay(Vc) * 1e6, "o", ms=8, color=C_LIM, mec=BG, mew=2, zorder=5)
    a.annotate(label, (Vc, t_decay(Vc) * 1e6), textcoords="offset points",
               xytext=(11, 7), fontsize=8.5, color=INK2)
a.set_xlim(0.5, 420); a.set_ylim(2.5, 1600)
plain(a.xaxis, [1, 2, 5, 10, 20, 50, 100, 200]); plain(a.yaxis, [5, 10, 30, 100, 300, 1000])
style(a, "Everything reduces to volts across the coil", "volts imposed across the coil [V]",
      "time for 2.5 A to fall to 10 % [\u00b5s]")
a.text(0.56, 3.4, "t \u2248 L\u00b7I\u2080 / V = 0.95 mV\u00b7s / V", fontsize=10, color=INK2, style="italic")

# --- B: speed against stress on the driver
b.axhspan(28, 34, color=C_FREE, alpha=0.09, lw=0)
b.axhline(28, color=INK2, lw=0.9, ls=(0, (4, 3)), label="28 V max compliance (unverified above)")
b.axhline(VP, color=INK2, lw=0.9, ls=(0, (1, 2)), label="V+ = 12 V (LDC idle level)")
short = {"0  Setpoint RC, tau = 0.4 ms": "setpoint RC, \u03c4 = 0.4 ms", "0b Setpoint linear ramp": "setpoint linear ramp",
         "1  D1 freewheel diode": "D1 only", "2  D1 + 6 V zener": "D1 + 6 V zener", "3  D1 + 15 V TVS": "D1 + 15 V TVS",
         "4  Series 2 ohm + D1": "series 2 \u03a9 + D1", "5  Half the turns, 5 A": "half the turns, 5 A",
         "6  Series MOSFET + 100 V TVS": "MOSFET + 100 V TVS", "7  Series MOSFET + 250 V TVS": "MOSFET + 250 V TVS"}
off = {"0  Setpoint RC, tau = 0.4 ms": (-40, -20), "0b Setpoint linear ramp": (7, -14),
       "1  D1 freewheel diode": (8, 7), "2  D1 + 6 V zener": (-10, 10),
       "3  D1 + 15 V TVS": (6, 8), "4  Series 2 ohm + D1": (-26, -18),
       "5  Half the turns, 5 A": (-16, -17), "6  Series MOSFET + 100 V TVS": (6, 10),
       "7  Series MOSFET + 250 V TVS": (-6, -17)}
for name, parts, Vs, t10, t1, ldc in rows:
    free = ldc <= VP
    b.plot(t10 * 1e6, ldc, "o", ms=9, color=C_FREE if free else C_LIM, mec=BG, mew=2, zorder=5)
    b.annotate(short[name], (t10 * 1e6, ldc), textcoords="offset points",
               xytext=off.get(name, (8, 6)), fontsize=8.5, color=INK2)
b.set_xscale("log"); b.set_xlim(2.2, 2600); b.set_ylim(9, 34)
plain(b.xaxis, [3, 10, 30, 100, 300, 1000])
style(b, "Speed against stress on the driver", "time for 2.5 A to fall to 10 % [\u00b5s]", "peak LDC voltage [V]")
b.plot([], [], "o", ms=9, color=C_LIM, mec=BG, mew=2, label="LDC carries the clamp voltage")
b.plot([], [], "o", ms=9, color=C_FREE, mec=BG, mew=2, label="LDC shielded from it")
b.legend(frameon=False, loc="center left", bbox_to_anchor=(0.015, 0.56), fontsize=9)

fig.suptitle("Ways to speed up the 2.5 A \u2192 0 ramp-down (L = 0.38 mH, R = 0.99 \u03a9, V+ = 12 V)",
             x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig("docs/ramp_speed_options.png", dpi=150)
