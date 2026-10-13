
from datetime import datetime
from pathlib import Path

from airflow.sdk import dag, task

PROJECT_DIR = Path(
    "/mnt/c/Users/yared/Documents/Engineering the Beautiful Game"
)

PYTHON_EXECUTABLE = (
    "/home/yared/airflow-capstone/.venv312/bin/python"
)

@dag(
    dag_id="engineering_the_beautiful_game",
    description="StatsBomb EPL data engineering pipeline",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["capstone", "soccer", "data-engineering"],
)
def capstone_pipeline():

    @task
    def extract():
        import subprocess
        subprocess.run(
            [PYTHON_EXECUTABLE, "src/extract.py"],
            cwd=PROJECT_DIR,
            check=True,
        )

    @task
    def validate():
        import subprocess
        subprocess.run(
            [PYTHON_EXECUTABLE, "src/validate.py"],
            cwd=PROJECT_DIR,
            check=True,
        )

    @task
    def transform():
        import subprocess
        subprocess.run(
            [PYTHON_EXECUTABLE, "src/transform.py"],
            cwd=PROJECT_DIR,
            check=True,
        )

    @task
    def load():
        import subprocess
        subprocess.run(
            [PYTHON_EXECUTABLE, "src/load.py"],
            cwd=PROJECT_DIR,
            check=True,
        )

    @task
    def calculate_metrics():
        import os
        import subprocess

        sql_file = PROJECT_DIR / "sql" / "calculate_metrics.sql"

        subprocess.run(
            [
                "psql",
                "-h", "127.0.0.1",
                "-p", "5432",
                "-U", "postgres",
                "-d", "engineering_the_beautiful_game",
                "-v", "ON_ERROR_STOP=1",
                "-f", str(sql_file),
            ],
            cwd=PROJECT_DIR,
            env=os.environ.copy(),
            check=True,
        )

    extract_task = extract()
    validate_task = validate()
    transform_task = transform()
    load_task = load()
    metrics_task = calculate_metrics()

    extract_task >> validate_task >> transform_task >> load_task >> metrics_task


capstone_pipeline()
