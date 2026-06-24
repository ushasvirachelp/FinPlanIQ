# Methodology

## 1. Data Simulation

The project simulates a realistic company operating model with monthly revenue, COGS, opex, and headcount data. Revenue is modeled by region and business unit with growth assumptions and underperformance periods. Expenses are modeled by department, cost center, payroll, and non-payroll spend.

## 2. Data Transformation

Python transforms raw data into finance reporting tables:

- Monthly financial summary
- Department variance report
- Revenue variance report
- Ranked variance drivers

## 3. Reporting Layer

DuckDB stores raw and processed tables so the project demonstrates SQL-based analytics and reporting workflows.

## 4. Dashboard

Streamlit presents the analysis through FP&A-style dashboard pages for executive summary, budget vs actuals, department analysis, trends, forecasting, scenarios, and variance drivers.

## 5. Forecasting

The project uses a simple rolling forecast based on trailing revenue growth, COGS rate, and opex growth. This keeps the project realistic for FP&A work rather than turning it into an overly complex machine learning model.

## 6. Scenario Analysis

Scenario logic estimates the impact of revenue drops, payroll increases, and marketing spend changes on EBITDA and margin.