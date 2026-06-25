from io import BytesIO

import pandas as pd


def build_management_pack(
    monthly_summary,
    department_report,
    revenue_report,
    variance_drivers,
    forecast,
    scenario_table,
):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        monthly_summary.to_excel(writer, sheet_name="Monthly Summary", index=False)
        department_report.to_excel(writer, sheet_name="Department Variance", index=False)
        revenue_report.to_excel(writer, sheet_name="Revenue Variance", index=False)
        variance_drivers.to_excel(writer, sheet_name="Variance Drivers", index=False)
        forecast.to_excel(writer, sheet_name="Forecast", index=False)
        scenario_table.to_excel(writer, sheet_name="Scenario Analysis", index=False)

        workbook = writer.book

        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))

                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 35)

        currency_format = "$#,##0.00"
        percent_format = "0.0%"

        for worksheet in workbook.worksheets:
            for row in worksheet.iter_rows(min_row=2):
                for cell in row:
                    header = worksheet.cell(row=1, column=cell.column).value
                    header_text = str(header).lower() if header else ""

                    if "pct" in header_text or "margin" in header_text and "amount" not in header_text:
                        cell.number_format = percent_format
                    elif any(
                        word in header_text
                        for word in [
                            "revenue",
                            "cogs",
                            "opex",
                            "ebitda",
                            "expense",
                            "profit",
                            "variance",
                            "amount",
                        ]
                    ):
                        cell.number_format = currency_format

    output.seek(0)
    return output