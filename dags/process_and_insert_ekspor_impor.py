import os
import pandas as pd
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import calendar
import shutil

bulan_indonesia_ke_ingles = {
    'Januari': 'January',
    'Februari': 'February',
    'Maret': 'March',
    'April': 'April',
    'Mei': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'Agustus': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Desember': 'December'
}

# Fungsi untuk transformasi data berdasarkan kolom Bulan
def transform_data(df):
    # Menggunakan map() pada kolom 'Bulan' secara langsung
    df['Bulan'] = df['Bulan'].map(bulan_indonesia_ke_ingles)

    transformed_dates = []
    current_date = datetime.now()

    for index, row in df.iterrows():
        bulan = row['Bulan']  # Bulan sudah dalam bahasa Inggris
        
        # Mendapatkan bulan saat ini dalam format nama
        current_month = current_date.strftime('%B')
        
        if bulan == current_month:  # Jika bulan sama dengan bulan saat ini
            transformed_date = current_date.date()  # Hanya mengambil bagian tanggal
        else:  # Jika bulan berbeda
            year = current_date.year
            month_number = datetime.strptime(bulan, '%B').month
            last_day = calendar.monthrange(year, month_number)[1]
            transformed_date = datetime(year, month_number, last_day).date()  
        
        transformed_dates.append(transformed_date)
    df['Transformed_Date'] = transformed_dates
    return df

def process_and_insert_data():
    try:
        # Tentukan folder input dan output
        input_folder = '/opt/airflow/input'
        output_folder = '/opt/airflow/output'
        
        # Nama file yang ingin diproses
        file_name = 'Ekspor_import.xlsx'
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)

        # Cek jika file ada di folder input
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f'File {file_name} tidak ditemukan di {input_folder}')
        
        # Membaca file Excel menggunakan openpyxl
        df = pd.read_excel(input_file_path)

        # Validasi kolom
        required_columns = {'Bulan', 'Nilai_Ekspor_USD', 'Berat_Ekspor_KG', 'Nilai_Impor_USD', 'Berat_Impor_KG'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Kolom dalam file tidak sesuai. Diperlukan kolom: {required_columns}")

        # Transformasi data
        df = transform_data(df)

        # Menyambungkan ke database PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        # Insert data ke dalam tabel ekspor_impor
        for index, row in df.iterrows():
            insert_sql = """
                INSERT INTO ekspor_impor (Bulan, Nilai_Ekspor_USD, Berat_Ekspor_KG, Nilai_Impor_USD, Berat_Impor_KG, Transformed_Date)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (
                row['Bulan'], 
                row['Nilai_Ekspor_USD'], 
                row['Berat_Ekspor_KG'], 
                row['Nilai_Impor_USD'], 
                row['Berat_Impor_KG'], 
                row['Transformed_Date']
            ))

        # Commit perubahan dan menutup koneksi
        conn.commit()
        cursor.close()
        conn.close()
        print("File berhasil ditambahkan")
        # # Memindahkan file ke folder output setelah pemrosesan
        # shutil.move(input_file_path, output_file_path)
        # print(f'File {file_name} telah diproses dan dipindahkan ke {output_folder}')
    except Exception as e:
        print(f"Error terjadi: {e}")
        raise e

# Menentukan parameter DAG
dag = DAG(
    'process_and_insert_ekspor_impor',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 12, 3),
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='DAG untuk mengambil data dari file Excel, transformasi, dan memasukkannya ke PostgreSQL',
    schedule_interval=None,  # Menjalankan secara manual
)

# Operator untuk menjalankan fungsi process_and_insert_data
process_and_insert_data_task = PythonOperator(
    task_id='process_and_insert_data',
    python_callable=process_and_insert_data,
    dag=dag,
)

# Menjalankan task
process_and_insert_data_task
