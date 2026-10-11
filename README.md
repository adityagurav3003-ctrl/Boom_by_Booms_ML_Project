# Boom by Booms — Final Dockerized Research & ML Dashboard

This is the final reproducibility package for the **Boom by Booms** research project on the economic impact of public-private collaboration in India's strategic defence and space sectors.

## What is included

- Verified historical defence-export series.
- Official space-technology-industry import/export series (FY2014-15–FY2021-22).
- GDP and annual-average INR/USD macro layer for ratio and USD presentation graphs.
- Existing PyTorch defence-export forecast model.
- Existing PyTorch NSIL-revenue forecast model.
- Streamlit dashboard containing all six requested research-graph sections.
- A readable PyTorch code showcase inside the dashboard.
- Source/method notes and graph register.

## Run locally with Docker

```bash
docker build -t boom-by-booms .
docker run --rm -p 8501:8501 boom-by-booms
```

Open:

```text
http://localhost:8501
```

## Graphs

I. Export value over time

II. Exports as % of GDP — nominal and real

III. Exports as % of GDP — USD presentation

IV. Forecast trajectory and contextual public-private events

V. Value of space imports

VI. Defence export value

See `GRAPH_REGISTER.md` for the exact interpretation and data limits of each graph.

## Important methodological notes

### Graph II
A dedicated export-price deflator is not in the project dataset. The real-export line therefore uses a transparent analytical proxy: nominal exports divided by the GDP deflator (nominal GDP / real GDP). It must not be described as an official real-export series.

### Graph III
Exports and GDP are both converted from INR to USD using the same annual-average exchange rate. Therefore the percentage is mathematically identical to the nominal INR export/GDP ratio. The graph is retained because the research specification requested the USD presentation.

### Graph IV
The PyTorch models are exploratory forecasting extensions. The defence model uses nine annual observations, a chronological train/test design and a one-step FY2025-26 forecast. The project deliberately does not present recursive 2030/2035 extrapolations as reliable forecasts.

### Graph V
The space-import series is an official Department of Space/ISRO parliamentary series and currently covers FY2014-15 through FY2021-22. No missing years are fabricated or imputed.

## Primary data references

- Department of Space / ISRO, Budget Session 2023 parliamentary answer: https://www.isro.gov.in/media_isro/pdf/docs/UsefulLinks/ParliamentQuestions/Budget_Session_2023.pdf
- MoSPI National Accounts / GDP data catalogue: https://esankhyiki.mospi.gov.in/catalogue-main/catalogue?page=0&product=NAS&rowsPerPage=10
- MoSPI GDP 2025-26 FAE press note: https://www.mospi.gov.in/uploads/latestReleases/latest_release_1767781372753_1380ce82-f5a5-440d-99e6-e6b35af0deb5_GDP_Press_Note_on_FAE_2025-26.pdf
- RBI exchange-rate table: https://www.rbi.org.in/scripts/PublicationsView.aspx?id=22613

## Reproducibility

The saved `.pth` files are loaded directly by the application. The complete model-development notebook should be kept with the research repository for inspection of preprocessing, training, testing and reproducibility checks.

## AI assistance disclosure

AI tools were used as technical assistants for implementation, debugging, data structuring, Docker configuration and methodological discussion. The research design, source selection and verification, variable definitions, treatment of source-vintage issues, interpretation and final conclusions remain the student's responsibility.
