"""
Airflow DAG to ingest contact data into DuckDB.
"""
from datetime import datetime
from pathlib import Path
import sys
import duckdb
from airflow.sdk import dag, task

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.warehouse import ensure_warehouse_exists, WAREHOUSE_PATH

PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_PATH = PROJECT_ROOT / "sources" / "postgres" / "contacts.csv"


@dag(
    dag_id="ingest_contacts",
    start_date=datetime(2020, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ingestion", "crm"],
)
def ingest_contacts():
    """DAG to ingest contacts into DuckDB."""

    @task()
    def extract():
        print(f"Extracting contacts from {SOURCE_PATH}")
        return str(SOURCE_PATH)

    @task()
    def load_to_duckdb(warehouse_path: str, source_path: str):
        print(f"Loading contacts into DuckDB at {warehouse_path}")
        conn = duckdb.connect(warehouse_path)
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.contacts AS
            SELECT * FROM read_csv_auto('{source_path}')
        """)
        result = conn.execute("SELECT COUNT(*) FROM raw.contacts").fetchone()
        print(f"Loaded {result[0]} contact records into raw.contacts")
        conn.close()
        return result[0]

    warehouse_path = ensure_warehouse_exists()
    source_path = extract()
    load_to_duckdb(warehouse_path, source_path)


dag_instance = ingest_contacts()

if __name__ == "__main__":
    print("Testing ingest_contacts DAG...")
    dag_instance.test()

