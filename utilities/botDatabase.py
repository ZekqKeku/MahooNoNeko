import datetime
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
                discord_user_id INTEGER,
                pixeldrain_upload_id TEXT,
                file_name TEXT,
                file_extension TEXT,
                file_length REAL,
                downloaded_timestamp REAL,
                scheduled_deletion_timestamp REAL
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads_archive (
                id INTEGER PRIMARY KEY, 
                download_date TEXT,
                discord_user_id INTEGER,
                pixeldrain_upload_id TEXT,
                file_name TEXT,
                file_extension TEXT,
                file_length REAL,
                downloaded_timestamp REAL,
                scheduled_deletion_timestamp REAL
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                user_id  INTEGER,
                date TEXT,
                used_tokens INTEGER DEFAULT 0,
                custom_limit INTEGER DEFAULT NULL,
                PRIMARY KEY (user_id, date)
            )
            ''')

            conn.commit()

    def add_download(self,
        download_date,
        discord_user_id,
        pixeldrain_upload_id,
        file_name,
        file_extension,
        file_length,
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
                    file_extension,
                    file_length,
                    downloaded_timestamp, 
                    scheduled_deletion_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                download_date,
                discord_user_id,
                pixeldrain_upload_id,
                file_name,
                file_extension,
                file_length,
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

    def add_tokens(self, user_id: int, tokens_to_add: int):
        today = str(datetime.date.today())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT used_tokens FROM tokens WHERE user_id = ? AND date = ?', (user_id, today))
            row = cursor.fetchone()

            if row is None:
                custom_limit = self._get_latest_custom_limit(cursor, user_id)
                cursor.execute('''
                    INSERT INTO tokens (user_id, date, used_tokens, custom_limit)
                    VALUES (?, ?, ?, ?)
                    ''', (user_id, today, tokens_to_add, custom_limit))
            else:
                new_used = row[0] + tokens_to_add
                cursor.execute('''
                    UPDATE tokens
                    SET used_tokens = ?
                    WHERE user_id = ? AND date = ?
                    ''', (new_used, user_id, today))
            conn.commit()

    def can_use_tokens(self, user_id: int, tokens_needed: int, default_limit: int) -> bool:
        today = str(datetime.date.today())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT used_tokens, custom_limit FROM tokens WHERE user_id = ? AND date = ?', (user_id, today))
            row = cursor.fetchone()

            if row is None:
                used_today = 0
                custom_limit = self._get_latest_custom_limit(cursor, user_id)
            else:
                used_today, custom_limit = row

            limit = custom_limit if custom_limit is not None else default_limit

            return (used_today + tokens_needed) <= limit

    def get_token_usage_history(self, user_id: int, days_back: int) -> int:
        date_limit = str(datetime.date.today() - datetime.timedelta(days=days_back))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(used_tokens)
                FROM tokens
                WHERE user_id = ? AND date >= ?
                ''', (user_id, date_limit))

            result = cursor.fetchone()[0]
            return result if result is not None else 0