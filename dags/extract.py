from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# Fungsi untuk menambahkan tabel
def create_table():
    # Menyambungkan ke database PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    # SQL untuk membuat tabel baru
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS ekspor_impor (
            Bulan TEXT,
            Nilai_Ekspor_USD NUMERIC,
            Berat_Ekspor_KG NUMERIC,
            Nilai_Impor_USD NUMERIC,
            Berat_Impor_KG NUMERIC,
            Transformed_Date DATE
        );
        """

    # Eksekusi SQL untuk membuat tabel
    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    conn.close()

# Menentukan parameter DAG
dag = DAG(
    'create_postgres_table',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 12, 3),
        'retries': 1,
    },
    description='DAG untuk menambahkan tabel di PostgreSQL',
    schedule_interval=None,  # Menjalankan secara manual
)

# Operator untuk menjalankan fungsi create_table
create_table_task = PythonOperator(
    task_id='create_table',
    python_callable=create_table,
    dag=dag,
)

# Menjalankan task
create_table_task
