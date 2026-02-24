
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
                legal_articles TEXT,
                risk_score INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0,
                registrar TEXT,
                markers TEXT
            )
        ''')
        # Migration: add new columns to existing databases
        for col, coltype in [("risk_score", "INTEGER DEFAULT 0"),
                              ("confidence", "REAL DEFAULT 0.0"),
                              ("registrar", "TEXT"),
                              ("markers", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE incidents ADD COLUMN {col} {coltype}")
            except Exception:
                pass
        conn.commit()
        conn.close()

    def log_incident(self, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO incidents (source, threat_level, scam_type, indicators, ip, legal_articles, risk_score, confidence, registrar, markers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('url', 'Upload'),
            data.get('threat_level'),
            data.get('scam_type'),
            ", ".join(data.get('indicators', [])),
            data.get('ip'),
            ", ".join(data.get('legal_articles', [])),
            data.get('risk_score', 0),
            data.get('confidence', 0.0),
            data.get('registrar', 'N/A'),
            ", ".join(data.get('markers', []))
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

    def get_network_clusters(self):
        """
        Network Intelligence: finds scam clusters — domains sharing the same IP.
        Returns list of cluster dicts.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ip, GROUP_CONCAT(source, '||'), GROUP_CONCAT(scam_type, '||'), AVG(risk_score), COUNT(*)
            FROM incidents
            WHERE ip IS NOT NULL AND ip != 'N/A' AND threat_level != 'Low'
            GROUP BY ip
            HAVING COUNT(*) >= 1
            ORDER BY COUNT(*) DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        clusters = []
        for row in rows:
            ip, sources, types, avg_score, count = row
            cluster_domains = list(set(s.strip() for s in (sources or '').split('||') if s.strip()))
            cluster_types = list(set(t.strip() for t in (types or '').split('||') if t.strip()))
            clusters.append({
                "shared_ip": ip,
                "domains": cluster_domains,
                "scam_types": cluster_types,
                "avg_risk_score": round(avg_score or 0),
                "count": count,
            })
        return clusters
