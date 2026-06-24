import html
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


CHART_TEMPLATE = "plotly_white"

FINANCE_COLORS = {
    "actual": "#1F7A4D",
    "budget": "#64748B",
    "unfavorable": "#DC2626",
    "favorable": "#16A34A",
    "neutral": "#2563EB",
}


st.set_page_config(
    page_title="FinPlanIQ",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #F7F9FB;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #111827;
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #6B7280;
        font-size: 14px;
    }

    [data-testid="stMetricValue"] {
        color: #111827;
        font-size: 26px;
        font-weight: 700;
    }

    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 10px;
    }

    .dashboard-header {
        background: linear-gradient(135deg, #0F172A 0%, #1F7A4D 100%);
        padding: 28px;
        border-radius: 14px;
        margin-bottom: 24px;
    }

    .dashboard-header h1 {
        color: #FFFFFF;
        margin-bottom: 4px;
    }

    .dashboard-header p {
        color: #D1FAE5;
        font-size: 16px;
        margin-bottom: 0;
    }

    .summary-box {
        background-color: #FFFFFF;
        border: 1px solid #D1FAE5;
        border-left: 6px solid #1F7A4D;
        padding: 18px 22px;
        border-radius: 10px;
        color: #111827;
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
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


def render_page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="dashboard-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_tables():
    monthly = query_df("SELECT * FROM monthly_financial_summary ORDER BY month")
    departments = query_df("SELECT * FROM department_variance_report ORDER BY month, department")
    revenue = query_df("SELECT * FROM revenue_variance_report ORDER BY month, region, business_unit")
    drivers = query_df("SELECT * FROM variance_drivers ORDER BY month, rank_in_month")

    return monthly, departments, revenue, drivers


def render_global_filters(monthly, departments, revenue):
    st.sidebar.markdown("## Filters")

    available_months = sorted(monthly["month"].unique(), reverse=True)

    selected_month = st.sidebar.selectbox(
        "Month",
        available_months,
        format_func=lambda value: pd.to_datetime(value).strftime("%b %Y"),
    )

    selected_region = st.sidebar.selectbox(
        "Region",
        ["All"] + sorted(revenue["region"].unique().tolist()),
    )

    selected_business_unit = st.sidebar.selectbox(
        "Business Unit",
        ["All"] + sorted(revenue["business_unit"].unique().tolist()),
    )

    selected_department = st.sidebar.selectbox(
        "Department",
        ["All"] + sorted(departments["department"].unique().tolist()),
    )

    return selected_month, selected_region, selected_business_unit, selected_department


def render_kpi_cards(latest):
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Revenue", format_money(latest["actual_revenue"]), format_money(latest["revenue_variance"]))
    col2.metric("Revenue Variance %", format_pct(latest["revenue_variance_pct"]))
    col3.metric("Gross Margin %", format_pct(latest["gross_margin_pct"]))
    col4.metric("EBITDA", format_money(latest["actual_ebitda"]), format_money(latest["ebitda_variance"]))
    col5.metric("EBITDA Margin", format_pct(latest["ebitda_margin_pct"]))


def executive_summary_page(monthly, drivers, selected_month):
    render_page_header(
        "FinPlanIQ",
        "Monthly FP&A performance review for budget vs actuals, variance analysis, forecasting, and scenario planning.",
    )

    selected_monthly = monthly[monthly["month"] == selected_month]

    if selected_monthly.empty:
        st.warning("No data available for the selected month.")
        return

    latest = selected_monthly.iloc[0]
    latest_drivers = drivers[drivers["month"] == selected_month]
    monthly_chart = monthly[monthly["month"] <= selected_month]

    render_kpi_cards(latest)

    summary_text = generate_executive_summary(selected_monthly, latest_drivers)

    st.subheader("Executive Summary")
    st.markdown(
        f"""
        <div class="summary-box">
            {html.escape(summary_text)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            monthly_chart,
            x="month",
            y=["actual_revenue", "budget_revenue"],
            title="Revenue: Actual vs Budget",
            template=CHART_TEMPLATE,
            color_discrete_map={
                "actual_revenue": FINANCE_COLORS["actual"],
                "budget_revenue": FINANCE_COLORS["budget"],
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            monthly_chart,
            x="month",
            y=["actual_ebitda", "budget_ebitda"],
            title="EBITDA: Actual vs Budget",
            template=CHART_TEMPLATE,
            color_discrete_map={
                "actual_ebitda": FINANCE_COLORS["actual"],
                "budget_ebitda": FINANCE_COLORS["budget"],
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Unfavorable Variance Drivers")
    st.dataframe(
        latest_drivers.sort_values("unfavorable_amount", ascending=False).head(10),
        use_container_width=True,
    )


def budget_actuals_page(monthly, selected_month):
    render_page_header(
        "Budget vs Actuals",
        "Compare actual financial performance against budget across revenue, COGS, operating expenses, and EBITDA.",
    )

    monthly_chart = monthly[monthly["month"] <= selected_month]

    metric = st.selectbox(
        "Select financial line item",
        ["Revenue", "COGS", "Operating Expenses", "EBITDA"],
    )

    column_map = {
        "Revenue": ("actual_revenue", "budget_revenue"),
        "COGS": ("actual_cogs", "budget_cogs"),
        "Operating Expenses": ("actual_opex", "budget_opex"),
        "EBITDA": ("actual_ebitda", "budget_ebitda"),
    }

    actual_col, budget_col = column_map[metric]

    fig = px.bar(
        monthly_chart,
        x="month",
        y=[actual_col, budget_col],
        barmode="group",
        title=f"{metric}: Actual vs Budget",
        template=CHART_TEMPLATE,
        color_discrete_map={
            actual_col: FINANCE_COLORS["actual"],
            budget_col: FINANCE_COLORS["budget"],
        },
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(monthly_chart[["month", budget_col, actual_col]], use_container_width=True)


def department_page(departments, selected_month, selected_department):
    render_page_header(
        "Department / Cost Center Analysis",
        "Identify department-level overspend, headcount variance, and cost center pressure.",
    )

    filtered = departments[departments["month"] == selected_month]

    if selected_department != "All":
        filtered = filtered[filtered["department"] == selected_department]

    fig = px.bar(
        filtered.sort_values("opex_variance", ascending=False),
        x="department",
        y="opex_variance",
        color="overspend_flag",
        title="Selected Month Department Variance",
        template=CHART_TEMPLATE,
        color_discrete_map={
            True: FINANCE_COLORS["unfavorable"],
            False: FINANCE_COLORS["favorable"],
        },
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(filtered.sort_values("opex_variance", ascending=False), use_container_width=True)


def trends_page(monthly, revenue, selected_region, selected_business_unit):
    render_page_header(
        "Revenue & Expense Trends",
        "Track financial performance trends across revenue, operating expenses, gross margin, and EBITDA margin.",
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            monthly,
            x="month",
            y=["actual_revenue", "actual_opex"],
            title="Company Revenue and Operating Expense Trend",
            template=CHART_TEMPLATE,
            color_discrete_map={
                "actual_revenue": FINANCE_COLORS["actual"],
                "actual_opex": FINANCE_COLORS["budget"],
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(
            monthly,
            x="month",
            y=["gross_margin_pct", "ebitda_margin_pct"],
            title="Gross Margin and EBITDA Margin Trend",
            template=CHART_TEMPLATE,
        )
        st.plotly_chart(fig, use_container_width=True)

    filtered_revenue = revenue.copy()

    if selected_region != "All":
        filtered_revenue = filtered_revenue[filtered_revenue["region"] == selected_region]

    if selected_business_unit != "All":
        filtered_revenue = filtered_revenue[filtered_revenue["business_unit"] == selected_business_unit]

    revenue_by_region = (
        filtered_revenue
        .groupby(["month", "region"], as_index=False)["actual_revenue"]
        .sum()
    )

    fig = px.line(
        revenue_by_region,
        x="month",
        y="actual_revenue",
        color="region",
        title="Revenue by Region",
        template=CHART_TEMPLATE,
    )

    st.plotly_chart(fig, use_container_width=True)


def forecasting_page(monthly, selected_month):
    render_page_header(
        "Forecasting",
        "Project revenue, operating expenses, EBITDA, and margin using recent business trends.",
    )

    monthly_history = monthly[monthly["month"] <= selected_month]

    months_ahead = st.slider(
        "Forecast months",
        min_value=3,
        max_value=12,
        value=6,
    )

    forecast = build_simple_forecast(monthly_history, months_ahead)

    fig = px.line(
        forecast,
        x="month",
        y=["forecast_revenue", "forecast_ebitda"],
        title="Rolling Forecast",
        template=CHART_TEMPLATE,
        color_discrete_map={
            "forecast_revenue": FINANCE_COLORS["actual"],
            "forecast_ebitda": FINANCE_COLORS["neutral"],
        },
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(forecast, use_container_width=True)


def scenario_page(monthly, selected_month):
    render_page_header(
        "Scenario Analysis",
        "Model the impact of revenue declines, payroll inflation, and marketing spend changes on profitability.",
    )

    selected_monthly = monthly[monthly["month"] == selected_month]

    if selected_monthly.empty:
        st.warning("No data available for the selected month.")
        return

    latest = selected_monthly.iloc[0]

    col1, col2, col3 = st.columns(3)

    revenue_drop = col1.selectbox(
        "Revenue drop",
        [0.00, 0.05, 0.10, 0.15],
        format_func=lambda value: f"{int(value * 100)}%",
    )

    payroll_increase = col2.slider(
        "Payroll increase %",
        min_value=0,
        max_value=15,
        value=8,
    ) / 100

    marketing_change = col3.slider(
        "Marketing spend change %",
        min_value=-25,
        max_value=25,
        value=0,
    ) / 100

    result = apply_scenario(
        latest,
        revenue_drop_pct=revenue_drop,
        payroll_increase_pct=payroll_increase,
        marketing_change_pct=marketing_change,
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Scenario Revenue", format_money(result["scenario_revenue"]))
    kpi2.metric("Scenario EBITDA", format_money(result["scenario_ebitda"]), format_money(result["ebitda_impact"]))
    kpi3.metric("EBITDA Margin", format_pct(result["scenario_ebitda_margin_pct"]))
    kpi4.metric("Margin Impact", f"{result['margin_impact_pp']} pp")

    st.subheader("Standard Downside Cases")
    st.dataframe(build_revenue_downside_table(latest), use_container_width=True)


def variance_driver_page(drivers, selected_month):
    render_page_header(
        "Variance Driver Explanation",
        "Rank the largest unfavorable revenue and expense drivers impacting business performance.",
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
        title="Top Unfavorable Variance Drivers",
        template=CHART_TEMPLATE,
        color_discrete_map={
            "Revenue Shortfall": FINANCE_COLORS["unfavorable"],
            "Expense Overspend": FINANCE_COLORS["neutral"],
        },
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(filtered, use_container_width=True)


def main():
    monthly, departments, revenue, drivers = load_tables()

    selected_month, selected_region, selected_business_unit, selected_department = render_global_filters(
        monthly,
        departments,
        revenue,
    )

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
        ],
    )

    if page == "Executive Summary":
        executive_summary_page(monthly, drivers, selected_month)
    elif page == "Budget vs Actuals":
        budget_actuals_page(monthly, selected_month)
    elif page == "Department Analysis":
        department_page(departments, selected_month, selected_department)
    elif page == "Revenue & Expense Trends":
        trends_page(monthly, revenue, selected_region, selected_business_unit)
    elif page == "Forecasting":
        forecasting_page(monthly, selected_month)
    elif page == "Scenario Analysis":
        scenario_page(monthly, selected_month)
    elif page == "Variance Drivers":
        variance_driver_page(drivers, selected_month)


if __name__ == "__main__":
    main()