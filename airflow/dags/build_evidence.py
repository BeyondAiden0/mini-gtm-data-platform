"""
DAG to build Evidence dashboards.

This DAG builds the static Evidence site from markdown pages and SQL queries.
The build process creates a static site that can be viewed locally or deployed.
"""

from datetime import datetime
import subprocess
from pathlib import Path
from airflow.sdk import DAG, task

# Get paths
AIRFLOW_DIR = Path(__file__).parent.parent
EVIDENCE_DIR = AIRFLOW_DIR.parent / "evidence"


@task
def build_evidence():
    """Build the Evidence static site."""
    print(f"Building Evidence from: {EVIDENCE_DIR}")
    
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(EVIDENCE_DIR),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise Exception(f"Evidence build failed with return code {result.returncode}")
    
    print("Evidence build completed successfully!")
    print(result.stdout)
    return "Build complete"


with DAG(
    dag_id="build_evidence",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # Manual trigger only
    catchup=False,
    doc_md=__doc__,
    tags=["evidence", "bi", "dashboard"],
):
    build_evidence()

