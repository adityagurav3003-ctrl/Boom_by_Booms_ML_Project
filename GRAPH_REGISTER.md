# Final graph register

| ID | Graph | Status | Main source/data |
|---|---|---|---|
| I | Export value over time: defence + space technology industry | READY | DDP defence exports; DoS/ISRO space-industry exports |
| II | Exports as % of GDP, nominal and real | READY | Defence/space exports + MoSPI GDP; real export is explicitly a GDP-deflator proxy |
| III | Exports as % of GDP in USD | READY | Export/GDP series + annual-average INR/USD; ratio is mathematically unchanged by common FX conversion |
| IV | Defence + space forecast with contextual events | READY | Existing PyTorch models + documented collaboration events |
| V | Value of space imports | READY | DoS/ISRO parliamentary series, FY2014-15–FY2021-22 |
| VI | Defence export value | READY | DDP defence-export series |

## Important interpretation rules

- Graph II's "real" export value is an analytical proxy, not an official real-exports series.
- Graph III is a USD presentation, not an independent estimate: using the same annual FX rate for numerator and denominator leaves the percentage unchanged.
- Graph V currently ends at FY2021-22 because that is the span of the verified annual parliamentary series used here. No later years are invented.
- Forecasts are experimental model outputs, not official projections.
