import numpy as np
import pandas as pd

from config import (
    RAW_DIR,
    START_MONTH,
    END_MONTH,
    RANDOM_SEED,
    DEPARTMENTS,
    REGIONS,
    BUSINESS_UNITS,
)


def create_months():
    return pd.date_range(start=START_MONTH, end=END_MONTH, freq="MS")


def save_csv(df, filename):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DIR / filename, index=False)


def generate_dimensions(months):
    dim_date = pd.DataFrame({
        "month": months,
        "year": months.year,
        "quarter": "Q" + (((months.month - 1) // 3) + 1).astype(str),
        "month_name": months.strftime("%b"),
    })

    save_csv(dim_date, "dim_date.csv")
    save_csv(pd.DataFrame(DEPARTMENTS), "dim_department.csv")
    save_csv(pd.DataFrame(REGIONS), "dim_region.csv")
    save_csv(pd.DataFrame(BUSINESS_UNITS), "dim_business_unit.csv")


def generate_revenue_and_cogs(months, rng):
    rows = []

    base_revenue = {
        "Enterprise Subscription": 950_000,
        "SMB Subscription": 575_000,
        "Professional Services": 310_000,
        "Data & Insights": 225_000,
    }

    region_multiplier = {
        "North America": 1.00,
        "Europe": 0.55,
        "APAC": 0.35,
        "LATAM": 0.22,
    }

    cogs_rate = {
        "Enterprise Subscription": 0.24,
        "SMB Subscription": 0.28,
        "Professional Services": 0.45,
        "Data & Insights": 0.32,
    }

    for month_number, month in enumerate(months):
        growth = 1 + (month_number * 0.012)

        for region in REGIONS:
            for bu in BUSINESS_UNITS:
                business_unit = bu["business_unit"]
                region_name = region["region"]

                budget_revenue = (
                    base_revenue[business_unit]
                    * region_multiplier[region_name]
                    * growth
                )

                actual_revenue = budget_revenue * rng.normal(1.0, 0.06)

                if month.year == 2025 and month.month in [7, 8, 9]:
                    actual_revenue *= 0.94

                budget_cogs = budget_revenue * cogs_rate[business_unit]
                actual_cogs = actual_revenue * cogs_rate[business_unit] * rng.normal(1.0, 0.03)

                rows.append({
                    "month": month,
                    "region": region_name,
                    "business_unit": business_unit,
                    "budget_revenue": round(budget_revenue, 2),
                    "actual_revenue": round(actual_revenue, 2),
                    "budget_cogs": round(budget_cogs, 2),
                    "actual_cogs": round(actual_cogs, 2),
                })

    save_csv(pd.DataFrame(rows), "fact_revenue_cogs.csv")


def generate_opex_and_headcount(months, rng):
    rows = []

    base_headcount = {
        "Sales": 40,
        "Marketing": 24,
        "Engineering": 65,
        "Product": 22,
        "Customer Success": 36,
        "G&A": 26,
    }

    avg_salary = {
        "Sales": 10500,
        "Marketing": 9800,
        "Engineering": 13800,
        "Product": 12600,
        "Customer Success": 8700,
        "G&A": 10300,
    }

    other_expense = {
        "Sales": 95000,
        "Marketing": 260000,
        "Engineering": 190000,
        "Product": 70000,
        "Customer Success": 52000,
        "G&A": 165000,
    }

    for month_number, month in enumerate(months):
        for dept in DEPARTMENTS:
            department = dept["department"]

            budget_headcount = base_headcount[department] + int(month_number / 8)
            actual_headcount = budget_headcount + rng.choice([-1, 0, 0, 1])

            budget_payroll = budget_headcount * avg_salary[department]
            actual_payroll = actual_headcount * avg_salary[department] * rng.normal(1.02, 0.03)

            budget_other = other_expense[department] * (1 + month_number * 0.004)
            actual_other = budget_other * rng.normal(1.0, 0.07)

            if department == "Marketing" and month.year == 2025 and month.month in [3, 4, 5]:
                actual_other *= 1.18

            if department == "Engineering" and month.year == 2025 and month.month >= 8:
                actual_other *= 1.14

            rows.append({
                "month": month,
                "department": department,
                "cost_center": dept["cost_center"],
                "budget_headcount": budget_headcount,
                "actual_headcount": actual_headcount,
                "budget_payroll": round(budget_payroll, 2),
                "actual_payroll": round(actual_payroll, 2),
                "budget_other_opex": round(budget_other, 2),
                "actual_other_opex": round(actual_other, 2),
            })

    save_csv(pd.DataFrame(rows), "fact_opex_headcount.csv")


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    months = create_months()

    generate_dimensions(months)
    generate_revenue_and_cogs(months, rng)
    generate_opex_and_headcount(months, rng)

    print("FinPlanIQ raw financial datasets created successfully.")
    print(f"Files saved in: {RAW_DIR}")


if __name__ == "__main__":
    main()