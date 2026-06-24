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
2. Budget vs Actuals
3. Department Analysis
4. Revenue & Expense Trends
5. Forecasting
6. Scenario Analysis
7. Variance Drivers

## How To Run The Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate raw financial data:

```bash
python src/generate_data.py
```

Create processed reporting tables:

```bash
python src/clean_transform.py
```

Build the DuckDB database:

```bash
python src/build_duckdb.py
```

Run the Streamlit dashboard:

```bash
streamlit run app/streamlit_app.py
```

## Example Business Insight

In the latest month, FinPlanIQ identifies whether revenue came in above or below budget, highlights departments with operating expense overspend, calculates EBITDA impact, and explains the top unfavorable variance drivers in leadership-ready language.

## Resume Bullets

- Built FinPlanIQ, an FP&A analytics dashboard using Python, DuckDB, SQL, and Streamlit to analyze budget vs actuals, revenue variance, department overspend, gross margin, EBITDA, and rolling forecast performance.
- Simulated 36 months of realistic financial operating data across regions, business units, departments, cost centers, revenue, COGS, operating expenses, payroll, and headcount.
- Developed SQL-ready reporting tables and KPI calculations for revenue variance %, expense variance %, gross margin %, EBITDA margin, department overspend, and top unfavorable variance drivers.
- Created scenario analysis to quantify EBITDA and margin impact from revenue declines, payroll inflation, and marketing spend changes.
- Generated automated executive summaries translating financial variance drivers into concise business insights for management reporting.

## Interview Talking Point

FinPlanIQ is a realistic FP&A reporting project that mirrors how finance teams track company performance. I built the data pipeline, reporting tables, DuckDB database, SQL queries, and Streamlit dashboard to analyze budget vs actuals, explain variance drivers, forecast future performance, and test profitability scenarios.