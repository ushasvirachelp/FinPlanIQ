import duckdb
import pandas as pd

from src.config import DUCKDB_PATH


def query_df(sql):
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as connection:
        return connection.execute(sql).fetchdf()


def get_monthly_summary():
    return query_df(
        """
        SELECT *
        FROM monthly_financial_summary
        ORDER BY month;
        """
    )


def get_latest_kpis():
    latest = query_df(
        """
        SELECT *
        FROM v_latest_month;
        """
    )

    if latest.empty:
        return {}

    row = latest.iloc[0]

    return {
        "month": row["month"],
        "total_revenue": row["actual_revenue"],
        "budget_revenue": row["budget_revenue"],
        "revenue_variance": row["revenue_variance"],
        "revenue_variance_pct": row["revenue_variance_pct"],
        "actual_opex": row["actual_opex"],
        "opex_variance": row["opex_variance"],
        "opex_variance_pct": row["opex_variance_pct"],
        "gross_margin_pct": row["gross_margin_pct"],
        "actual_ebitda": row["actual_ebitda"],
        "ebitda_margin_pct": row["ebitda_margin_pct"],
        "ebitda_variance": row["ebitda_variance"],
    }


def get_top_drivers(limit=5):
    return query_df(
        f"""
        SELECT *
        FROM variance_drivers
        WHERE month = (
            SELECT MAX(month)
            FROM variance_drivers
        )
        ORDER BY unfavorable_amount DESC
        LIMIT {limit};
        """
    )


def get_department_variance():
    return query_df(
        """
        SELECT *
        FROM department_variance_report
        ORDER BY month, department;
        """
    )


def get_revenue_variance():
    return query_df(
        """
        SELECT *
        FROM revenue_variance_report
        ORDER BY month, region, business_unit;
        """
    )