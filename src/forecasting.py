import pandas as pd


def build_simple_forecast(monthly_summary, months_ahead=6):
    df = monthly_summary.sort_values("month").copy()
    df["month"] = pd.to_datetime(df["month"])

    latest = df.iloc[-1]
    trailing = df.tail(6)

    monthly_revenue_growth = trailing["actual_revenue"].pct_change().dropna().mean()
    cogs_rate = (trailing["actual_cogs"] / trailing["actual_revenue"]).mean()
    opex_growth = trailing["actual_opex"].pct_change().dropna().mean()

    forecast_rows = []

    revenue = latest["actual_revenue"]
    opex = latest["actual_opex"]
    latest_month = latest["month"]

    for i in range(1, months_ahead + 1):
        forecast_month = latest_month + pd.DateOffset(months=i)

        revenue = revenue * (1 + monthly_revenue_growth)
        opex = opex * (1 + opex_growth)
        cogs = revenue * cogs_rate

        gross_profit = revenue - cogs
        ebitda = gross_profit - opex

        forecast_rows.append({
            "month": forecast_month,
            "forecast_revenue": round(revenue, 2),
            "forecast_cogs": round(cogs, 2),
            "forecast_opex": round(opex, 2),
            "forecast_gross_profit": round(gross_profit, 2),
            "forecast_ebitda": round(ebitda, 2),
            "forecast_gross_margin_pct": round(gross_profit / revenue, 4),
            "forecast_ebitda_margin_pct": round(ebitda / revenue, 4),
        })

    return pd.DataFrame(forecast_rows)