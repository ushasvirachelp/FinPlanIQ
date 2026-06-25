from io import BytesIO

import pandas as pd


REVENUE_REQUIRED_COLUMNS = [
    "month",
    "region",
    "business_unit",
    "budget_revenue",
    "actual_revenue",
    "budget_cogs",
    "actual_cogs",
]

OPEX_REQUIRED_COLUMNS = [
    "month",
    "department",
    "cost_center",
    "budget_headcount",
    "actual_headcount",
    "budget_payroll",
    "actual_payroll",
    "budget_other_opex",
    "actual_other_opex",
]

REVENUE_NUMERIC_COLUMNS = [
    "budget_revenue",
    "actual_revenue",
    "budget_cogs",
    "actual_cogs",
]

OPEX_NUMERIC_COLUMNS = [
    "budget_headcount",
    "actual_headcount",
    "budget_payroll",
    "actual_payroll",
    "budget_other_opex",
    "actual_other_opex",
]


def normalize_column_name(column):
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
    )


def normalize_columns(df):
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def safe_divide(numerator, denominator):
    denominator = denominator.replace(0, pd.NA)
    return (numerator / denominator).fillna(0)


def round_numeric(df, decimals=4):
    df = df.copy()
    numeric_columns = df.select_dtypes(include="number").columns
    df[numeric_columns] = df[numeric_columns].round(decimals)
    return df


def validate_required_columns(df, required_columns, table_name):
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"{table_name} is missing required columns: {', '.join(missing_columns)}"
        )


def validate_numeric_columns(df, numeric_columns, table_name):
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

        if df[column].isna().any():
            raise ValueError(
                f"{table_name} has non-numeric or blank values in column: {column}"
            )

        if (df[column] < 0).any():
            raise ValueError(
                f"{table_name} has negative values in column: {column}"
            )

    return df


def standardize_month_column(df, table_name):
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"], errors="coerce")

    if df["month"].isna().any():
        raise ValueError(
            f"{table_name} has invalid month values. Use dates like 2025-01-01 or Jan 2025."
        )

    df["month"] = df["month"].dt.to_period("M").dt.to_timestamp()

    return df


def find_sheet_name(excel_file, expected_name):
    normalized_expected = normalize_column_name(expected_name)

    for sheet_name in excel_file.sheet_names:
        if normalize_column_name(sheet_name) == normalized_expected:
            return sheet_name

    raise ValueError(
        f"Missing required sheet: {expected_name}. "
        f"Workbook must include sheets named Revenue_COGS and Opex_Headcount."
    )


def read_uploaded_workbook(uploaded_file):
    excel_file = pd.ExcelFile(uploaded_file)

    revenue_sheet = find_sheet_name(excel_file, "Revenue_COGS")
    opex_sheet = find_sheet_name(excel_file, "Opex_Headcount")

    revenue_cogs = pd.read_excel(uploaded_file, sheet_name=revenue_sheet)
    opex_headcount = pd.read_excel(uploaded_file, sheet_name=opex_sheet)

    revenue_cogs = normalize_columns(revenue_cogs)
    opex_headcount = normalize_columns(opex_headcount)

    validate_required_columns(
        revenue_cogs,
        REVENUE_REQUIRED_COLUMNS,
        "Revenue_COGS",
    )

    validate_required_columns(
        opex_headcount,
        OPEX_REQUIRED_COLUMNS,
        "Opex_Headcount",
    )

    revenue_cogs = revenue_cogs[REVENUE_REQUIRED_COLUMNS].copy()
    opex_headcount = opex_headcount[OPEX_REQUIRED_COLUMNS].copy()

    revenue_cogs = standardize_month_column(revenue_cogs, "Revenue_COGS")
    opex_headcount = standardize_month_column(opex_headcount, "Opex_Headcount")

    revenue_cogs = validate_numeric_columns(
        revenue_cogs,
        REVENUE_NUMERIC_COLUMNS,
        "Revenue_COGS",
    )

    opex_headcount = validate_numeric_columns(
        opex_headcount,
        OPEX_NUMERIC_COLUMNS,
        "Opex_Headcount",
    )

    revenue_cogs = (
        revenue_cogs
        .groupby(["month", "region", "business_unit"], as_index=False)[
            REVENUE_NUMERIC_COLUMNS
        ]
        .sum()
    )

    opex_headcount = (
        opex_headcount
        .groupby(["month", "department", "cost_center"], as_index=False)[
            OPEX_NUMERIC_COLUMNS
        ]
        .sum()
    )

    return revenue_cogs, opex_headcount


