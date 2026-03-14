"""
Airflow DAG to ingest contact-opportunity role data into DuckDB.
"""
from datetime import datetime
from pathlib import Path
import sys
import duckdb
from airflow.sdk import dag, task

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.warehouse import ensure_warehouse_exists, WAREHOUSE_PATH

PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_PATH = PROJECT_ROOT / "sources" / "postgres" / "contact_roles.csv"


@dag(
    dag_id="ingest_contact_roles",
    start_date=datetime(2020, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ingestion", "crm"],
)
def ingest_contact_roles():
    """DAG to ingest contact-opportunity roles into DuckDB."""

    @task()
    def extract():
        print(f"Extracting contact roles from {SOURCE_PATH}")
        return str(SOURCE_PATH)

    @task()
    def load_to_duckdb(warehouse_path: str, source_path: str):
        print(f"Loading contact roles into DuckDB at {warehouse_path}")
        conn = duckdb.connect(warehouse_path)
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.contact_roles AS
            SELECT * FROM read_csv_auto('{source_path}')
        """)
        result = conn.execute("SELECT COUNT(*) FROM raw.contact_roles").fetchone()
        print(f"Loaded {result[0]} contact role records into raw.contact_roles")
        conn.close()
        return result[0]

    warehouse_path = ensure_warehouse_exists()
    source_path = extract()
    load_to_duckdb(warehouse_path, source_path)


dag_instance = ingest_contact_roles()

if __name__ == "__main__":
    print("Testing ingest_contact_roles DAG...")
    dag_instance.test()
