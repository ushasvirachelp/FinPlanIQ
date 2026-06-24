import sys
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import DUCKDB_PATH
from src.executive_summary import generate_executive_summary
from src.forecasting import build_simple_forecast
from src.scenario_analysis import apply_scenario, build_revenue_downside_table


st.set_page_config(
    page_title="FinPlanIQ",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def query_df(sql):
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as connection:
        return connection.execute(sql).fetchdf()


def format_money(value):
    value = float(value)

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"

    return f"${value:,.0f}"


def format_pct(value):
    return f"{float(value) * 100:.1f}%"


def load_tables():
    monthly = query_df("SELECT * FROM monthly_financial_summary ORDER BY month")
    departments = query_df("SELECT * FROM department_variance_report ORDER BY month, department")
    revenue = query_df("SELECT * FROM revenue_variance_report ORDER BY month, region, business_unit")
    drivers = query_df("SELECT * FROM variance_drivers ORDER BY month, rank_in_month")

    return monthly, departments, revenue, drivers


def render_kpi_cards(latest):
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Revenue",
        format_money(latest["actual_revenue"]),
        format_money(latest["revenue_variance"])
    )

    col2.metric(
        "Revenue Variance %",
        format_pct(latest["revenue_variance_pct"])
    )

    col3.metric(
        "Gross Margin %",
        format_pct(latest["gross_margin_pct"])
    )

    col4.metric(
        "EBITDA",
        format_money(latest["actual_ebitda"]),
        format_money(latest["ebitda_variance"])
    )

    col5.metric(
        "EBITDA Margin",
        format_pct(latest["ebitda_margin_pct"])
    )


def executive_summary_page(monthly, drivers):
    st.title("FinPlanIQ")
    st.caption("FP&A dashboard for budget vs actuals, variance analysis, forecasting, and scenario planning.")

    latest = monthly.sort_values("month").iloc[-1]
    render_kpi_cards(latest)

    latest_month = latest["month"]
    latest_drivers = drivers[drivers["month"] == latest_month]

    st.subheader("Executive Summary")
    st.info(generate_executive_summary(monthly, latest_drivers))

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            monthly,
            x="month",
            y=["actual_revenue", "budget_revenue"],
            title="Revenue: Actual vs Budget"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            monthly,
            x="month",
            y=["actual_ebitda", "budget_ebitda"],
            title="EBITDA: Actual vs Budget"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Unfavorable Variance Drivers")
    st.dataframe(
        latest_drivers.sort_values("unfavorable_amount", ascending=False).head(10),
        use_container_width=True
    )


def budget_actuals_page(monthly):
    st.title("Budget vs Actuals")

    metric = st.selectbox(
        "Select financial line item",
        ["Revenue", "COGS", "Operating Expenses", "EBITDA"]
    )

    column_map = {
        "Revenue": ("actual_revenue", "budget_revenue"),
        "COGS": ("actual_cogs", "budget_cogs"),
        "Operating Expenses": ("actual_opex", "budget_opex"),
        "EBITDA": ("actual_ebitda", "budget_ebitda"),
    }

    actual_col, budget_col = column_map[metric]

    fig = px.bar(
        monthly,
        x="month",
        y=[actual_col, budget_col],
        barmode="group",
        title=f"{metric}: Actual vs Budget"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        monthly[["month", budget_col, actual_col]],
        use_container_width=True
    )


def department_page(departments):
    st.title("Department / Cost Center Analysis")

    latest_month = departments["month"].max()
    latest = departments[departments["month"] == latest_month]

    fig = px.bar(
        latest.sort_values("opex_variance", ascending=False),
        x="department",
        y="opex_variance",
        color="overspend_flag",
        title="Latest Month Department Variance"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        latest.sort_values("opex_variance", ascending=False),
        use_container_width=True
    )


