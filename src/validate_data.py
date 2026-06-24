import pandas as pd

from config import RAW_DIR, PROCESSED_DIR

def check_file_exists(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")


def check_no_nulls(df, table_name, key_columns):
    null_counts = df[key_columns].isnull().sum()
    failed = null_counts[null_counts > 0]

    if not failed.empty:
        raise ValueError(f"{table_name} has nulls in key columns: {failed.to_dict()}")


def check_no_negative_values(df, table_name, numeric_columns):
    for column in numeric_columns:
        if (df[column] < 0).any():
            raise ValueError(f"{table_name} has negative values in {column}")


def validate_raw_files():
    raw_files = [
        "dim_date.csv",
        "dim_department.csv",
        "dim_region.csv",
        "dim_business_unit.csv",
        "fact_revenue_cogs.csv",
        "fact_opex_headcount.csv",
    ]

    for filename in raw_files:
        check_file_exists(RAW_DIR / filename)


def validate_processed_files():
    processed_files = [
        "monthly_financial_summary.csv",
        "department_variance_report.csv",
        "revenue_variance_report.csv",
        "variance_drivers.csv",
    ]

    for filename in processed_files:
        check_file_exists(PROCESSED_DIR / filename)


def validate_monthly_summary():
    df = pd.read_csv(PROCESSED_DIR / "monthly_financial_summary.csv")

    check_no_nulls(
        df,
        "monthly_financial_summary",
        ["month", "actual_revenue", "actual_opex", "actual_ebitda"]
    )

    check_no_negative_values(
        df,
        "monthly_financial_summary",
        ["actual_revenue", "actual_cogs", "actual_opex"]
    )

    expected_months = 36
    if len(df) != expected_months:
        raise ValueError(
            f"monthly_financial_summary expected {expected_months} rows, found {len(df)}"
        )


def validate_department_report():
    df = pd.read_csv(PROCESSED_DIR / "department_variance_report.csv")

    check_no_nulls(
        df,
        "department_variance_report",
        ["month", "department", "budget_opex", "actual_opex"]
    )

    expected_rows = 36 * 6
    if len(df) != expected_rows:
        raise ValueError(
            f"department_variance_report expected {expected_rows} rows, found {len(df)}"
        )


def validate_revenue_report():
    df = pd.read_csv(PROCESSED_DIR / "revenue_variance_report.csv")

    check_no_nulls(
        df,
        "revenue_variance_report",
        ["month", "region", "business_unit", "actual_revenue"]
    )

    expected_rows = 36 * 4 * 4
    if len(df) != expected_rows:
        raise ValueError(
            f"revenue_variance_report expected {expected_rows} rows, found {len(df)}"
        )


def main():
    validate_raw_files()
    validate_processed_files()
    validate_monthly_summary()
    validate_department_report()
    validate_revenue_report()

    print("All FinPlanIQ data validation checks passed.")


if __name__ == "__main__":
    main()