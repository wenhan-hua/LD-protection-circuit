| Ramp time T | di/dt | Peak LDC, no D1 | Peak LDC with D1 | Driver peak P | Driver avg P over ramp | Driver energy over ramp | Verdict (no D1) |
|---|---|---|---|---|---|---|---|
| 0.05 ms | 50000 A/s | 31.0 V | 12.9 V | 71 W | 36.7 W | 1.83 mJ | **avalanche risk** (above 30 V) |
| 0.1 ms | 25000 A/s | 21.5 V | 12.9 V | 48 W | 24.8 W | 2.48 mJ | high, unverified |
| 0.2 ms | 12500 A/s | 16.8 V | 12.9 V | 36 W | 18.9 W | 3.77 mJ | moderate |
| 0.5 ms | 5000 A/s | 13.9 V | 12.9 V | 29 W | 15.3 W | 7.66 mJ | benign (within about 2 V of V+) |
| 1 ms | 2500 A/s | 12.9 V | 12.9 V | 26 W | 14.1 W | 14.12 mJ | benign (within about 2 V of V+) |
| 2 ms | 1250 A/s | 12.5 V | 12.5 V | 25 W | 13.5 W | 27.06 mJ | benign (within about 2 V of V+) |
| 5 ms | 500 A/s | 12.2 V | 12.2 V | 24 W | 13.2 W | 65.87 mJ | benign (within about 2 V of V+) |
| 10 ms | 250 A/s | 12.1 V | 12.1 V | 24 W | 13.1 W | 130.56 mJ | benign (within about 2 V of V+) |

Steady 2.5 A dissipation: 23.8 W. Coil + cable energy ½·L·I0² = 1.19 mJ (≈ 50 µs of steady-state heat, independent of T).
With D1 the current cannot fall faster than natural decay, about 0.49 ms, so commanded ramps shorter than that are overridden.
