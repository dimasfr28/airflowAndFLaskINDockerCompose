# Gunakan image apache/airflow sebagai base image
FROM apache/airflow:2.10.3-python3.9

# Switch ke root user untuk menginstal dependensi sistem
USER root

# Update dan install dependensi sistem termasuk libpq-dev untuk psycopg2
RUN apt-get update && \
    apt-get install -y libpq-dev supervisor

# Salin requirements.txt ke container dan install dependensi Python
COPY ./requirements.txt /requirements.txt

# Switch ke pengguna airflow untuk menjalankan pip install
USER airflow

WORKDIR /app

# Salin aplikasi Flask Anda ke dalam container (menggunakan folder app yang ada di root)
COPY ./app .

# Install dependensi Python menggunakan pip
RUN pip install --no-cache-dir -r /requirements.txt

# Set environment variable untuk Flask
# ENV FLASK_APP=/app/app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV FLASK_RUN_PORT=5000

# Expose port untuk Flask dan Airflow webserver
EXPOSE 8080

# Menambahkan entrypoint untuk menjalankan Flask dan Airflow secara bersamaan
# Menggunakan supervisord untuk mengelola kedua aplikasi (Flask dan Airflow)
COPY ./supervisord.conf /etc/supervisor/supervisord.conf

    # Gunakan supervisord untuk menjalankan Flask dan Airflow webserver secara bersamaan
CMD ["flask run --host=0.0.0.0 --port=8080"]
