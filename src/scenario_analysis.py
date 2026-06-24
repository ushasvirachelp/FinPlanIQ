import pandas as pd


def apply_scenario(
    base_row,
    revenue_drop_pct=0.0,
    payroll_increase_pct=0.0,
    marketing_change_pct=0.0,
    payroll_share_of_opex=0.58,
    marketing_share_of_opex=0.18,
):
    base_revenue = base_row["actual_revenue"]
    base_cogs = base_row["actual_cogs"]
    base_opex = base_row["actual_opex"]
    base_ebitda = base_row["actual_ebitda"]
    base_ebitda_margin = base_row["ebitda_margin_pct"]

    new_revenue = base_revenue * (1 - revenue_drop_pct)

    cogs_rate = base_cogs / base_revenue
    new_cogs = new_revenue * cogs_rate

    payroll_opex = base_opex * payroll_share_of_opex * (1 + payroll_increase_pct)
    marketing_opex = base_opex * marketing_share_of_opex * (1 + marketing_change_pct)
    other_opex = base_opex * (1 - payroll_share_of_opex - marketing_share_of_opex)

    new_opex = payroll_opex + marketing_opex + other_opex

    gross_profit = new_revenue - new_cogs
    ebitda = gross_profit - new_opex

    ebitda_margin = ebitda / new_revenue if new_revenue != 0 else 0

    return {
        "scenario_revenue": round(new_revenue, 2),
        "scenario_cogs": round(new_cogs, 2),
        "scenario_opex": round(new_opex, 2),
        "scenario_gross_profit": round(gross_profit, 2),
        "scenario_ebitda": round(ebitda, 2),
        "scenario_ebitda_margin_pct": round(ebitda_margin, 4),
        "ebitda_impact": round(ebitda - base_ebitda, 2),
        "margin_impact_pp": round((ebitda_margin - base_ebitda_margin) * 100, 2),
    }


def build_revenue_downside_table(base_row):
    scenarios = []

    for drop in [0.05, 0.10, 0.15]:
        result = apply_scenario(base_row, revenue_drop_pct=drop)
        result["scenario"] = f"Revenue drops {int(drop * 100)}%"
        scenarios.append(result)

    return pd.DataFrame(scenarios)