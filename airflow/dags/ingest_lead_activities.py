"""
Airflow DAG to ingest lead activity data into DuckDB.
"""
from datetime import datetime
from pathlib import Path
import sys
import duckdb
from airflow.sdk import dag, task

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.warehouse import ensure_warehouse_exists, WAREHOUSE_PATH

PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_PATH = PROJECT_ROOT / "sources" / "postgres" / "lead_activities.csv"


@dag(
    dag_id="ingest_lead_activities",
    start_date=datetime(2020, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ingestion", "marketing"],
)
def ingest_lead_activities():
    """DAG to ingest lead activities into DuckDB."""

    @task()
    def extract():
        print(f"Extracting lead activities from {SOURCE_PATH}")
        return str(SOURCE_PATH)

    @task()
    def load_to_duckdb(warehouse_path: str, source_path: str):
        print(f"Loading lead activities into DuckDB at {warehouse_path}")
        conn = duckdb.connect(warehouse_path)
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.lead_activities AS
            SELECT * FROM read_csv_auto('{source_path}')
        """)
        result = conn.execute("SELECT COUNT(*) FROM raw.lead_activities").fetchone()
        print(f"Loaded {result[0]} lead activity records into raw.lead_activities")
        conn.close()
        return result[0]

    warehouse_path = ensure_warehouse_exists()
    source_path = extract()
    load_to_duckdb(warehouse_path, source_path)


dag_instance = ingest_lead_activities()

if __name__ == "__main__":
    print("Testing ingest_lead_activities DAG...")
    dag_instance.test()

