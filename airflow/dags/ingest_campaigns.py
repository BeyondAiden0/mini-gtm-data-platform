"""
Airflow DAG to ingest marketing campaign data into DuckDB.
"""
from datetime import datetime
from pathlib import Path
import sys
import duckdb
from airflow.sdk import dag, task

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.warehouse import ensure_warehouse_exists, WAREHOUSE_PATH

PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_PATH = PROJECT_ROOT / "sources" / "postgres" / "campaigns.csv"


@dag(
    dag_id="ingest_campaigns",
    start_date=datetime(2020, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ingestion", "marketing"],
)
def ingest_campaigns():
    """DAG to ingest marketing campaigns into DuckDB."""

    @task()
    def extract():
        print(f"Extracting campaigns from {SOURCE_PATH}")
        return str(SOURCE_PATH)

    @task()
    def load_to_duckdb(warehouse_path: str, source_path: str):
        print(f"Loading campaigns into DuckDB at {warehouse_path}")
        conn = duckdb.connect(warehouse_path)
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw.campaigns AS
            SELECT * FROM read_csv_auto('{source_path}')
        """)
        result = conn.execute("SELECT COUNT(*) FROM raw.campaigns").fetchone()
        print(f"Loaded {result[0]} campaign records into raw.campaigns")
        conn.close()
        return result[0]

    warehouse_path = ensure_warehouse_exists()
    source_path = extract()
    load_to_duckdb(warehouse_path, source_path)


dag_instance = ingest_campaigns()

if __name__ == "__main__":
    print("Testing ingest_campaigns DAG...")
    dag_instance.test()

