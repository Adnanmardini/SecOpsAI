import time
import os
import psycopg2
from prometheus_client import Gauge, start_http_server
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# METRICS DEFINITIONS
# -----------------------------
NETWORK_FLOWS_TOTAL = Gauge(
    'secopsai_network_flows_total',
    'Total rows in network_flows table'
)

DETECTIONS_TOTAL = Gauge(
    'secopsai_detections_total',
    'Total rows in detection_results table'
)

ALERTS_OPEN = Gauge(
    'secopsai_alerts_open',
    'Open alerts in security_alerts table'
)

ALERTS_CRITICAL = Gauge(
    'secopsai_alerts_critical',
    'Critical severity alerts'
)

AUDIT_LOG_TOTAL = Gauge(
    'secopsai_audit_log_total',
    'Total audit log entries'
)

MODEL_ACCURACY = Gauge(
    'secopsai_model_accuracy',
    'Current model accuracy score'
)

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# -----------------------------
# METRIC COLLECTION
# -----------------------------
def collect_metrics():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM network_flows;")
        NETWORK_FLOWS_TOTAL.set(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM detection_results;")
        DETECTIONS_TOTAL.set(cursor.fetchone()[0])

        cursor.execute("""
            SELECT COUNT(*) 
            FROM security_alerts 
            WHERE status = 'open';
        """)
        ALERTS_OPEN.set(cursor.fetchone()[0])

        cursor.execute("""
            SELECT COUNT(*) 
            FROM security_alerts 
            WHERE severity = 'critical';
        """)
        ALERTS_CRITICAL.set(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM audit_log;")
        AUDIT_LOG_TOTAL.set(cursor.fetchone()[0])

        cursor.execute("""
            SELECT f1_score 
            FROM model_versions 
            WHERE is_production = TRUE 
            ORDER BY deployed_at DESC 
            LIMIT 1;
        """)
        result = cursor.fetchone()

        if result and result[0] is not None:
            MODEL_ACCURACY.set(float(result[0]))
        else:
            MODEL_ACCURACY.set(0.0)

    except Exception as e:
        print(f"Metrics collection error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("Starting PostgreSQL metrics collector on port 8001...")

    start_http_server(8001)

    while True:
        collect_metrics()
        print(f"Metrics collected at {time.strftime('%H:%M:%S')}")
        time.sleep(300)
