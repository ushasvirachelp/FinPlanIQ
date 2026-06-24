import pandas as pd

from config import RAW_DIR, PROCESSED_DIR


def safe_pct(numerator, denominator):
    if denominator == 0:
        return 0
    return numerator / denominator


def load_raw_data():
    revenue_cogs = pd.read_csv(RAW_DIR / "fact_revenue_cogs.csv", parse_dates=["month"])
    opex_headcount = pd.read_csv(RAW_DIR / "fact_opex_headcount.csv", parse_dates=["month"])

    return revenue_cogs, opex_headcount


def build_monthly_financial_summary(revenue_cogs, opex_headcount):
    revenue_summary = (
        revenue_cogs
        .groupby("month", as_index=False)[
            ["budget_revenue", "actual_revenue", "budget_cogs", "actual_cogs"]
        ]
        .sum()
    )

    opex_headcount["budget_opex"] = (
        opex_headcount["budget_payroll"] + opex_headcount["budget_other_opex"]
    )

    opex_headcount["actual_opex"] = (
        opex_headcount["actual_payroll"] + opex_headcount["actual_other_opex"]
    )

    opex_summary = (
        opex_headcount
        .groupby("month", as_index=False)[["budget_opex", "actual_opex"]]
        .sum()
    )

    summary = revenue_summary.merge(opex_summary, on="month", how="left")

    summary["budget_gross_profit"] = summary["budget_revenue"] - summary["budget_cogs"]
    summary["actual_gross_profit"] = summary["actual_revenue"] - summary["actual_cogs"]

    summary["budget_ebitda"] = summary["budget_gross_profit"] - summary["budget_opex"]
    summary["actual_ebitda"] = summary["actual_gross_profit"] - summary["actual_opex"]

    summary["revenue_variance"] = summary["actual_revenue"] - summary["budget_revenue"]
    summary["opex_variance"] = summary["actual_opex"] - summary["budget_opex"]
    summary["ebitda_variance"] = summary["actual_ebitda"] - summary["budget_ebitda"]

    summary["revenue_variance_pct"] = summary.apply(
        lambda row: safe_pct(row["revenue_variance"], row["budget_revenue"]),
        axis=1
    )

    summary["opex_variance_pct"] = summary.apply(
        lambda row: safe_pct(row["opex_variance"], row["budget_opex"]),
        axis=1
    )

    summary["gross_margin_pct"] = summary.apply(
        lambda row: safe_pct(row["actual_gross_profit"], row["actual_revenue"]),
        axis=1
    )

    summary["ebitda_margin_pct"] = summary.apply(
        lambda row: safe_pct(row["actual_ebitda"], row["actual_revenue"]),
        axis=1
    )

    return summary.round(4)


def build_department_variance_report(opex_headcount):
    report = opex_headcount.copy()

    report["budget_opex"] = report["budget_payroll"] + report["budget_other_opex"]
    report["actual_opex"] = report["actual_payroll"] + report["actual_other_opex"]

    report["opex_variance"] = report["actual_opex"] - report["budget_opex"]
    report["opex_variance_pct"] = report.apply(
        lambda row: safe_pct(row["opex_variance"], row["budget_opex"]),
        axis=1
    )

    report["headcount_variance"] = report["actual_headcount"] - report["budget_headcount"]
    report["overspend_flag"] = report["opex_variance"] > 0

    return report[
        [
            "month",
            "department",
            "cost_center",
            "budget_headcount",
            "actual_headcount",
            "headcount_variance",
            "budget_opex",
            "actual_opex",
            "opex_variance",
            "opex_variance_pct",
            "overspend_flag",
        ]
    ].round(4)


def build_revenue_variance_report(revenue_cogs):
    report = revenue_cogs.copy()

    report["revenue_variance"] = report["actual_revenue"] - report["budget_revenue"]
    report["revenue_variance_pct"] = report.apply(
        lambda row: safe_pct(row["revenue_variance"], row["budget_revenue"]),
        axis=1
    )

    report["gross_profit"] = report["actual_revenue"] - report["actual_cogs"]
    report["gross_margin_pct"] = report.apply(
        lambda row: safe_pct(row["gross_profit"], row["actual_revenue"]),
        axis=1
    )

    report["under_budget_flag"] = report["revenue_variance"] < 0

    return report.round(4)


def build_variance_drivers(revenue_report, department_report):
    revenue_drivers = revenue_report.copy()
    revenue_drivers["driver_type"] = "Revenue Shortfall"
    revenue_drivers["driver_category"] = (
        revenue_drivers["region"] + " / " + revenue_drivers["business_unit"]
    )
    revenue_drivers["unfavorable_amount"] = revenue_drivers["revenue_variance"].apply(
        lambda x: abs(x) if x < 0 else 0
    )
    revenue_drivers["explanation"] = (
        "Revenue came in below budget for "
        + revenue_drivers["region"]
        + " - "
        + revenue_drivers["business_unit"]
    )

    revenue_drivers = revenue_drivers[
        [
            "month",
            "driver_type",
            "driver_category",
            "unfavorable_amount",
            "explanation",
        ]
    ]

    expense_drivers = department_report.copy()
    expense_drivers["driver_type"] = "Expense Overspend"
    expense_drivers["driver_category"] = (
        expense_drivers["department"] + " / " + expense_drivers["cost_center"]
    )
    expense_drivers["unfavorable_amount"] = expense_drivers["opex_variance"].apply(
        lambda x: x if x > 0 else 0
    )
    expense_drivers["explanation"] = (
        expense_drivers["department"]
        + " overspent budget in "
        + expense_drivers["cost_center"]
    )

    expense_drivers = expense_drivers[
        [
            "month",
            "driver_type",
            "driver_category",
            "unfavorable_amount",
            "explanation",
        ]
    ]

    drivers = pd.concat([revenue_drivers, expense_drivers], ignore_index=True)
    drivers = drivers[drivers["unfavorable_amount"] > 0]

    drivers = drivers.sort_values(
        ["month", "unfavorable_amount"],
        ascending=[True, False]
    )

    drivers["rank_in_month"] = drivers.groupby("month")["unfavorable_amount"].rank(
        method="first",
        ascending=False
    )

    return drivers.round(2)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    revenue_cogs, opex_headcount = load_raw_data()

    monthly_summary = build_monthly_financial_summary(revenue_cogs, opex_headcount)
    department_report = build_department_variance_report(opex_headcount)
    revenue_report = build_revenue_variance_report(revenue_cogs)
    variance_drivers = build_variance_drivers(revenue_report, department_report)

    monthly_summary.to_csv(PROCESSED_DIR / "monthly_financial_summary.csv", index=False)
    department_report.to_csv(PROCESSED_DIR / "department_variance_report.csv", index=False)
    revenue_report.to_csv(PROCESSED_DIR / "revenue_variance_report.csv", index=False)
    variance_drivers.to_csv(PROCESSED_DIR / "variance_drivers.csv", index=False)

    print("Processed FP&A reporting tables created successfully.")
    print(f"Files saved in: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()