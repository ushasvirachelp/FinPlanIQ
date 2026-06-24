# Dataset Description

FinPlanIQ uses simulated monthly financial data from January 2023 through December 2025.

## Raw Tables

| Table | Description |
|---|---|
| `dim_date` | Month, year, and quarter fields |
| `dim_department` | Department and cost center mapping |
| `dim_region` | Geographic region mapping |
| `dim_business_unit` | Business unit mapping |
| `fact_revenue_cogs` | Monthly budget and actual revenue and COGS by region and business unit |
| `fact_opex_headcount` | Monthly budget and actual opex and headcount by department |

## Processed Tables

| Table | Description |
|---|---|
| `monthly_financial_summary` | Monthly revenue, COGS, opex, gross profit, EBITDA, margin, and variance |
| `department_variance_report` | Department-level operating expense and headcount variance |
| `revenue_variance_report` | Revenue variance by region and business unit |
| `variance_drivers` | Ranked unfavorable revenue shortfalls and expense overspend drivers |