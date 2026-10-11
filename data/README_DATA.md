# Data additions for final dashboard

## space_trade.csv
Official Department of Space / ISRO parliamentary answer, Budget Session 2023, reporting annual space-technology-industry imports and exports for FY2014-15 through FY2021-22 (₹ crore).

Source: https://www.isro.gov.in/media_isro/pdf/docs/UsefulLinks/ParliamentQuestions/Budget_Session_2023.pdf

## gdp_fx.csv
GDP values are a consistent 2011-12-base historical vintage used for the dashboard's ratio calculations: current-price GDP and constant-price GDP for FY2014-15 through FY2024-25. FY2023-24 and FY2024-25 values follow the 2024-25 Economic Survey vintage (₹295.36 lakh crore / ₹173.82 lakh crore and ₹324.11 lakh crore / ₹184.88 lakh crore respectively). Earlier values are from the same 2011-12-base series.

Exchange-rate column uses annual average ₹/US$ values reported by RBI/FBIL; FY2024-25 = ₹84.57/US$.

Primary references:
- https://www.rbi.org.in/scripts/PublicationReportDetails.aspx?ID=1292
- https://www.rbi.org.in/scripts/PublicationsView.aspx?id=22613
- https://himachalservices.nic.in/economics/en-IN/eco-survey-2024-25.html

## Method note for real export shares

"Real export value" is an analytical proxy created by deflating the nominal export value with the GDP deflator (nominal GDP / real GDP), because a dedicated export-price deflator is not included in the project dataset. It is therefore NOT an official real-exports series and is labelled as a proxy in the dashboard.

## USD graph note

Nominal export values are converted to USD using the annual-average ₹/US$ rate. GDP is converted using the same annual-average rate. Consequently, the export/GDP percentage is mathematically the same ratio as the nominal rupee export/GDP ratio; the USD view is a presentation/unit conversion, not an independent economic estimate.
