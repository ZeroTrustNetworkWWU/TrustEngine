# setup_db.py
import sqlite3

def setup_db():
    conn = sqlite3.connect('trust_engine_logs.db')
    cursor = conn.cursor()
    
    # Create logs table
    cursor.execute('''
            CREATE TABLE "logs" (
        "id INTEGER PRIMARY KEY AUTOINCREMENT"	INTEGER,
        "timestamp"	TEXT,
        "ip"	TEXT,
        "user"	TEXT,
        "resource"	TEXT,
        "action"	TEXT,
        "additional_info"	TEXT
    ''');
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_db()
