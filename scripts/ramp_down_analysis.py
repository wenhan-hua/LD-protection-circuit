"""Ramp-down 2.5 A -> 0 at several timescales, original config (no D1), V+ = 12 V.

Model: driver stays in regulation and forces i(t) = I0 (1 - t/T).
  LDC(t)   = V+ - i R - L di/dt = V+ - i R + L I0/T          (can exceed V+ near the end)
  P_drv(t) = LDC(t) * i(t)                                     (heat in the driver)
Run: .venv/bin/python scripts/ramp_down_analysis.py -> docs/ramp_down.png, docs/ramp_down_table.md
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L, R, VP, I0 = 0.38e-3, 0.99, 12.0, 2.5
P_NOAIR, P_AIR = 25.0, 35.0     # datasheet max internal dissipation, 25 C
V_SUPPLY_MAX = 30.0             # supply max; datasheet gives no separate LDC limit
VF = lambda i: 0.7 + 0.1 * i    # 1N5408-like

E_L = 0.5 * L * I0**2
P_ss = (VP - I0 * R) * I0
tau = L / R
t_d1 = tau * np.log(1 + (I0 * R) / VF(I0))   # natural decay time through D1 (approx., Vf at I0)

Ts = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]) * 1e-3

def metrics(T):
    a = L * I0 / T
    t = np.linspace(0, T, 4001)
    i = I0 * (1 - t / T)
    ldc = VP - i * R + a
    p = ldc * i
    return dict(T=T, didt=I0 / T, a=a, ldc_peak=VP + a, ldc_start=ldc[0],
                p_peak=p.max(), p_avg=np.trapz(p, t) / T, e_drv=np.trapz(p, t),
                ldc_peak_d1=VP + min(a, VF(I0)))

rows = [metrics(T) for T in Ts]

hdr = ("| Ramp time T | di/dt | Peak LDC, no D1 | Peak LDC with D1 | Driver peak P | Driver avg P over ramp | Driver energy over ramp | Verdict (no D1) |\n"
       "|---|---|---|---|---|---|---|---|\n")
def verdict(v):
    if v > V_SUPPLY_MAX: return "**avalanche risk** (above 30 V)"
    if v > VP + 5: return "high, unverified"
    if v > VP + 2: return "moderate"
    return "benign (within about 2 V of V+)"
body = ""
for r in rows:
    body += f"| {r['T']*1e3:g} ms | {r['didt']:.0f} A/s | "
    body += (f"{r['ldc_peak']:.1f} V | {r['ldc_peak_d1']:.1f} V | {r['p_peak']:.0f} W | {r['p_avg']:.1f} W | "
             f"{r['e_drv']*1e3:.2f} mJ | {verdict(r['ldc_peak'])} |\n")
foot = (f"\nSteady 2.5 A dissipation: {P_ss:.1f} W. Coil + cable energy ½·L·I0² = {E_L*1e3:.2f} mJ "
        f"(≈ {E_L/P_ss*1e6:.0f} µs of steady-state heat, independent of T).\n"
        f"With D1 the current cannot fall faster than natural decay, about {t_d1*1e3:.2f} ms, so commanded ramps shorter than that are overridden.\n")
open("docs/ramp_down_table.md", "w").write(hdr + body + foot)
print(hdr + body + foot)

# ---------------- plots ----------------
Tg = np.logspace(np.log10(0.05e-3), np.log10(10e-3), 200)
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))

pk = VP + L * I0 / Tg
ax[0].semilogx(Tg * 1e3, pk, "C0", lw=2, label="no D1 (original)")
ax[0].semilogx(Tg * 1e3, VP + np.minimum(L * I0 / Tg, 0.95), "C2", lw=2, label="with D1 (clamped, ramp ≥ %.2f ms)" % (t_d1 * 1e3))
ax[0].axhline(VP, c="gray", ls=":", label="V+ = 12 V (LDC at idle)")
ax[0].axhline(28, c="orange", ls="--", label="28 V (max compliance, datasheet)")
ax[0].axhline(30, c="r", ls="--", label="30 V (max supply)")
ax[0].set(xlabel="ramp time T [ms]", ylabel="peak LDC voltage [V]", title="Peak LDC voltage (end of ramp)")
ax[0].legend(fontsize=8); ax[0].grid(alpha=.3, which="both")

pp = np.array([metrics(T)["p_peak"] for T in Tg])
pa = np.array([metrics(T)["p_avg"] for T in Tg])
ax[1].semilogx(Tg * 1e3, pp, "C3", lw=2, label="peak power (start of ramp)")
ax[1].semilogx(Tg * 1e3, pa, "C1", lw=2, label="average over ramp")
ax[1].axhline(P_ss, c="gray", ls=":", label=f"steady 2.5 A: {P_ss:.1f} W")
ax[1].axhline(P_NOAIR, c="orange", ls="--", label="25 W (no airflow limit)")
ax[1].axhline(P_AIR, c="r", ls="--", label="35 W (with airflow limit)")
ax[1].set(xlabel="ramp time T [ms]", ylabel="driver dissipation [W]", title="Heat in the driver during the ramp")
ax[1].legend(fontsize=8); ax[1].grid(alpha=.3, which="both")

for T, c in zip((0.05e-3, 0.2e-3, 1e-3), ("C3", "C1", "C0")):
    t = np.linspace(0, T, 500); i = I0 * (1 - t / T)
    ax[2].plot(t / T, VP - i * R + L * I0 / T, c, label=f"T = {T*1e3:g} ms")
ax[2].axhline(VP, c="gray", ls=":"); ax[2].axhline(30, c="r", ls="--")
ax[2].set(xlabel="t / T", ylabel="LDC voltage [V]", title="LDC waveform during the ramp (no D1)")
ax[2].legend(fontsize=8); ax[2].grid(alpha=.3)
fig.tight_layout(); fig.savefig("docs/ramp_down.png", dpi=150)
