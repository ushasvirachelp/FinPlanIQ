import pandas as pd


def format_money(value):
    value = float(value)

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"

    return f"${value:,.0f}"


def format_pct(value):
    return f"{float(value) * 100:.1f}%"


def generate_executive_summary(monthly_summary, drivers):
    latest = monthly_summary.sort_values("month").iloc[-1]
    month = pd.to_datetime(latest["month"]).strftime("%B %Y")

    revenue_direction = "above" if latest["revenue_variance"] >= 0 else "below"
    opex_direction = "above" if latest["opex_variance"] >= 0 else "below"
    ebitda_direction = "favorable" if latest["ebitda_variance"] >= 0 else "unfavorable"

    if drivers.empty:
        driver_text = "No material unfavorable variance drivers were identified."
    else:
        top_drivers = drivers.sort_values("unfavorable_amount", ascending=False).head(3)

        driver_items = []
        for _, row in top_drivers.iterrows():
            driver_items.append(
                f"{row['driver_category']} ({format_money(row['unfavorable_amount'])})"
            )

        driver_text = "The largest unfavorable drivers were " + ", ".join(driver_items) + "."

    summary = (
        f"In {month}, total revenue was {format_money(latest['actual_revenue'])}, "
        f"{revenue_direction} budget by {format_money(latest['revenue_variance'])} "
        f"({format_pct(latest['revenue_variance_pct'])}). "
        f"Operating expenses were {format_money(latest['actual_opex'])}, "
        f"{opex_direction} budget by {format_money(latest['opex_variance'])} "
        f"({format_pct(latest['opex_variance_pct'])}). "
        f"Gross margin was {format_pct(latest['gross_margin_pct'])}, while EBITDA was "
        f"{format_money(latest['actual_ebitda'])} with an EBITDA margin of "
        f"{format_pct(latest['ebitda_margin_pct'])}. "
        f"Overall EBITDA variance was {ebitda_direction} at "
        f"{format_money(latest['ebitda_variance'])}. "
        f"{driver_text}"
    )

    return summary