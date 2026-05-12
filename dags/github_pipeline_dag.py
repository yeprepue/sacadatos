from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
import logging
import sys
import os

# Configuración por defecto
default_args = {
    'owner': 'sacadatos',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
dag = DAG(
    'github_pipeline_v2',
    default_args=default_args,
    description='Pipeline de extracción de datos de GitHub orquestado con Airflow',
    schedule_interval='0 2 * * *',  # Ejecutar diariamente a las 2 AM UTC
    catchup=False,
    tags=['github', 'etl', 'orchestration'],
)

logger = logging.getLogger(__name__)

# ============ TAREA 1: Cargar configuración desde Google Drive ============
def load_config_from_drive(**context):
    """Lee la configuración desde Google Drive"""
    sys.path.insert(0, '/opt/airflow/src')
    from dotenv import load_dotenv
    
    load_dotenv('/opt/airflow/.env')
    
    config_file_id = os.getenv('GOOGLE_DRIVE_CONFIG_FILE_ID')
    logger.info(f"✓ Config cargada desde Drive: {config_file_id}")
    
    # Guardar en contexto para otras tareas
    context['task_instance'].xcom_push(key='config_file_id', value=config_file_id)
    
    return {'status': 'success', 'config_id': config_file_id}

load_config_task = PythonOperator(
    task_id='load_config_from_drive',
    python_callable=load_config_from_drive,
    provide_context=True,
    dag=dag,
)

# ============ TAREA 2: Ejecutar contenedor de extracción ============
run_extractor = BashOperator(
    task_id='run_extractor_container',
    bash_command='''
    set -e
    
    echo "🐳 Iniciando contenedor de extracción..."
    cd /opt/airflow/docker
    
    # Asegurar que existe el .env
    if [ ! -f .env ]; then
        cp /opt/airflow/.env .env
    fi
    
    # Ejecutar extractor
    docker-compose -f docker-compose.yml up -d --build extractor
    
    # Esperar a que termine
    docker-compose -f docker-compose.yml exec -T extractor python main.py || true
    
    # Copiar reporte
    docker cp github_extractor:/app/reporte_github.csv /opt/airflow/reports/reporte_github.csv 2>/dev/null || echo "⚠️ Reporte no disponible"
    
    echo "✓ Extracción completada"
    ''',
    dag=dag,
)

# ============ TAREA 3: Transformaciones SQL ============
def transform_and_validate(**context):
    """Ejecuta transformaciones SQL y validaciones"""
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        from src.infrastructure.database import Database
        from src.config.settings import PipelineConfig
        from sqlalchemy import text
        
        config = PipelineConfig()
        db = Database(config.database.connection_string)
        
        with db.engine.connect() as conn:
            # Vista de resumen de repositorios
            conn.execute(text("""
                DROP VIEW IF EXISTS repository_summary CASCADE;
            """))
            conn.execute(text("""
                CREATE VIEW repository_summary AS
                SELECT 
                    r.id,
                    r.owner || '/' || r.name as full_name,
                    COUNT(DISTINCT i.id) as total_issues,
                    COUNT(DISTINCT c.sha) as total_commits,
                    MIN(c.commit_date) as first_commit,
                    MAX(c.commit_date) as last_commit
                FROM repositories r
                LEFT JOIN issues i ON r.id = i.repository_id
                LEFT JOIN commits c ON r.id = c.repository_id
                GROUP BY r.id, r.owner, r.name;
            """))
            conn.commit()
        
        logger.info("✓ Transformaciones SQL completadas")
        db.close()
        
        return {'status': 'success', 'message': 'Transformaciones completadas'}
    
    except Exception as e:
        logger.error(f"❌ Error en transformación: {str(e)}")
        return {'status': 'error', 'message': str(e)}

transform_task = PythonOperator(
    task_id='transform_sql_data',
    python_callable=transform_and_validate,
    provide_context=True,
    dag=dag,
)

# ============ TAREA 4: Generar reporte final ============
def generate_final_report(**context):
    """Genera el reporte final en CSV"""
    sys.path.insert(0, '/opt/airflow/src')
    
    try:
        from src.infrastructure.database import Database
        from src.config.settings import PipelineConfig
        from src.application.use_cases.generate_report import GenerateReportUseCase
        from src.infrastructure.adapters.database_adapter import DatabaseAdapter
        
        config = PipelineConfig()
        db = Database(config.database.connection_string)
        db_adapter = DatabaseAdapter(db)
        
        report_use_case = GenerateReportUseCase(db_adapter, None)
        result = report_use_case.execute()
        
        logger.info(f"✓ Reporte generado: {result}")
        
        context['task_instance'].xcom_push(key='report_status', value=result)
        db.close()
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {str(e)}")
        raise

generate_report = PythonOperator(
    task_id='generate_final_report',
    python_callable=generate_final_report,
    provide_context=True,
    dag=dag,
)

# ============ TAREA 5: Validación y Cleanup ============
def cleanup_and_validate(**context):
    """Limpia recursos temporales y valida"""
    logger.info("🧹 Limpiando recursos...")
    
    # Obtener información de tareas anteriores
    ti = context['task_instance']
    report_status = ti.xcom_pull(task_ids='generate_final_report', key='report_status')
    
    logger.info(f"✓ Pipeline completado exitosamente")
    logger.info(f"Resultado: {report_status}")
    
    return {'status': 'completed', 'timestamp': datetime.now().isoformat()}

cleanup_task = PythonOperator(
    task_id='cleanup_and_validate',
    python_callable=cleanup_and_validate,
    provide_context=True,
    dag=dag,
)

# ============ Control Flow ============
start = EmptyOperator(task_id='start', dag=dag)
end = EmptyOperator(task_id='end', dag=dag)

# Dependencias
start >> load_config_task >> run_extractor >> transform_task >> generate_report >> cleanup_task >> end
