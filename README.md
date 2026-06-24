# FinPlanIQ

FinPlanIQ is an FP&A and finance analytics portfolio project that simulates a company's monthly financial performance and analyzes budget vs actuals, revenue variance, expense variance, department performance, rolling forecasts, and scenario analysis.

The project is designed for roles such as Financial Analyst, FP&A Analyst, Finance Data Analyst, BI Analyst, Business Analyst in finance, and Risk/Reporting Analyst.

## Business Problem

Finance teams need to understand whether the company is performing above or below plan, which departments are overspending, which revenue segments are underperforming, and how future scenarios may impact profitability.

FinPlanIQ solves this by creating a realistic finance reporting workflow using Python, SQL, DuckDB, and Streamlit.

## Key Features

- Monthly budget vs actual analysis
- Revenue, COGS, operating expense, gross margin, and EBITDA tracking
- Department and cost center variance analysis
- Region and business unit revenue reporting
- Rolling revenue and EBITDA forecast
- Scenario analysis for revenue drops, payroll increases, and marketing spend changes
- Automated executive summary written in FP&A business language
- SQL reporting queries for finance analytics

## Tech Stack

- Python
- Pandas
- NumPy
- DuckDB
- SQL
- Streamlit
- Plotly

## Project Structure

```text
FinPlanIQ/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── finplaniq.duckdb
├── src/
│   ├── config.py
│   ├── generate_data.py
│   ├── clean_transform.py
│   ├── build_duckdb.py
│   ├── kpi_calculations.py
│   ├── forecasting.py
│   ├── scenario_analysis.py
│   └── executive_summary.py
├── app/
│   └── streamlit_app.py
├── sql/
│   └── reporting_queries.sql
├── notebooks/
├── docs/
└── screenshots/
```

## Dataset Overview

The project simulates 36 months of financial data from January 2023 to December 2025.

The dataset includes:

- Monthly revenue
- Budget revenue
- Actual revenue
- COGS
- Operating expenses
- Payroll expense
- Department headcount
- Cost centers
- Regions
- Business units
- Variance drivers

## Core KPIs

| KPI | Definition |
|---|---|
| Total Revenue | Actual revenue for the selected period |
| Revenue Variance | Actual revenue minus budget revenue |
| Revenue Variance % | Revenue variance divided by budget revenue |
| Gross Profit | Revenue minus COGS |
| Gross Margin % | Gross profit divided by revenue |
| Operating Expenses | Payroll plus other operating expenses |
| Expense Variance | Actual opex minus budget opex |
| EBITDA | Gross profit minus operating expenses |
| EBITDA Margin % | EBITDA divided by revenue |
| Department Overspend | Department where actual spend exceeds budget |
| Unfavorable Variance Driver | Revenue shortfall or expense overspend impacting profit |

## Dashboard Pages

1. Executive Summary
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 1 40 20 PM" src="https://github.com/user-attachments/assets/9e030b96-ef5e-425c-bb9f-9b1616fb79d1" />
2. Budget vs Actuals\
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 27 04 PM" src="https://github.com/user-attachments/assets/dbf53e02-ca02-4b4d-8ba1-c7c25d1a245a" />
3. Department Analysis
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 27 53 PM" src="https://github.com/user-attachments/assets/ceba44fb-4b25-48aa-a0d7-7df5d6006f37" />
4. Revenue & Expense Trends
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 28 25 PM" src="https://github.com/user-attachments/assets/d2d0b75c-7751-498e-85a3-67ecc6bda207" />
5. Forecasting
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 29 53 PM" src="https://github.com/user-attachments/assets/3d721f2c-dfc2-4d62-a5f0-aad52777bafd" />
6. Scenario Analysis
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 30 17 PM" src="https://github.com/user-attachments/assets/6e89bb28-03a2-41d5-a1c6-88b99f230367" />
7. Variance Drivers
<img width="1470" height="747" alt="Screenshot 2026-06-24 at 3 31 03 PM" src="https://github.com/user-attachments/assets/e0761bf0-8d92-4e15-98f7-7d4c52d6d112" />
