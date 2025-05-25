import sqlite3
import uuid
from datetime import datetime

DB_NAME = "user_data.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                file BLOB,
                file_ext TEXT,
                ocr_results TEXT,
                nlp_data TEXT,
                gemini_response TEXT
            )
        ''')
        conn.commit()

def save_data(file_bytes, file_ext, ocr_results, nlp_data, gemini_response):
    unique_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO data (id, timestamp, file, file_ext, ocr_results, nlp_data, gemini_response)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (unique_id, timestamp, file_bytes, file_ext, ocr_results, nlp_data, gemini_response))
        conn.commit()
    return unique_id

def get_data_by_id(unique_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, file_ext, ocr_results, nlp_data, gemini_response FROM data WHERE id=?', (unique_id,))
        return cursor.fetchone()
