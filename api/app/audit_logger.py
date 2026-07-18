# === api/app/audit_logger.py — Hash-Chained Audit Log ===

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secopsai:secopsai@localhost:5432/secopsai"
)

_last_entry_hash = "GENESIS"  # Hash chain seed


def _get_connection():
    """Return a PostgreSQL connection."""
    return psycopg2.connect(DATABASE_URL)


def log_event(
    endpoint:      str,
    method:        str,
    user_id:       str,
    response_code: int,
    detail:        str = ""
) -> None:
    """
    Append one entry to the hash-chained audit log.
    STRIDE T06 mitigation: every entry contains SHA-256 of prior entry.
    The PostgreSQL append-only rule prevents deletion.
    """
    global _last_entry_hash

    entry_id  = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build the entry payload for hashing
    entry_data = json.dumps({
        "entry_id":       entry_id,
        "timestamp":      timestamp,
        "endpoint":       endpoint,
        "method":         method,
        "user_id":        user_id,
        "response_code":  response_code,
        "detail":         detail,
        "prev_hash":      _last_entry_hash,
    }, sort_keys=True)

    # SHA-256 of this entry
    entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()

    try:
        conn = _get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit_log (
                    entry_id, endpoint, http_method, user_id,
                    response_code, detail,
                    prev_entry_hash, entry_hash, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entry_id, endpoint, method, user_id,
                response_code, detail,
                _last_entry_hash, entry_hash, timestamp
            ))
            conn.commit()

        # Update chain pointer
        _last_entry_hash = entry_hash

    except Exception as e:
        # Never let audit log failure crash the API
        import logging
        logging.getLogger("secopsai.audit").error(f"Audit log write failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def get_recent_events(limit: int = 50) -> List[dict]:
    """Return the most recent audit log entries, newest first."""
    try:
        conn = _get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT entry_id, endpoint, http_method, user_id,
                       response_code, detail, timestamp,
                       LEFT(entry_hash, 16) AS hash_prefix,
                       LEFT(prev_entry_hash, 16) AS prev_hash_prefix
                FROM audit_log
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        if 'conn' in locals():
            conn.close()
