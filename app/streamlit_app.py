import html
import sys
from io import BytesIO
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import DUCKDB_PATH
from src.executive_summary import generate_executive_summary
from src.export_pack import build_management_pack
from src.forecasting import build_simple_forecast
from src.scenario_analysis import apply_scenario, build_revenue_downside_table
from src.security_utils import (
    UploadSecurityError,
    create_security_event,
    validate_uploaded_file_security,
)
from src.upload_processor import build_upload_template, process_uploaded_workbook


CHART_TEMPLATE = "plotly_dark"

FINANCE_COLORS = {
    "actual": "#22C55E",
    "budget": "#94A3B8",
    "unfavorable": "#EF4444",
    "favorable": "#22C55E",
    "neutral": "#38BDF8",
}


st.set_page_config(
    page_title="FinPlanIQ",
    page_icon="📊",
    layout="wide",
)


st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B1120;
        color: #E5E7EB;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    h1, h2, h3, h4 {
        color: #F9FAFB !important;
        font-weight: 700;
    }

    p, label, span {
        color: inherit;
    }

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.18);
    }

    [data-testid="stMetricLabel"] {
        color: #9CA3AF;
        font-size: 14px;
    }

    [data-testid="stMetricValue"] {
        color: #F9FAFB;
        font-size: 26px;
        font-weight: 700;
    }

    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] * {
        color: #F9FAFB;
    }

    div[data-baseweb="select"] > div {
        background-color: #111827;
        border-color: #1F2937;
        color: #F9FAFB;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #1F2937;
        border-radius: 10px;
    }

    .dashboard-header {
        background: linear-gradient(135deg, #020617 0%, #064E3B 50%, #15803D 100%);
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 24px;
        border: 1px solid #1F2937;
        box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    }

    .dashboard-header h1 {
        color: #FFFFFF !important;
        margin-bottom: 6px;
    }

    .dashboard-header p {
        color: #D1FAE5;
        font-size: 16px;
        margin-bottom: 0;
    }

    .summary-box {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-left: 6px solid #22C55E;
        padding: 20px 24px;
        border-radius: 12px;
        color: #E5E7EB;
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.18);
    }

    .filter-note {
        background-color: #111827;
        border: 1px solid #1F2937;
        padding: 12px 16px;
        border-radius: 10px;
        color: #CBD5E1;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .upload-box {
        background-color: #111827;
        border: 1px solid #1F2937;
        padding: 16px 18px;
        border-radius: 12px;
        color: #CBD5E1;
        font-size: 14px;
        margin-bottom: 18px;
    }

    .privacy-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-left: 5px solid #38BDF8;
        padding: 16px 18px;
        border-radius: 12px;
        color: #CBD5E1;
        font-size: 14px;
        margin-bottom: 18px;
        line-height: 1.6;
    }

    .security-box {
        background-color: #052E16;
        border: 1px solid #166534;
        padding: 12px 14px;
        border-radius: 10px;
        color: #DCFCE7;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .stDownloadButton button {
        background-color: #16A34A;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 700;
    }

    .stDownloadButton button:hover {
        background-color: #15803D;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def query_df(sql):
    with duckdb.connect(str(DUCKDB_PATH), read_only=True) as connection:
        return connection.execute(sql).fetchdf()


@st.cache_data
def load_demo_tables():
    monthly = query_df("SELECT * FROM monthly_financial_summary ORDER BY month")
    departments = query_df("SELECT * FROM department_variance_report ORDER BY month, department")
    revenue = query_df("SELECT * FROM revenue_variance_report ORDER BY month, region, business_unit")
    drivers = query_df("SELECT * FROM variance_drivers ORDER BY month, rank_in_month")
    return monthly, departments, revenue, drivers


@st.cache_data
def load_uploaded_tables(uploaded_file_bytes):
    processed = process_uploaded_workbook(BytesIO(uploaded_file_bytes))
    return (
        processed["monthly"],
        processed["departments"],
        processed["revenue"],
        processed["drivers"],
    )


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


def render_privacy_notice():
    st.markdown(
        """
        <div class="privacy-box">
            <strong>Privacy-first upload handling:</strong><br>
            Uploaded workbooks are processed in memory for this dashboard session.
            FinPlanIQ does not intentionally save uploaded financial files to the project folder.
            For safety, avoid uploading real confidential company financials to a public demo deployment.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_source_selector():
    st.sidebar.markdown("## Data Source")

    data_source = st.sidebar.radio(
        "Choose dataset",
        ["Demo Dataset", "Upload My Own Dataset"],
    )

    uploaded_file = None

    if data_source == "Upload My Own Dataset":
        template_file = build_upload_template()

        st.sidebar.download_button(
            label="Download Upload Template",
            data=template_file,
            file_name="finplaniq_upload_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        uploaded_file = st.sidebar.file_uploader(
            "Upload completed Excel workbook",
            type=["xlsx"],
            help="Only standard .xlsx files up to 10 MB are accepted.",
        )

    return data_source, uploaded_file


def get_active_tables(data_source, uploaded_file):
    if data_source == "Demo Dataset":
        return load_demo_tables(), "Demo Dataset", None

    if uploaded_file is None:
        render_page_header(
            "Upload Your FP&A Dataset",
            "Download the template, fill in your revenue and opex data, then upload the workbook to generate the dashboard.",
        )

        render_privacy_notice()

        st.markdown(
            """
            <div class="upload-box">
                <strong>Upload mode is waiting for a file.</strong><br><br>
                Use the sidebar to download the Excel template. The workbook must include two sheets:
                <br><br>
                <strong>Revenue_COGS</strong> and <strong>Opex_Headcount</strong>.
                <br><br>
                Accepted file type: <strong>.xlsx only</strong><br>
                Maximum file size: <strong>10 MB</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.stop()

    try:
        security_metadata = validate_uploaded_file_security(uploaded_file)
        security_event = create_security_event(
            "upload_validation_passed",
            security_metadata,
        )

        uploaded_file_bytes = uploaded_file.getvalue()
        tables = load_uploaded_tables(uploaded_file_bytes)

        return tables, "Uploaded Dataset", security_event

    except UploadSecurityError as security_error:
        render_page_header(
            "Upload Security Check Failed",
            "The uploaded file did not pass FinPlanIQ's basic upload safety checks.",
        )

        render_privacy_notice()
        st.error(str(security_error))

        st.markdown(
            """
            Please upload a standard Excel `.xlsx` workbook only.
            
            FinPlanIQ does not accept:
            - macro-enabled Excel files
            - old Excel formats
            - CSV files
            - compressed files
            - files larger than 10 MB
            """
        )

        st.stop()

    except Exception as error:
        render_page_header(
            "Upload Error",
            "FinPlanIQ could not process the uploaded workbook.",
        )

        render_privacy_notice()
        st.error("The workbook could not be processed. Please check the template format and try again.")

        with st.expander("Technical detail"):
            st.write(str(error))

        st.markdown(
            """
            Please check that your workbook follows the template exactly:
            - Sheet names must be `Revenue_COGS` and `Opex_Headcount`
            - Required columns must be present
            - Numeric columns cannot contain blanks, text, or negative values
            - Month values should look like `2025-01-01` or `Jan 2025`
            """
        )

        st.stop()


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
        ["All"] + sorted(revenue["region"].dropna().unique().tolist()),
    )

    selected_business_unit = st.sidebar.selectbox(
        "Business Unit",
        ["All"] + sorted(revenue["business_unit"].dropna().unique().tolist()),
    )

    selected_department = st.sidebar.selectbox(
        "Department",
        ["All"] + sorted(departments["department"].dropna().unique().tolist()),
    )

    return selected_month, selected_region, selected_business_unit, selected_department


def render_kpi_cards(latest):
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Revenue",
        format_money(latest["actual_revenue"]),
        format_money(latest["revenue_variance"]),
    )

    col2.metric(
        "Revenue Variance %",
        format_pct(latest["revenue_variance_pct"]),
    )

    col3.metric(
        "Gross Margin %",
        format_pct(latest["gross_margin_pct"]),
    )

    col4.metric(
        "EBITDA",
        format_money(latest["actual_ebitda"]),
        format_money(latest["ebitda_variance"]),
    )

    col5.metric(
        "EBITDA Margin",
        format_pct(latest["ebitda_margin_pct"]),
    )


