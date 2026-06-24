-- 1. Monthly executive financial summary
SELECT
    month,
    actual_revenue,
    budget_revenue,
    revenue_variance,
    revenue_variance_pct,
    actual_opex,
    opex_variance,
    gross_margin_pct,
    actual_ebitda,
    ebitda_margin_pct
FROM monthly_financial_summary
ORDER BY month;


-- 2. Latest month top unfavorable variance drivers
SELECT
    month,
    driver_type,
    driver_category,
    unfavorable_amount,
    explanation
FROM variance_drivers
WHERE month = (
    SELECT MAX(month)
    FROM variance_drivers
)
ORDER BY unfavorable_amount DESC
LIMIT 10;


-- 3. Department overspend by month
SELECT
    month,
    department,
    cost_center,
    budget_opex,
    actual_opex,
    opex_variance,
    opex_variance_pct,
    actual_headcount,
    budget_headcount
FROM department_variance_report
WHERE overspend_flag = TRUE
ORDER BY month, opex_variance DESC;


-- 4. Revenue variance by region and business unit
SELECT
    month,
    region,
    business_unit,
    budget_revenue,
    actual_revenue,
    revenue_variance,
    revenue_variance_pct
FROM revenue_variance_report
ORDER BY month, revenue_variance ASC;


-- 5. Monthly margin trend
SELECT
    month,
    gross_margin_pct,
    ebitda_margin_pct,
    actual_revenue,
    actual_ebitda
FROM monthly_financial_summary
ORDER BY month;


-- 6. Highest department overspend overall
SELECT
    department,
    cost_center,
    SUM(opex_variance) AS total_opex_variance,
    AVG(opex_variance_pct) AS avg_opex_variance_pct
FROM department_variance_report
WHERE overspend_flag = TRUE
GROUP BY department, cost_center
ORDER BY total_opex_variance DESC;


-- 7. Revenue shortfall by region
SELECT
    region,
    SUM(budget_revenue) AS total_budget_revenue,
    SUM(actual_revenue) AS total_actual_revenue,
    SUM(revenue_variance) AS total_revenue_variance,
    SUM(actual_revenue) - SUM(budget_revenue) AS variance_check
FROM revenue_variance_report
GROUP BY region
ORDER BY total_revenue_variance ASC;