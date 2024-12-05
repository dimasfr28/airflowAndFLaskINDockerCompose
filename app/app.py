from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)

# Aktifkan CORS untuk semua rute
CORS(app)

# Database connection configuration
DATABASE_URL = "postgresql://airflow:airflow@papemrog-postgres-1:5432/airflow"

def get_data_from_db():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Query to fetch raw data for each month
    query = """
        SELECT bulan, 
               nilai_ekspor_usd, 
               nilai_impor_usd, 
               berat_ekspor_kg, 
               berat_impor_kg
        FROM ekspor_impor
        ORDER BY bulan;
    """
    cur.execute(query)
    result = cur.fetchall()

    bulan = []
    nilai_ekspor_usd = []
    nilai_impor_usd = []
    berat_ekspor_kg = []
    berat_impor_kg = []

    for row in result:
        bulan.append(row[0])
        nilai_ekspor_usd.append(row[1])
        nilai_impor_usd.append(row[2])
        berat_ekspor_kg.append(row[3])
        berat_impor_kg.append(row[4])

    # Calculate the averages
    avg_ekspor_usd = sum(nilai_ekspor_usd) / len(nilai_ekspor_usd) if nilai_ekspor_usd else 0
    avg_impor_usd = sum(nilai_impor_usd) / len(nilai_impor_usd) if nilai_impor_usd else 0
    avg_ekspor_kg = sum(berat_ekspor_kg) / len(berat_ekspor_kg) if berat_ekspor_kg else 0
    avg_impor_kg = sum(berat_impor_kg) / len(berat_impor_kg) if berat_impor_kg else 0

    # Close the connection
    cur.close()
    conn.close()

    # Return both raw data and averages
    return {
        "bulan": bulan,
        "nilai_ekspor_usd": nilai_ekspor_usd,
        "nilai_impor_usd": nilai_impor_usd,
        "berat_ekspor_kg": berat_ekspor_kg,
        "berat_impor_kg": berat_impor_kg,
        "avg_ekspor_usd": avg_ekspor_usd,
        "avg_impor_usd": avg_impor_usd,
        "avg_ekspor_kg": avg_ekspor_kg,
        "avg_impor_kg": avg_impor_kg,
    }

@app.route('/')
def index():
    # Render the index.html page
    return render_template('index.html')

@app.route('/data')
def data():
    data = get_data_from_db()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
