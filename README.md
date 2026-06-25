# FinPlanIQ

## Live Demo

https://finplaniq-jyrfgtljthputrmbmjj8ca.streamlit.app/

FinPlanIQ is a deployed FP&A and finance analytics portfolio project that recreates a simplified month-end reporting workflow for budget vs actuals, variance analysis, department performance, forecasting, scenario planning, and management pack generation.

I built this project to strengthen my finance analytics knowledge and better understand how internal finance teams analyze performance, explain variances, and support leadership reporting.

The project is designed for roles such as Financial Analyst, FP&A Analyst, Finance Data Analyst, BI Analyst, Business Analyst in finance, and Risk/Reporting Analyst.

## Business Problem

Month-end FP&A reporting often involves comparing actuals against plan, identifying key variance drivers, reviewing department-level spend, updating forecasts, modeling downside scenarios, and preparing leadership-ready summaries.

FinPlanIQ explores how this workflow can be made more repeatable and self-service by combining structured financial data, automated KPI calculations, variance analysis, forecasting, scenario modeling, and Excel management pack export.

The project uses Python, SQL, DuckDB, and Streamlit to simulate and analyze a realistic finance reporting workflow.

## Key Features

* Monthly budget vs actual analysis
* Revenue, COGS, operating expense, gross margin, and EBITDA tracking
* Department and cost center variance analysis
* Region and business unit revenue reporting
* Rolling revenue and EBITDA forecast
* Scenario analysis for revenue drops, payroll increases, and marketing spend changes
* Automated executive summary written in FP&A business language
* Downloadable Excel management pack
* User-uploaded FP&A datasets using a provided Excel template
* SQL reporting queries for finance analytics
* Deployed Streamlit dashboard

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

FinPlanIQ also supports optional template-based user uploads for demonstration purposes. Uploaded files are processed in memory and should follow the provided Excel template.

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
2. Budget vs Actuals
3. Department Analysis
4. Revenue & Expense Trends
5. Forecasting
6. Scenario Analysis
7. Variance Drivers

## Project Note

FinPlanIQ is a portfolio and learning project. It uses a simulated demo dataset and optional template-based uploads for demonstration purposes.

It is not investment advice, financial advice, or an enterprise production finance system. Users should avoid uploading confidential company financial data to a public demo deployment.
