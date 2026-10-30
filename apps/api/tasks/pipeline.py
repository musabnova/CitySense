"""
TASK-036: Orchestrated Ingestion Pipeline Task & End-to-End Understand Test
============================================================================
Stage: Stage 2 — Understand / Verification
Objective: Assemble the complete pipeline executing Tasks 029→035 in sequence
           for every incoming report.

Pipeline order:
  1. TASK-029: Generate text embedding
  2. TASK-030: Verify/correct category
  3. TASK-031: Generate concise summary
  4. TASK-032/033: Detect & consolidate duplicates
  5. TASK-034: Calculate priority score
  6. TASK-035: Generate priority rationale
  7. Transition status: Submitted → Under Review
"""

import logging
import time

logger = logging.getLogger("citysense.pipeline")


def process_incident_report_task(report_id: str, db_path: str = None) -> dict:
    """
    Execute the full AI understanding pipeline for a single report.

    Runs Tasks 029-035 in sequence:
    1. Embedding generation
    2. Category verification
    3. Summary generation
    4. Duplicate detection & consolidation
    5. Priority scoring
    6. Rationale generation
    7. Status transition: Submitted → Under Review

    Args:
        report_id: UUID of the report to process
        db_path: Path to SQLite database file

    Returns dict with pipeline results and timing.
    """
    import sqlite3
    from pathlib import Path

    if db_path is None:
        db_path = str(Path(__file__).resolve().parent.parent.parent.parent / "citysense.db")

    start_time = time.monotonic()
    results = {}
    errors = []

    # ── Step 1: TASK-029 — Generate embedding ────────────────────────────
    try:
        from apps.api.services.embedding_service import update_report_embedding
        results["embedding"] = update_report_embedding(report_id, db_path)
    except Exception as e:
        errors.append(f"embedding: {e}")
        results["embedding"] = {"error": str(e)}

    # ── Step 2: TASK-030 — Verify/correct category ──────────────────────
    try:
        from apps.api.services.category_service import update_report_category
        results["category"] = update_report_category(report_id, db_path)
    except Exception as e:
        errors.append(f"category: {e}")
        results["category"] = {"error": str(e)}

    # ── Step 3: TASK-031 — Generate summary ─────────────────────────────
    try:
        from apps.api.services.summary_service import update_report_summary
        results["summary"] = update_report_summary(report_id, db_path)
    except Exception as e:
        errors.append(f"summary: {e}")
        results["summary"] = {"error": str(e)}

    # ── Step 4: TASK-032/033 — Duplicate detection & consolidation ──────
    try:
        from apps.api.services.duplicate_service import consolidate_duplicate
        results["duplicate"] = consolidate_duplicate(report_id, db_path)
    except Exception as e:
        errors.append(f"duplicate: {e}")
        results["duplicate"] = {"error": str(e)}

    # ── Step 5: TASK-034 — Priority scoring ─────────────────────────────
    try:
        from apps.api.services.priority_engine import update_report_priority
        results["priority"] = update_report_priority(report_id, db_path)
    except Exception as e:
        errors.append(f"priority: {e}")
        results["priority"] = {"error": str(e)}

    # ── Step 6: TASK-035 — Rationale generation ─────────────────────────
    try:
        from apps.api.services.explainability_service import update_report_rationale
        priority_result = results.get("priority", {})
        results["rationale"] = update_report_rationale(
            report_id, db_path, priority_result=priority_result
        )
    except Exception as e:
        errors.append(f"rationale: {e}")
        results["rationale"] = {"error": str(e)}

    # ── Step 7: Transition status Submitted → Under Review ──────────────
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            """UPDATE reports
               SET lifecycle_status = 'Under Review',
                   updated_at = datetime('now')
               WHERE id = ? AND lifecycle_status = 'Submitted'""",
            (report_id,),
        )
        conn.commit()
        status_updated = cur.rowcount > 0
        conn.close()
        results["status_transition"] = {
            "from": "Submitted",
            "to": "Under Review",
            "updated": status_updated,
        }
    except Exception as e:
        errors.append(f"status_transition: {e}")
        results["status_transition"] = {"error": str(e)}

    elapsed = time.monotonic() - start_time

    # Collect final state for the API response
    final_state = {}
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT lifecycle_status, priority_rank, priority_score,
                      verified_category, concise_summary, priority_rationale,
                      is_duplicate, master_ticket_id
               FROM reports WHERE id = ?""",
            (report_id,),
        )
        row = cur.fetchone()
        if row:
            final_state = dict(row)
        conn.close()
    except Exception:
        pass

    pipeline_result = {
        "report_id": report_id,
        "pipeline_status": "completed" if not errors else "completed_with_errors",
        "elapsed_seconds": round(elapsed, 3),
        "steps": results,
        "errors": errors,
        # Expose final state for API response
        "lifecycle_status": final_state.get("lifecycle_status", "Submitted"),
        "priority_rank": final_state.get("priority_rank", "Priority 3"),
        "priority_score": float(final_state.get("priority_score", 0)),
        "verified_category": final_state.get("verified_category", ""),
        "concise_summary": final_state.get("concise_summary", ""),
    }

    logger.info(
        "TASK-036: Pipeline completed for report %s in %.3fs (%d errors)",
        report_id, elapsed, len(errors),
    )
    return pipeline_result

