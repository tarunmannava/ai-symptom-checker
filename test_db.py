import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="symptom_checker",
        user="postgres",
        password="password123"
    )
    print(" PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f" Connection failed: {e}")