def render_filter_note(
    selected_month,
    selected_region,
    selected_business_unit,
    selected_department,
    active_dataset_label,
):
    st.markdown(
        f"""
        <div class="filter-note">
            <strong>Selected view:</strong>
            {pd.to_datetime(selected_month).strftime("%b %Y")} |
            Region: {selected_region} |
            Business Unit: {selected_business_unit} |
            Department: {selected_department} |
            Source: {active_dataset_label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_security_status(security_event):
    if security_event is None:
        return

    details = security_event["details"]

    st.sidebar.markdown(
        f"""
        <div class="security-box">
            <strong>Upload security check passed</strong><br>
            File: {html.escape(str(details.get("filename", "uploaded file")))}<br>
            Size: {details.get("file_size_mb", "N/A")} MB
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ebitda_bridge(latest):
    revenue_impact = latest["actual_revenue"] - latest["budget_revenue"]
    cogs_impact = -(latest["actual_cogs"] - latest["budget_cogs"])
    opex_impact = -(latest["actual_opex"] - latest["budget_opex"])

    fig = go.Figure(
        go.Waterfall(
            name="EBITDA Bridge",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=[
                "Budget EBITDA",
                "Revenue Variance",
                "COGS Impact",
                "Opex Impact",
                "Actual EBITDA",
            ],
            y=[
                latest["budget_ebitda"],
                revenue_impact,
                cogs_impact,
                opex_impact,
                latest["actual_ebitda"],
            ],
            connector={"line": {"color": "#94A3B8"}},
            increasing={"marker": {"color": FINANCE_COLORS["favorable"]}},
            decreasing={"marker": {"color": FINANCE_COLORS["unfavorable"]}},
            totals={"marker": {"color": FINANCE_COLORS["neutral"]}},
        )
    )

    fig.update_layout(
        title="EBITDA Variance Bridge",
        template=CHART_TEMPLATE,
        yaxis_title="Amount ($)",
        showlegend=False,
        height=430,
    )

    st.plotly_chart(fig, use_container_width=True)


def executive_summary_page(
    monthly,
    departments,
    revenue,
    drivers,
    selected_month,
    selected_region,
    selected_business_unit,
    selected_department,
    active_dataset_label,
):
    render_page_header(
        "FinPlanIQ",
        "Self-service FP&A analytics for budget vs actuals, variance analysis, forecasting, scenario planning, and management reporting.",
    )

    render_filter_note(
        selected_month,
        selected_region,
        selected_business_unit,
        selected_department,
        active_dataset_label,
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

    render_ebitda_bridge(latest)

    forecast = build_simple_forecast(monthly_chart, months_ahead=6)
    scenario_table = build_revenue_downside_table(latest)

    management_pack = build_management_pack(
        monthly_chart,
        departments[departments["month"] == selected_month],
        revenue[revenue["month"] == selected_month],
        latest_drivers,
        forecast,
        scenario_table,
    )

    st.download_button(
        label="Download Monthly FP&A Pack",
        data=management_pack,
        file_name=f"finplaniq_fpa_pack_{pd.to_datetime(selected_month).strftime('%Y_%m')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
    st.dataframe(
        monthly_chart[["month", budget_col, actual_col]],
        use_container_width=True,
    )


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
    st.dataframe(
        filtered.sort_values("opex_variance", ascending=False),
        use_container_width=True,
    )


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
        filtered_revenue = filtered_revenue[
            filtered_revenue["business_unit"] == selected_business_unit
        ]

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
        title="Filtered Revenue Trend",
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
    kpi2.metric(
        "Scenario EBITDA",
        format_money(result["scenario_ebitda"]),
        format_money(result["ebitda_impact"]),
    )
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
    data_source, uploaded_file = render_data_source_selector()

    tables, active_dataset_label, security_event = get_active_tables(data_source, uploaded_file)
    monthly, departments, revenue, drivers = tables

    render_security_status(security_event)

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
        executive_summary_page(
            monthly,
            departments,
            revenue,
            drivers,
            selected_month,
            selected_region,
            selected_business_unit,
            selected_department,
            active_dataset_label,
        )
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