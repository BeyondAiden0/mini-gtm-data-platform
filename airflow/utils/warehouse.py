"""
Shared utilities for DuckDB warehouse operations.
"""
from pathlib import Path
import duckdb
from airflow.sdk import task

PROJECT_ROOT = Path(__file__).parent.parent.parent
WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "data.duckdb"


@task()
def ensure_warehouse_exists():
    """Ensure the DuckDB warehouse database exists and has required schemas."""
    print(f"Ensuring warehouse exists at {WAREHOUSE_PATH}")
    
    # Create warehouse directory if it doesn't exist
    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to DuckDB (creates file if it doesn't exist)
    conn = duckdb.connect(str(WAREHOUSE_PATH))
    
    # Create schemas
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
    conn.execute("CREATE SCHEMA IF NOT EXISTS staging")
    conn.execute("CREATE SCHEMA IF NOT EXISTS marts")
    
    # Verify
    schemas = conn.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('raw', 'staging', 'marts')").fetchall()
    print(f"✓ Warehouse initialized with schemas: {[s[0] for s in schemas]}")
    
    conn.close()
    return str(WAREHOUSE_PATH)

