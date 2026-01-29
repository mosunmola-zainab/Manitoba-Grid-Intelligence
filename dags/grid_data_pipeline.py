"""
Manitoba Grid Intelligence - Data Pipeline DAG

This DAG orchestrates the data pipeline for grid analytics:
1. Fetch weather data from Environment Canada
2. Process sensor readings from Kafka
3. Run data quality checks
4. Trigger dbt transformations
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


default_args = {
    "owner": "grid-intelligence",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def fetch_weather_data(**context):
    """Fetch weather data from Environment Canada API."""
    import requests
    import os

    # Placeholder for weather API integration
    print("Fetching weather data for Manitoba regions...")

    # In production, this would call the actual API
    weather_data = {
        "timestamp": context["ts"],
        "regions": [
            {"name": "Winnipeg", "temp_c": -15, "wind_kph": 20},
            {"name": "Thompson", "temp_c": -25, "wind_kph": 15},
            {"name": "Churchill", "temp_c": -30, "wind_kph": 35},
        ]
    }

    return weather_data


def run_data_quality_checks(**context):
    """Run data quality checks on recent sensor readings."""
    from sqlalchemy import create_engine, text
    import os

    # Build connection string from environment
    conn_str = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'grid_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'grid_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'grid_intelligence')}"
    )

    engine = create_engine(conn_str)

    checks = [
        # Check for recent data
        """
        SELECT COUNT(*) as count
        FROM raw.sensor_readings
        WHERE time > NOW() - INTERVAL '1 hour'
        """,
        # Check for anomalies
        """
        SELECT COUNT(*) as anomaly_count
        FROM raw.sensor_readings
        WHERE quality_flag > 0
        AND time > NOW() - INTERVAL '1 hour'
        """,
    ]

    results = {}
    with engine.connect() as conn:
        for i, check in enumerate(checks):
            try:
                result = conn.execute(text(check))
                results[f"check_{i}"] = result.fetchone()
            except Exception as e:
                print(f"Check {i} failed: {e}")
                results[f"check_{i}"] = None

    print(f"Data quality results: {results}")
    return results


with DAG(
    dag_id="grid_data_pipeline",
    default_args=default_args,
    description="Manitoba Grid Intelligence data pipeline",
    schedule_interval=timedelta(minutes=15),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["grid", "pipeline", "manitoba"],
) as dag:

    start = EmptyOperator(task_id="start")

    fetch_weather = PythonOperator(
        task_id="fetch_weather_data",
        python_callable=fetch_weather_data,
    )

    quality_checks = PythonOperator(
        task_id="run_data_quality_checks",
        python_callable=run_data_quality_checks,
    )

    aggregate_hourly = PostgresOperator(
        task_id="aggregate_hourly_readings",
        postgres_conn_id="grid_postgres",
        sql="""
            INSERT INTO staging.hourly_aggregates (
                hour, station_id, reading_type,
                avg_value, min_value, max_value, reading_count
            )
            SELECT
                time_bucket('1 hour', time) as hour,
                sensor_id,
                reading_type,
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value,
                COUNT(*) as reading_count
            FROM raw.sensor_readings
            WHERE time > NOW() - INTERVAL '2 hours'
            GROUP BY 1, 2, 3
            ON CONFLICT (hour, station_id, reading_type)
            DO UPDATE SET
                avg_value = EXCLUDED.avg_value,
                min_value = EXCLUDED.min_value,
                max_value = EXCLUDED.max_value,
                reading_count = EXCLUDED.reading_count;
        """,
    )

    end = EmptyOperator(task_id="end")

    # Define task dependencies
    start >> fetch_weather >> quality_checks >> aggregate_hourly >> end
