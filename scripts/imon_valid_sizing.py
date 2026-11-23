"""Size the clamp so the driver stays in regulation and I MON keeps reading true current.

I MON measures current through the driver's internal sense, NOT the coil. Any current
that freewheels through the clamp is invisible to it. So the clamp must be chosen to
sit ABOVE the working ramp, firing only on faults.

Commanded linear ramp of duration T, driver in regulation:
    i(t)  = I0 (1 - t/T)
    LDC(t)= V+ - i R + L I0 / T      -> peak at the END (i -> 0) = V+ + L I0 / T
Note the peak does not depend on R, so a series resistor buys nothing for a linear
commanded ramp (it still helps thermals, ramp-up, and clamp-assisted decay).
Run: .venv/bin/python scripts/imon_valid_sizing.py
"""
import numpy as np

L, R, I0, FRAC = 0.38e-3, 0.99, 2.5, 0.10
VF_LOW, VF_HI = 0.4, 0.95      # D1 drop at leakage currents / at 2.5 A

# part, standoff Vwm, Vbr typ, max leakage at Vwm (uA)  [Vishay/Littelfuse 1.5KE]
tvs = [("1.5KE6.8A", 5.80, 6.80, 1000.0),
       ("1.5KE10A",  8.55, 10.0, 5.0),
       ("1.5KE15A", 12.80, 15.0, 1.0),
       ("1.5KE18A", 15.30, 18.0, 1.0)]

print("Working ramp kept below the TVS standoff, so the clamp stays off and I MON stays true.\n")
print(f"{'TVS':11s}{'usable dV':>11s}{'ramp T':>9s}{'t to 10%':>10s}"
      f"{'peak LDC @8V':>14s}{'@12V':>8s}{'fault clamp @8V':>17s}{'leak err':>10s}")
for nm, vwm, vbr, ir in tvs:
    dv = vwm + VF_LOW                      # clamp stays off up to here
    T = L * I0 / dv
    t10 = (1 - FRAC) * T
    fault = 8 + vbr + VF_HI
    print(f"{nm:11s}{dv:9.1f} V{T*1e6:7.0f} us{t10*1e6:8.0f} us"
          f"{8 + dv:12.1f} V{12 + dv:7.1f} V{fault:15.1f} V{ir/1e6/I0*1e6:8.0f} ppm")

print("\nFor comparison, letting the clamp do the work (I MON blind during the decay):")
for nm, vwm, vbr, ir in tvs:
    vc = vbr + VF_HI
    t = (L / R) * np.log((I0 * R + vc) / (FRAC * I0 * R + vc))
    print(f"  {nm:11s} clamp {vc:5.1f} V -> {t*1e6:4.0f} us, peak LDC @8V = {8+vc:.1f} V")

print("\nThermal reminder (no series resistor):")
for vp in (8, 12):
    print(f"  V+ = {vp:2d} V: LDC steady {vp - I0*R:.2f} V, driver {(vp - I0*R)*I0:.1f} W "
          f"({(vp - I0*R)*I0/25*100:.0f} % of the 25 W no-airflow limit)")
