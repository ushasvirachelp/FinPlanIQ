## Live Demo

[Launch FinPlanIQ](YOUR_STREAMLIT_APP_LINK_HERE)

# FinPlanIQ

FinPlanIQ is an FP&A and finance analytics portfolio project that simulates a company's monthly financial performance and analyzes budget vs actuals, revenue variance, expense variance, department performance, rolling forecasts, and scenario analysis.

The project is designed for roles such as Financial Analyst, FP&A Analyst, Finance Data Analyst, BI Analyst, Business Analyst in finance, and Risk/Reporting Analyst.

## Business Problem

Finance teams need to understand whether the company is performing above or below plan, which departments are overspending, which revenue segments are underperforming, and how future scenarios may impact profitability.

FinPlanIQ solves this by creating a realistic finance reporting workflow using Python, SQL, DuckDB, and Streamlit.

## Key Features

* Monthly budget vs actual analysis
* Revenue, COGS, operating expense, gross margin, and EBITDA tracking
* Department and cost center variance analysis
* Region and business unit revenue reporting
* Rolling revenue and EBITDA forecast
* Scenario analysis for revenue drops, payroll increases, and marketing spend changes
* Automated executive summary written in FP&A business language
* SQL reporting queries for finance analytics

## Security Features

* Secure upload validation for user-provided FP&A workbooks
* `.xlsx` file allowlisting
* Rejection of unsupported or macro-enabled file formats
* Upload size limit of 10 MB
* In-memory file processing for uploaded financial data
* Privacy notice for user-uploaded datasets
* Safe error handling for invalid uploads
* Security documentation available in `SECURITY.md`

## Tech Stack

* Python
* Pandas
* NumPy
* DuckDB
* SQL
* Streamlit
* Plotly

## Project Structure

```text
FinPlanIQ/
├── README.md
├── SECURITY.md
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
│   ├── upload_processor.py
│   ├── security_utils.py
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

* Monthly revenue
* Budget revenue
* Actual revenue
* COGS
* Operating expenses
* Payroll expense
* Department headcount
* Cost centers
* Regions
* Business units
* Variance drivers

## Core KPIs

| KPI                         | Definition                                              |
| --------------------------- | ------------------------------------------------------- |
| Total Revenue               | Actual revenue for the selected period                  |
| Revenue Variance            | Actual revenue minus budget revenue                     |
| Revenue Variance %          | Revenue variance divided by budget revenue              |
| Gross Profit                | Revenue minus COGS                                      |
| Gross Margin %              | Gross profit divided by revenue                         |
| Operating Expenses          | Payroll plus other operating expenses                   |
| Expense Variance            | Actual opex minus budget opex                           |
| EBITDA                      | Gross profit minus operating expenses                   |
| EBITDA Margin %             | EBITDA divided by revenue                               |
| Department Overspend        | Department where actual spend exceeds budget            |
| Unfavorable Variance Driver | Revenue shortfall or expense overspend impacting profit |

## Dashboard Pages

1. Executive Summary
   ![alt text](<Screenshot 2026-06-24 at 1.40.20 PM.png>)

2. Budget vs Actuals
   ![alt text](<Screenshot 2026-06-24 at 3.27.04 PM.png>)

3. Department Analysis
   ![alt text](<Screenshot 2026-06-24 at 3.27.53 PM.png>)

4. Revenue & Expense Trends
   ![alt text](<Screenshot 2026-06-24 at 3.28.25 PM.png>)

5. Forecasting
   ![alt text](<Screenshot 2026-06-24 at 3.29.53 PM.png>)

6. Scenario Analysis
   ![alt text](<Screenshot 2026-06-24 at 3.30.17 PM.png>)

7. Variance Drivers
   ![alt text](<Screenshot 2026-06-24 at 3.31.03 PM.png>)
