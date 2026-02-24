
import sqlite3
import os

class DBManager:
    def __init__(self, db_path="data/sunqar.db"):
        if not os.path.exists("data"):
            os.makedirs("data")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                threat_level TEXT,
                scam_type TEXT,
                indicators TEXT,
                ip TEXT,
                legal_articles TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_incident(self, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO incidents (source, threat_level, scam_type, indicators, ip, legal_articles)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('url', 'Upload'),
            data.get('threat_level'),
            data.get('scam_type'),
            ", ".join(data.get('indicators', [])),
            data.get('ip'),
            ", ".join(data.get('legal_articles', []))
        ))
        conn.commit()
        conn.close()

    def get_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM incidents ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_stats(self):
        """Returns real aggregated statistics from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM incidents')
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM incidents WHERE threat_level = 'High'")
        high = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT scam_type) FROM incidents WHERE threat_level = 'High'")
        clusters = cursor.fetchone()[0]

        # Precision: ratio of analyzed incidents with non-null verdicts
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE threat_level IS NOT NULL")
        with_verdict = cursor.fetchone()[0]
        precision = round((with_verdict / total * 100), 1) if total > 0 else 0.0

        conn.close()
        return {
            "total": total,
            "high_threat": high,
            "clusters": clusters,
            "precision": precision,
        }