def build_monthly_financial_summary(revenue_cogs, opex_headcount):
    revenue_summary = (
        revenue_cogs
        .groupby("month", as_index=False)[
            ["budget_revenue", "actual_revenue", "budget_cogs", "actual_cogs"]
        ]
        .sum()
    )

    opex = opex_headcount.copy()
    opex["budget_opex"] = opex["budget_payroll"] + opex["budget_other_opex"]
    opex["actual_opex"] = opex["actual_payroll"] + opex["actual_other_opex"]

    opex_summary = (
        opex
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

    summary["revenue_variance_pct"] = safe_divide(
        summary["revenue_variance"],
        summary["budget_revenue"],
    )

    summary["opex_variance_pct"] = safe_divide(
        summary["opex_variance"],
        summary["budget_opex"],
    )

    summary["gross_margin_pct"] = safe_divide(
        summary["actual_gross_profit"],
        summary["actual_revenue"],
    )

    summary["ebitda_margin_pct"] = safe_divide(
        summary["actual_ebitda"],
        summary["actual_revenue"],
    )

    return round_numeric(summary, 4)


def build_department_variance_report(opex_headcount):
    report = opex_headcount.copy()

    report["budget_opex"] = report["budget_payroll"] + report["budget_other_opex"]
    report["actual_opex"] = report["actual_payroll"] + report["actual_other_opex"]

    report["opex_variance"] = report["actual_opex"] - report["budget_opex"]
    report["opex_variance_pct"] = safe_divide(
        report["opex_variance"],
        report["budget_opex"],
    )

    report["headcount_variance"] = (
        report["actual_headcount"] - report["budget_headcount"]
    )

    report["overspend_flag"] = report["opex_variance"] > 0

    columns = [
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

    return round_numeric(report[columns], 4)


def build_revenue_variance_report(revenue_cogs):
    report = revenue_cogs.copy()

    report["revenue_variance"] = report["actual_revenue"] - report["budget_revenue"]
    report["revenue_variance_pct"] = safe_divide(
        report["revenue_variance"],
        report["budget_revenue"],
    )

    report["gross_profit"] = report["actual_revenue"] - report["actual_cogs"]
    report["gross_margin_pct"] = safe_divide(
        report["gross_profit"],
        report["actual_revenue"],
    )

    report["under_budget_flag"] = report["revenue_variance"] < 0

    return round_numeric(report, 4)


def build_variance_drivers(revenue_report, department_report):
    revenue_drivers = revenue_report.copy()

    revenue_drivers["driver_type"] = "Revenue Shortfall"
    revenue_drivers["driver_category"] = (
        revenue_drivers["region"] + " / " + revenue_drivers["business_unit"]
    )

    revenue_drivers["unfavorable_amount"] = revenue_drivers["revenue_variance"].apply(
        lambda value: abs(value) if value < 0 else 0
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
        lambda value: value if value > 0 else 0
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
        ascending=[True, False],
    )

    drivers["rank_in_month"] = drivers.groupby("month")["unfavorable_amount"].rank(
        method="first",
        ascending=False,
    )

    return round_numeric(drivers, 2)


def process_uploaded_workbook(uploaded_file):
    revenue_cogs, opex_headcount = read_uploaded_workbook(uploaded_file)

    monthly_summary = build_monthly_financial_summary(revenue_cogs, opex_headcount)
    department_report = build_department_variance_report(opex_headcount)
    revenue_report = build_revenue_variance_report(revenue_cogs)
    variance_drivers = build_variance_drivers(revenue_report, department_report)

    return {
        "monthly": monthly_summary,
        "departments": department_report,
        "revenue": revenue_report,
        "drivers": variance_drivers,
    }


def build_upload_template():
    revenue_sample = pd.DataFrame(
        [
            {
                "month": "2025-01-01",
                "region": "North America",
                "business_unit": "Enterprise Subscription",
                "budget_revenue": 1200000,
                "actual_revenue": 1165000,
                "budget_cogs": 300000,
                "actual_cogs": 296000,
            },
            {
                "month": "2025-01-01",
                "region": "Europe",
                "business_unit": "SMB Subscription",
                "budget_revenue": 550000,
                "actual_revenue": 575000,
                "budget_cogs": 154000,
                "actual_cogs": 160000,
            },
            {
                "month": "2025-02-01",
                "region": "North America",
                "business_unit": "Enterprise Subscription",
                "budget_revenue": 1230000,
                "actual_revenue": 1280000,
                "budget_cogs": 307500,
                "actual_cogs": 320000,
            },
            {
                "month": "2025-02-01",
                "region": "Europe",
                "business_unit": "SMB Subscription",
                "budget_revenue": 565000,
                "actual_revenue": 540000,
                "budget_cogs": 158200,
                "actual_cogs": 151000,
            },
        ]
    )

    opex_sample = pd.DataFrame(
        [
            {
                "month": "2025-01-01",
                "department": "Sales",
                "cost_center": "Revenue Operations",
                "budget_headcount": 40,
                "actual_headcount": 41,
                "budget_payroll": 420000,
                "actual_payroll": 432000,
                "budget_other_opex": 95000,
                "actual_other_opex": 102000,
            },
            {
                "month": "2025-01-01",
                "department": "Marketing",
                "cost_center": "Growth Marketing",
                "budget_headcount": 24,
                "actual_headcount": 24,
                "budget_payroll": 235000,
                "actual_payroll": 238000,
                "budget_other_opex": 260000,
                "actual_other_opex": 285000,
            },
            {
                "month": "2025-02-01",
                "department": "Sales",
                "cost_center": "Revenue Operations",
                "budget_headcount": 40,
                "actual_headcount": 40,
                "budget_payroll": 420000,
                "actual_payroll": 418000,
                "budget_other_opex": 96000,
                "actual_other_opex": 93000,
            },
            {
                "month": "2025-02-01",
                "department": "Marketing",
                "cost_center": "Growth Marketing",
                "budget_headcount": 24,
                "actual_headcount": 25,
                "budget_payroll": 235000,
                "actual_payroll": 248000,
                "budget_other_opex": 265000,
                "actual_other_opex": 292000,
            },
        ]
    )

    instructions = pd.DataFrame(
        [
            {
                "Sheet": "Revenue_COGS",
                "Purpose": "Revenue and direct cost data by month, region, and business unit.",
                "Required": "Yes",
            },
            {
                "Sheet": "Opex_Headcount",
                "Purpose": "Department operating expense and headcount data by month.",
                "Required": "Yes",
            },
            {
                "Sheet": "Instructions",
                "Purpose": "Keep the column names exactly as shown in the sample sheets.",
                "Required": "No",
            },
        ]
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        instructions.to_excel(writer, sheet_name="Instructions", index=False)
        revenue_sample.to_excel(writer, sheet_name="Revenue_COGS", index=False)
        opex_sample.to_excel(writer, sheet_name="Opex_Headcount", index=False)

        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))

                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 35)

    output.seek(0)
    return output