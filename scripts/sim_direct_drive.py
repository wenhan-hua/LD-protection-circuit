"""Simulate ramp-up (driver saturated at compliance) and ramp-down (D1 freewheel) for the direct-drive circuit.
Run: .venv/bin/python scripts/sim_direct_drive.py -> docs/direct_drive_sim.png + printed numbers
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

L = 0.38e-3
R_COIL, R_CABLE = 0.19, 0.80
R = R_COIL + R_CABLE            # 0.99 ohm total
I_SET = 3.0
V_COMPL = 2.0                   # LDC cannot go below ~2 V (driver compliance = V+ - 2)

def vf(i):
    """1N5408-like forward drop vs current (approx. fit: 0.7 V + 0.1 V/A)."""
    return 0.7 + 0.1 * max(i, 0)

def ramp_up(vplus):
    # driver saturated: coil sees V+ - 2 V - iR until i reaches setpoint
    f = lambda t, y: [(vplus - V_COMPL - R * y[0]) / L]
    ev = lambda t, y: y[0] - I_SET
    ev.terminal = True
    s = solve_ivp(f, [0, 5e-3], [0], events=ev, max_step=1e-6)
    return s.t_events[0][0] if len(s.t_events[0]) else np.inf

def ramp_down(vplus):
    f = lambda t, y: [-(R * y[0] + vf(y[0])) / L]
    ev = lambda t, y: y[0] - 0.01
    ev.terminal = True
    s = solve_ivp(f, [0, 5e-3], [I_SET], events=ev, max_step=1e-6, dense_output=True)
    t_end = s.t_events[0][0]
    return s, t_end

print(f"L = {L*1e3:.2f} mH, R = {R:.2f} ohm, tau = {L/R*1e3:.2f} ms")
print(f"Ramp-down 3 A -> 0 through D1 only: {ramp_down(0)[1]*1e3:.2f} ms ; "
      f"LDC peak = V+ + Vf({I_SET} A) = V+ + {vf(I_SET):.1f} V")
for vp in (5, 6, 8, 10, 12):
    ok = (vp - V_COMPL) / R >= I_SET
    pd = (vp - I_SET * R) * I_SET
    t = ramp_up(vp) if ok else float('nan')
    print(f"V+ = {vp:2d} V: I_max = {(vp-V_COMPL)/R:.2f} A, ramp-up to 3 A = {t*1e3:.2f} ms, "
          f"driver dissipation = {pd:.1f} W, LDC peak at turn-off = {vp+vf(I_SET):.1f} V")

# plot for V+ = 6 V
vp = 6.0
fu = lambda t, y: [(vp - V_COMPL - R * y[0]) / L]
up = solve_ivp(fu, [0, 2e-3], [0], max_step=1e-6)
dn, tend = ramp_down(vp)
td = np.linspace(0, tend, 400)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
ax[0].plot(up.t * 1e3, np.minimum(up.y[0], 3.0) if False else up.y[0]); ax[0].axhline(3, ls="--", c="gray")
ax[0].set(title=f"Ramp-up, V+ = {vp:.0f} V (saturated drive, until setpoint)", xlabel="ms", ylabel="coil current [A]")
ax[1].plot(td * 1e3, dn.sol(td)[0]); ax[1].set(title=f"Ramp-down via D1 only ({tend*1e3:.2f} ms)", xlabel="ms")
for a in ax: a.grid(alpha=.3)
fig.tight_layout(); fig.savefig("docs/direct_drive_sim.png", dpi=150)
