import sqlite3
import os

class BotDatabase:
    def __init__(self, directory, filename):
        os.makedirs(directory, exist_ok=True)
        self.db_path = os.path.join(directory, filename)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                download_date TEXT,
                discord_user_id  INTEGER,
                pixeldrain_upload_id TEXT,
                file_name TEXT,
                downloaded_timestamp REAL,
                scheduled_deletion_timestamp REAL
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads_archive (
                id INTEGER PRIMARY KEY, 
                download_date TEXT,
                discord_user_id  INTEGER,
                pixeldrain_upload_id TEXT,
                file_name TEXT,
                downloaded_timestamp REAL,
                scheduled_deletion_timestamp REAL
            )
            ''')
            conn.commit()

    def add_download(self,
        download_date,
        discord_user_id,
        pixeldrain_upload_id,
        file_name,
        downloaded_timestamp,
        scheduled_deletion_timestamp
    ):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads (
                    download_date, 
                    discord_user_id, 
                    pixeldrain_upload_id,
                    file_name,
                    downloaded_timestamp, 
                    scheduled_deletion_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                download_date,
                discord_user_id,
                pixeldrain_upload_id,
                file_name,
                downloaded_timestamp,
                scheduled_deletion_timestamp))
            conn.commit()

            return cursor.lastrowid

    def get_expired_downloads(self, current_timestamp):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, pixeldrain_upload_id
                FROM downloads
                WHERE scheduled_deletion_timestamp <= ?
                ''', (current_timestamp,))

            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    def move_to_archive(self, record_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO downloads_archive 
                SELECT * FROM downloads WHERE id = ?
            ''', (record_id,))
            if cursor.rowcount > 0:
                cursor.execute("DELETE FROM downloads WHERE id = ?", (record_id,))

            conn.commit()