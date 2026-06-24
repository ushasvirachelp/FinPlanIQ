import duckdb

from config import RAW_DIR, PROCESSED_DIR, DUCKDB_PATH


RAW_TABLES = {
    "dim_date": "dim_date.csv",
    "dim_department": "dim_department.csv",
    "dim_region": "dim_region.csv",
    "dim_business_unit": "dim_business_unit.csv",
    "fact_revenue_cogs": "fact_revenue_cogs.csv",
    "fact_opex_headcount": "fact_opex_headcount.csv",
}

PROCESSED_TABLES = {
    "monthly_financial_summary": "monthly_financial_summary.csv",
    "department_variance_report": "department_variance_report.csv",
    "revenue_variance_report": "revenue_variance_report.csv",
    "variance_drivers": "variance_drivers.csv",
}


def load_csv_table(connection, table_name, csv_path):
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT *
        FROM read_csv_auto('{csv_path}');
        """
    )


def create_views(connection):
    connection.execute(
        """
        CREATE OR REPLACE VIEW v_latest_month AS
        SELECT *
        FROM monthly_financial_summary
        WHERE month = (
            SELECT MAX(month)
            FROM monthly_financial_summary
        );
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE VIEW v_top_variance_drivers AS
        SELECT *
        FROM variance_drivers
        WHERE rank_in_month <= 10;
        """
    )

    connection.execute(
        """
        CREATE OR REPLACE VIEW v_department_overspend AS
        SELECT *
        FROM department_variance_report
        WHERE overspend_flag = TRUE;
        """
    )


def main():
    connection = duckdb.connect(str(DUCKDB_PATH))

    for table_name, filename in RAW_TABLES.items():
        load_csv_table(connection, table_name, RAW_DIR / filename)

    for table_name, filename in PROCESSED_TABLES.items():
        load_csv_table(connection, table_name, PROCESSED_DIR / filename)

    create_views(connection)
    connection.close()

    print("DuckDB database created successfully.")
    print(f"Database saved at: {DUCKDB_PATH}")


if __name__ == "__main__":
    main()