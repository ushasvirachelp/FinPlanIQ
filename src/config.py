from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DUCKDB_PATH = DATA_DIR / "finplaniq.duckdb"

START_MONTH = "2023-01-01"
END_MONTH = "2025-12-01"
RANDOM_SEED = 42

DEPARTMENTS = [
    {"department_id": "D001", "department": "Sales", "cost_center": "Revenue Operations"},
    {"department_id": "D002", "department": "Marketing", "cost_center": "Growth Marketing"},
    {"department_id": "D003", "department": "Engineering", "cost_center": "Product Engineering"},
    {"department_id": "D004", "department": "Product", "cost_center": "Product Management"},
    {"department_id": "D005", "department": "Customer Success", "cost_center": "Client Operations"},
    {"department_id": "D006", "department": "G&A", "cost_center": "Corporate Operations"},
]

REGIONS = [
    {"region_id": "R001", "region": "North America"},
    {"region_id": "R002", "region": "Europe"},
    {"region_id": "R003", "region": "APAC"},
    {"region_id": "R004", "region": "LATAM"},
]

BUSINESS_UNITS = [
    {"business_unit_id": "B001", "business_unit": "Enterprise Subscription"},
    {"business_unit_id": "B002", "business_unit": "SMB Subscription"},
    {"business_unit_id": "B003", "business_unit": "Professional Services"},
    {"business_unit_id": "B004", "business_unit": "Data & Insights"},
]