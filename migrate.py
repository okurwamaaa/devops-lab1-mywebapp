import psycopg2
import json
import os


CONFIG_PATH = '/etc/mywebapp/config.json'
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = 'config.json'

try:
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Помилка завантаження конфігурації: {e}")
    exit(1)

def run_migration():
    try:
        print("Підключення до бази даних...")
        conn = psycopg2.connect(
            host=config.get('db_host', '127.0.0.1'),
            port=config.get('db_port', 5432),
            dbname=config.get('db_name', 'inventory_db'),
            user=config.get('db_user', 'app'),
            password=config.get('db_password', '123')
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("Створення таблиці 'items', якщо вона не існує...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("Міграція успішно завершена!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Помилка міграції: {e}")

if __name__ == '__main__':
    run_migration()