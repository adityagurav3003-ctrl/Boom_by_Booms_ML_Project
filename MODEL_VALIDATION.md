# Model validation summary

## Defence exports

Chronological split:
- Training: FY2016-17 to FY2021-22 (6 observations)
- Held-out test: FY2022-23 to FY2024-25 (3 observations)
- Lookback: 2 years
- Seed: 42
- Architecture: 2 → 8 → ReLU → 1
- Parameters: 33
- Loss: MSE
- Optimizer: Adam, learning rate 0.001
- Epochs: 1000

Held-out test metrics:

| Model | MAE (₹ crore) | RMSE (₹ crore) |
|---|---:|---:|
| Naïve last-value baseline | 3,602.33 | 3,774.66 |
| Raw nonlinear PyTorch | 2,289.35 | 2,548.39 |
| Normalized nonlinear PyTorch | 23,592.33 | 26,329.85 |
| Linear PyTorch control | 10,541.76 | 11,086.21 |

Experimental FY2025-26 forecast: approximately ₹27,108 crore.

The raw nonlinear model is retained because it outperformed the locked naïve benchmark on the three held-out observations. The result is exploratory because n=3 in the test set and the full annual series has only nine observations.

## Space / NSIL revenue

- Observations: FY2019-20 to FY2024-25 (6)
- Architecture: 1 → 1 linear trend
- Forecast period: FY2025-26
- Experimental forecast: ₹3,851.34 crore
- Target: NSIL company-level total revenue, not the entire Indian space sector.
