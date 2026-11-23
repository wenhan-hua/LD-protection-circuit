**Linear ramp**

| Ramp time T | Peak LDC | Driver peak P | Time to 10 % | Verdict |
|---|---|---|---|---|
| 0.05 ms | 31.0 V | 71 W | 0.05 ms | avalanche risk (above 30 V) |
| 0.1 ms | 21.5 V | 48 W | 0.09 ms | high, unverified |
| 0.2 ms | 16.8 V | 36 W | 0.18 ms | moderate |
| 0.5 ms | 13.9 V | 29 W | 0.45 ms | benign |
| 1 ms | 12.9 V | 26 W | 0.9 ms | benign |
| 2 ms | 12.5 V | 25 W | 1.8 ms | benign |
| 5 ms | 12.2 V | 24 W | 4.5 ms | benign |
| 10 ms | 12.1 V | 24 W | 9 ms | benign |

**Exponential (RC) ramp**

| τ | Peak LDC | Driver peak P | Time to 10 % | Time to 1 % | Verdict |
|---|---|---|---|---|---|
| 0.05 ms | 28.5 V | 71 W | 0.12 ms | 0.23 ms | high, unverified |
| 0.1 ms | 19.0 V | 48 W | 0.23 ms | 0.46 ms | high, unverified |
| 0.2 ms | 14.3 V | 36 W | 0.46 ms | 0.92 ms | moderate |
| 0.3 ms | 12.7 V | 32 W | 0.69 ms | 1.38 ms | benign |
| 0.4 ms | 12.0 V | 30 W | 0.92 ms | 1.84 ms | benign, no overshoot above V+ |
| 0.5 ms | 12.0 V | 29 W | 1.15 ms | 2.3 ms | benign, no overshoot above V+ |
| 1 ms | 12.0 V | 26 W | 2.3 ms | 4.61 ms | benign, no overshoot above V+ |
| 2 ms | 12.0 V | 25 W | 4.61 ms | 9.21 ms | benign, no overshoot above V+ |

Steady 2.5 A dissipation 23.8 W. The exponential has no overshoot above V+ when τ ≥ L/R = 0.38 ms. Stored coil energy ½·L·I0² = 1.19 mJ.
