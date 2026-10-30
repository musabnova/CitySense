"""
TASK-035: Plain-Language Explainable Priority Rationale Generator
==================================================================
Stage: Stage 2 — Understand / Explainable AI
Objective: Generate human-readable, transparent natural language explanations
           detailing *why* an issue received its specific priority rank.

Implementation: Template-based rationale generation (no LLM required for MVP).
Clearly labelled: [TEMPLATE-BASED RATIONALE - rule-generated explanation]
"""

import logging

logger = logging.getLogger("citysense.explainability")

# ── Priority rank descriptions ───────────────────────────────────────────────
RANK_DESCRIPTIONS = {
    "Priority 1": "Critical",
    "Priority 2": "High",
    "Priority 3": "Medium",
    "Priority 4": "Low / Routine",
}


def generate_rationale(priority_rank: str, priority_score: float, factors: list[dict]) -> str:
    """
    [TEMPLATE-BASED RATIONALE - rule-generated explanation]

    Generate a plain-language rationale string from priority scoring factors.

    Example output:
    "Ranked Priority 1 (Critical). Near St. Jude Primary School (+40).
     Safety hazard keywords detected (+20). 3 linked duplicate reports (+30)."

    Args:
        priority_rank: e.g. "Priority 1"
        priority_score: numeric score (0-100)
        factors: list of dicts with 'name', 'points', 'detail'

    Returns a non-empty rationale string.
    """
    rank_label = RANK_DESCRIPTIONS.get(priority_rank, "Unranked")
    parts = [f"Ranked {priority_rank} ({rank_label})."]

    if not factors:
        parts.append("Standard intake assessment; no elevated risk factors identified.")
    else:
        for factor in factors:
            detail = factor.get("detail", factor.get("name", "Unknown factor"))
            points = factor.get("points", 0)
            parts.append(f"{detail} (+{points}).")

    rationale = " ".join(parts)
    return rationale


def update_report_rationale(report_id: str, db_path: str, priority_result: dict = None) -> dict:
    """
    Load report from DB (or use provided priority_result), generate rationale,
    update priority_rationale column.

    If priority_result is provided (from TASK-034), use its factors directly.
    Otherwise, re-read the report and generate a basic rationale.

    Returns dict with rationale result.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()

        if priority_result and "factors" in priority_result:
            # Use the factors from the priority engine
            rank = priority_result["priority_rank"]
            score = priority_result["priority_score"]
            factors = priority_result["factors"]
        else:
            # Read from DB
            cur.execute(
                "SELECT priority_rank, priority_score FROM reports WHERE id = ?",
                (report_id,),
            )
            row = cur.fetchone()
            if not row:
                return {"error": f"Report {report_id} not found"}
            rank = row["priority_rank"]
            score = float(row["priority_score"])
            factors = []  # No factor details available in DB alone

        rationale = generate_rationale(rank, score, factors)

        cur.execute(
            "UPDATE reports SET priority_rationale = ? WHERE id = ?",
            (rationale, report_id),
        )
        conn.commit()

        logger.info(
            "TASK-035: Rationale generated for report %s: %s",
            report_id, rationale[:120],
        )
        return {
            "report_id": report_id,
            "priority_rationale": rationale,
            "char_count": len(rationale),
            "mode": "template-based-rule-generated",
        }
    finally:
        conn.close()

