from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'github_data_pipeline',
    default_args=default_args,
    description='Pipeline de extracción de datos GitHub',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['github', 'data_engineering'],
) as dag:

    # Task 1: Cargar configuración desde Google Drive
    def load_config(**context):
        import sys
        sys.path.append('/opt/airflow/scripts')
        from config_loader import ConfigLoader
        
        loader = ConfigLoader(
            credentials_path='/opt/airflow/scripts/credentials.json',
            folder_id=os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        )
        
        config = loader.get_config()
        context['ti'].xcom_push(key='config', value=config)
        
        # Determinar tipo de extracción
        last_extraction = config.get('last_extraction')
        if last_extraction:
            context['ti'].xcom_push(key='extraction_type', value='incremental')
        else:
            context['ti'].xcom_push(key='extraction_type', value='full')
        
        return config

    load_config_task = PythonOperator(
        task_id='load_config_from_drive',
        python_callable=load_config,
    )

    # Task 2: Ejecutar contenedor de extracción
    extract_data = DockerOperator(
        task_id='extract_github_data',
        image='github-extractor:latest',
        command='python /app/src/main.py {{ ti.xcom_pull(task_ids="load_config_from_drive", key="extraction_type") }}',
        docker_url='unix://var/run/docker.sock',
        environment={
            'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
            'POSTGRES_HOST': 'postgres',
            'POSTGRES_USER': 'airflow',
            'POSTGRES_PASSWORD': 'airflow',
            'POSTGRES_DB': 'github_data',
        },
        xcom_all=True,
    )

    # Task 3: Cargar y transformar en SQL (ya done en extractor)
    # Task 4: Generar reporte
    def generate_report(**context):
        import sys
        sys.path.append('/opt/airflow/scripts')
        from storage import DataStorage
        from reporter import Reporter
        
        storage = DataStorage(
            host=os.environ.get('POSTGRES_HOST', 'postgres'),
            user=os.environ.get('POSTGRES_USER', 'airflow'),
            password=os.environ.get('POSTGRES_PASSWORD', 'airflow'),
            db=os.environ.get('POSTGRES_DB', 'github_data')
        )
        
        reporter = Reporter(
            credentials_path='/opt/airflow/scripts/credentials.json',
            folder_id=os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        )
        
        df = reporter.generate_summary(storage)
        reporter.upload_to_drive(df)
        
        return "Reporte generado exitosamente"

    generate_report_task = PythonOperator(
        task_id='generate_and_upload_report',
        python_callable=generate_report,
    )

    # Task 5: Actualizar last_extraction
    def update_last_extraction(**context):
        from datetime import datetime
        import sys
        sys.path.append('/opt/airflow/scripts')
        from config_loader import ConfigLoader
        
        # Aquí actualizarías en Drive el timestamp
        new_timestamp = datetime.now().isoformat()
        print(f"Extraction updated to: {new_timestamp}")

    update_config_task = PythonOperator(
        task_id='update_last_extraction',
        python_callable=update_last_extraction,
    )

    # Flujo
    load_config_task >> extract_data >> generate_report_task >> update_config_task
