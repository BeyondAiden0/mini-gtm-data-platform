"""
Airflow DAG to run dbt transformations.
Separate tasks for staging and marts layers with tests for each.
"""
from datetime import datetime
from pathlib import Path
import subprocess
from airflow.sdk import dag, task

PROJECT_ROOT = Path(__file__).parent.parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"

@dag(
    dag_id="run_dbt",
    start_date=datetime(2020, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["dbt", "transformation"],
)
def run_dbt():
    """DAG to run dbt models and tests in staging and marts layers."""
    
    @task()
    def run_staging_models():
        """Run dbt staging models (views)."""
        print(f"Running dbt staging models in {DBT_PROJECT_DIR}")
        
        result = subprocess.run(
            ["dbt", "run", "--select", "staging.*", "--profiles-dir", "."],
            cwd=DBT_PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"dbt staging run failed with return code {result.returncode}")
        
        print("✓ Staging models completed successfully")
        return "staging_run_complete"
    
    @task()
    def test_staging_models(staging_result: str):
        """Run dbt tests on staging models."""
        print(f"Testing dbt staging models in {DBT_PROJECT_DIR}")
        print(f"Dependency: {staging_result}")
        
        result = subprocess.run(
            ["dbt", "test", "--select", "staging.*", "--profiles-dir", "."],
            cwd=DBT_PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"dbt staging tests failed with return code {result.returncode}")
        
        print("✓ Staging tests completed successfully")
        return "staging_test_complete"
    
    @task()
    def run_marts_models(staging_test_result: str):
        """Run dbt marts models (tables)."""
        print(f"Running dbt marts models in {DBT_PROJECT_DIR}")
        print(f"Dependency: {staging_test_result}")
        
        result = subprocess.run(
            ["dbt", "run", "--select", "marts.*", "--profiles-dir", "."],
            cwd=DBT_PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"dbt marts run failed with return code {result.returncode}")
        
        print("✓ Marts models completed successfully")
        return "marts_run_complete"
    
    @task()
    def test_marts_models(marts_result: str):
        """Run dbt tests on marts models."""
        print(f"Testing dbt marts models in {DBT_PROJECT_DIR}")
        print(f"Dependency: {marts_result}")
        
        result = subprocess.run(
            ["dbt", "test", "--select", "marts.*", "--profiles-dir", "."],
            cwd=DBT_PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise Exception(f"dbt marts tests failed with return code {result.returncode}")
        
        print("✓ Marts tests completed successfully")
        return "marts_test_complete"
    
    # Define task dependencies
    staging_result = run_staging_models()
    staging_test_result = test_staging_models(staging_result)
    marts_result = run_marts_models(staging_test_result)
    test_marts_models(marts_result)

dag_instance = run_dbt()

if __name__ == "__main__":
    print("Testing run_dbt DAG...")
    dag_instance.test()

