"""What a scope sees when the clamp actually FIRES, versus a normal ramp.

The working ramp is sized so the clamp stays asleep (see sim_fastest_safe_ramp.py).
This script covers the other case: a fault -- ENABLE drops, the coil is
disconnected, or a ramp is commanded faster than 106 us -- where the driver stops
sinking and the coil freewheels through the clamp instead.

  t < 0      steady 2.5 A, LDC = V+ - I0 R = 9.53 V, clamp reverse-biased
  t = 0      driver stops sinking; LDC charges stray C at i/C ~ GV/s (ns edge)
  LDC rises  until the TVS breaks down, then is pinned at V+ + Vf + Vtvs
  flat top   droops as Vf and the TVS dynamic-resistance term shrink with i
  i -> 0     clamp stops conducting, LDC collapses back to V+

    freewheel loop:  coil -> LDC -> D1 -> TVS -> LDA -> coil
    (excludes both the driver and ground, which is why I MON reads ~0)

    L di/dt = -(Vf(i) + Vtvs(i) + i R)      ->  i(t) = (I0 + A) exp(-t/tau) - A
    with A = Vc/R, tau = L/R, Vc = Vf + Vtvs

Writes figures/fault-clamp-waveform.png.
Run: .venv/bin/python scripts/sim_fault_clamp.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L, R, I0, VP = 0.38e-3, 0.99, 2.5, 12.0
VBR, RDYN = 10.0, 0.05                  # TVS breakdown and dynamic resistance
DV_RAMP = 8.95                          # Vwm + Vf(leakage): the in-regulation ramp
T_RAMP = L * I0 / DV_RAMP               # 106 us commanded linear ramp
FRAC = 0.10

def vf(i):   return 0.70 + 0.10 * i     # D1 forward drop vs current
def vtvs(i): return VBR + RDYN * i      # TVS held in breakdown

Vc = vf(I0) + vtvs(I0)
A, tau = Vc / R, L / R
t_zero = tau * np.log((I0 + A) / A)                       # current actually reaches 0
t_10 = tau * np.log((I0 + A) / (FRAC * I0 + A))           # 10 % point

print(f"V+ = {VP:.0f} V | L = {L*1e3:.2f} mH | R = {R:.2f} ohm | I0 = {I0:.1f} A\n")
print("FAULT: coil freewheels through D1 + TVS")
print(f"  LDC pinned         {VP+vf(I0)+vtvs(I0):6.2f} V at 2.5 A  ->  "
      f"{VP+vf(0)+vtvs(0):5.2f} V as i -> 0   (droop {vf(I0)+vtvs(I0)-vf(0)-vtvs(0):.2f} V)")
print(f"  opposing voltage   {Vc:6.2f} V")
print(f"  decay to 10 %      {t_10*1e6:6.1f} us")
print(f"  current reaches 0  {t_zero*1e6:6.1f} us   (clamp conducts for this long)")
print(f"  I MON              reads ~0 throughout, while the coil is still energised\n")
print("NORMAL RAMP: driver stays in regulation, clamp asleep")
print(f"  commanded T        {T_RAMP*1e6:6.1f} us")
print(f"  LDC steady         {VP-I0*R:6.2f} V")
print(f"  LDC step at t=0    {VP-I0*R+DV_RAMP:6.2f} V")
print(f"  LDC peak (at end)  {VP+DV_RAMP:6.2f} V   margin to clamp "
      f"{VP+vf(I0)+vtvs(I0)-(VP+DV_RAMP):.2f} V")
print(f"  decay to 10 %      {0.9*T_RAMP*1e6:6.1f} us")
print(f"  I MON              tracks the coil for the whole ramp\n")
print(f"The fault decays {(0.9*T_RAMP)/t_10:.2f}x FASTER than the working ramp "
      f"-- a constant-voltage clamp is the optimal trajectory. That speed is given up "
      f"deliberately to keep I MON valid.")

# ------------------------------------------------------------------ waveforms
t = np.linspace(-25e-6, 140e-6, 4000)
i_f = np.where(t < 0, I0, np.clip((I0 + A) * np.exp(-np.maximum(t, 0) / tau) - A, 0, None))
edge = 1 - np.exp(-np.maximum(t, 0) / 0.3e-6)             # ns in reality; slowed to be visible
ldc_f = np.where(t < 0, VP - I0 * R,
                 np.where(i_f > 0,
                          (VP - I0 * R) + edge * ((VP + vf(i_f) + vtvs(i_f)) - (VP - I0 * R)),
                          VP))
i_n = np.where(t < 0, I0, np.clip(I0 * (1 - t / T_RAMP), 0, None))
ldc_n = np.where(t < 0, VP - I0 * R, np.where(t < T_RAMP, VP - i_n * R + DV_RAMP, VP))

BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
CF, CN, CR = "#d6336c", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.facecolor": BG, "figure.facecolor": BG})
fig, ax = plt.subplots(3, 1, figsize=(11.5, 11), sharex=True)

def style(a, yl, title):
    a.set_ylabel(yl); a.grid(True, color=GRID, lw=0.8); a.set_axisbelow(True)
    a.set_title(title, loc="left", fontsize=11.5, color=INK, fontweight="bold")
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.axvspan(0, t_zero * 1e6, color=CF, alpha=0.06, lw=0)

a = ax[0]
a.axhline(28, color=CR, lw=1.3, ls=(0, (5, 3)))
a.text(137, 28.6, "28 V — only published figure near this pin", ha="right", fontsize=9, color=CR)
a.axhline(VP, color=INK2, lw=1.0, ls=(0, (3, 3)))
a.text(-23, VP + 0.5, f"V+ = {VP:.0f} V", fontsize=9, color=INK2)
a.plot(t * 1e6, ldc_n, lw=2.0, color=CN, label="normal ramp — clamp stays asleep")
a.plot(t * 1e6, ldc_f, lw=2.4, color=CF, label="FAULT — clamp conducting")
a.annotate("clamp fires, LDC pinned ≈ 23 V", xy=(30, ldc_f[np.argmin(abs(t - 30e-6))]),
           xytext=(52, 26.3), fontsize=9.5, color=CF,
           arrowprops=dict(arrowstyle="->", color=CF, lw=1.2))
a.annotate("edge is ~ns, set by stray C\n(drawn slowed for visibility)", xy=(0.6, 20),
           xytext=(13, 15.4), fontsize=8.6, color=INK2,
           arrowprops=dict(arrowstyle="->", color=INK2, lw=0.9))
a.annotate("peak 21.0 V at the END", xy=(T_RAMP * 1e6, VP + DV_RAMP), xytext=(74, 18.2),
           fontsize=9.5, color=CN, arrowprops=dict(arrowstyle="->", color=CN, lw=1.2))
a.plot([t_zero * 1e6], [VP], 'o', color=CF, ms=7)
a.annotate("current gone → clamp opens,\nLDC falls back to V+", xy=(t_zero * 1e6, VP),
           xytext=(95, 15.8), fontsize=9, color=CF,
           arrowprops=dict(arrowstyle="->", color=CF, lw=1.1))
a.set_ylim(5, 31); style(a, "LDC  [V]", "① LDC — what the clamp does to the voltage")
a.legend(frameon=False, fontsize=10, loc="lower left")

a = ax[1]
a.plot(t * 1e6, i_n, lw=2.0, color=CN, label=f"normal ramp — {0.9*T_RAMP*1e6:.0f} µs to 10 %")
a.plot(t * 1e6, i_f, lw=2.4, color=CF, label=f"fault freewheel — {t_10*1e6:.0f} µs to 10 %")
a.axhline(FRAC * I0, color=INK2, lw=1.0, ls=(0, (4, 3)))
a.text(137, FRAC * I0 + 0.08, "10 %", ha="right", fontsize=9, color=INK2)
a.set_ylim(-0.1, 2.8); style(a, "coil current  [A]", "② Coil current — the fault is actually FASTER")
a.legend(frameon=False, fontsize=10, loc="upper right")

a = ax[2]
a.plot(t * 1e6, i_n / 2.0, lw=2.0, color=CN, label="normal ramp — tracks the coil")
a.plot(t * 1e6, np.where(t < 0, I0 / 2.0, 0.0), lw=2.4, color=CF,
       label="fault — reads ~0 while coil is still full")
a.annotate("I MON lies here:\ncoil has 2.5 A, monitor says 0", xy=(10, 0.02), xytext=(26, 0.55),
           fontsize=9.5, color=CF, arrowprops=dict(arrowstyle="->", color=CF, lw=1.2))
a.set_ylim(-0.08, 1.45); style(a, "I MON  [V]   (2 A/V)", "③ I MON — why the clamp is fault-only by design")
a.set_xlabel("time  [µs]"); a.set_xlim(-25, 140)
a.legend(frameon=False, fontsize=10, loc="upper right")

fig.tight_layout()
fig.savefig("figures/fault-clamp-waveform.png", dpi=140, bbox_inches="tight")
