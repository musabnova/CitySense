"""
TASK-046: Audit Logging Trigger & Immutable History Inspection Service
=======================================================================
Stage: Stage 4: Act / Governance
Objective: Record immutable audit logs for state changes and overrides,
           and provide retrieval for report audit trails.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"


def record_audit_log(
    report_id: str,
    user_id: str,
    action_type: str,
    previous_value: str,
    new_value: str,
    justification: str,
    db_path: str = None
) -> Dict[str, Any]:
    """
    Appends an immutable audit log entry for a report action into report_audit_logs.
    """
    path = db_path or str(DEFAULT_DB_PATH)
    log_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO report_audit_logs (
                id, report_id, user_id, timestamp, action_type,
                previous_value, new_value, justification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            report_id,
            user_id,
            now_iso,
            action_type,
            str(previous_value),
            str(new_value),
            str(justification)
        ))
        conn.commit()
    finally:
        conn.close()

    return {
        "id": log_id,
        "report_id": report_id,
        "user_id": user_id,
        "timestamp": now_iso,
        "action_type": action_type,
        "previous_value": str(previous_value),
        "new_value": str(new_value),
        "justification": str(justification)
    }


def get_report_audit_trail(report_id: str, db_path: str = None) -> List[Dict[str, Any]]:
    """
    Retrieves chronological history of audit events for a given report ID.
    """
    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, report_id, user_id, timestamp, action_type,
                   previous_value, new_value, justification
            FROM report_audit_logs
            WHERE report_id = ?
            ORDER BY timestamp ASC
        """, (report_id,))
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()