def trends_page(monthly, revenue):
    st.title("Revenue & Expense Trends")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            monthly,
            x="month",
            y=["actual_revenue", "actual_opex"],
            title="Revenue and Operating Expense Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            monthly,
            x="month",
            y=["gross_margin_pct", "ebitda_margin_pct"],
            title="Gross Margin and EBITDA Margin Trend"
        )
        st.plotly_chart(fig, use_container_width=True)

    revenue_by_region = (
        revenue
        .groupby(["month", "region"], as_index=False)["actual_revenue"]
        .sum()
    )

    fig = px.line(
        revenue_by_region,
        x="month",
        y="actual_revenue",
        color="region",
        title="Revenue by Region"
    )

    st.plotly_chart(fig, use_container_width=True)


def forecasting_page(monthly):
    st.title("Forecasting")

    months_ahead = st.slider(
        "Forecast months",
        min_value=3,
        max_value=12,
        value=6
    )

    forecast = build_simple_forecast(monthly, months_ahead)

    fig = px.line(
        forecast,
        x="month",
        y=["forecast_revenue", "forecast_ebitda"],
        title="Rolling Forecast"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(forecast, use_container_width=True)


def scenario_page(monthly):
    st.title("Scenario Analysis")

    latest = monthly.sort_values("month").iloc[-1]

    col1, col2, col3 = st.columns(3)

    revenue_drop = col1.selectbox(
        "Revenue drop",
        [0.00, 0.05, 0.10, 0.15],
        format_func=lambda value: f"{int(value * 100)}%"
    )

    payroll_increase = col2.slider(
        "Payroll increase %",
        min_value=0,
        max_value=15,
        value=8
    ) / 100

    marketing_change = col3.slider(
        "Marketing spend change %",
        min_value=-25,
        max_value=25,
        value=0
    ) / 100

    result = apply_scenario(
        latest,
        revenue_drop_pct=revenue_drop,
        payroll_increase_pct=payroll_increase,
        marketing_change_pct=marketing_change
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Scenario Revenue", format_money(result["scenario_revenue"]))
    kpi2.metric("Scenario EBITDA", format_money(result["scenario_ebitda"]), format_money(result["ebitda_impact"]))
    kpi3.metric("EBITDA Margin", format_pct(result["scenario_ebitda_margin_pct"]))
    kpi4.metric("Margin Impact", f"{result['margin_impact_pp']} pp")

    st.subheader("Standard Downside Cases")
    st.dataframe(
        build_revenue_downside_table(latest),
        use_container_width=True
    )


def variance_driver_page(drivers):
    st.title("Variance Driver Explanation")

    selected_month = st.selectbox(
        "Select month",
        sorted(drivers["month"].unique(), reverse=True)
    )

    filtered = (
        drivers[drivers["month"] == selected_month]
        .sort_values("unfavorable_amount", ascending=False)
        .head(15)
    )

    fig = px.bar(
        filtered,
        x="unfavorable_amount",
        y="driver_category",
        color="driver_type",
        orientation="h",
        title="Top Unfavorable Variance Drivers"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(filtered, use_container_width=True)


def main():
    monthly, departments, revenue, drivers = load_tables()

    page = st.sidebar.radio(
        "Dashboard Page",
        [
            "Executive Summary",
            "Budget vs Actuals",
            "Department Analysis",
            "Revenue & Expense Trends",
            "Forecasting",
            "Scenario Analysis",
            "Variance Drivers",
        ]
    )

    if page == "Executive Summary":
        executive_summary_page(monthly, drivers)
    elif page == "Budget vs Actuals":
        budget_actuals_page(monthly)
    elif page == "Department Analysis":
        department_page(departments)
    elif page == "Revenue & Expense Trends":
        trends_page(monthly, revenue)
    elif page == "Forecasting":
        forecasting_page(monthly)
    elif page == "Scenario Analysis":
        scenario_page(monthly)
    elif page == "Variance Drivers":
        variance_driver_page(drivers)


if __name__ == "__main__":
    main()