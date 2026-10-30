"""
TASK-030: Automated Category Verification & Correction Worker
==============================================================
Stage: Stage 2 — Understand / AI Pipeline
Objective: Validate citizen-selected categories and correct misclassifications.

Implementation: Keyword-based rule classifier (no LLM required for MVP).
Maps complaint text keywords to verified municipal categories.
Clearly labelled: [RULE-BASED CLASSIFIER - keyword matching]
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("citysense.category")

# ── Verified Municipal Category Taxonomy ─────────────────────────────────────
VALID_CATEGORIES = [
    "Waterlogging & Drainage",
    "Road Failure & Potholes",
    "Waste Management",
    "Street Lighting",
    "Public Utilities",
]

# ── Keyword → Category mapping ──────────────────────────────────────────────
# Each category has a weighted set of keywords. The category with the highest
# keyword match score wins.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Waterlogging & Drainage": [
        "water", "flood", "flooding", "waterlog", "waterlogging", "drain",
        "drainage", "clog", "clogged", "overflow", "overflowing", "sewage",
        "sewer", "stagnant", "standing water", "knee-deep", "ankle-deep",
        "puddle", "submerged", "inundated", "rainwater", "storm drain",
        "gutter", "blocked drain", "monsoon",
    ],
    "Road Failure & Potholes": [
        "pothole", "road", "asphalt", "pavement", "crack", "cracked",
        "broken road", "road damage", "road failure", "road surface",
        "tar", "bitumen", "manhole", "sinkhole", "cave-in", "road cave",
        "tire damage", "vehicle damage", "bumpy", "uneven road",
        "road repair", "road breaking", "road collapse",
    ],
    "Waste Management": [
        "garbage", "trash", "waste", "litter", "rubbish", "dump",
        "dumping", "refuse", "debris", "bin", "dumpster", "pile",
        "rotting", "stench", "smell", "odor", "odour", "decomposing",
        "overflowing bin", "waste pile", "illegal dumping", "trash heap",
        "sanitation", "cleanup", "unsanitary",
    ],
    "Street Lighting": [
        "light", "lighting", "lamp", "lamppost", "streetlight", "streetlights",
        "street light", "street lights", "lights", "lamps", "bulbs",
        "dark", "darkness", "no light", "broken light", "flickering", "dim",
        "bulb", "LED", "illumination", "night", "visibility", "unsafe dark", "unlit",
    ],
    "Public Utilities": [
        "electric", "electrical", "wire", "wiring", "cable", "cables", "power",
        "transformer", "pole", "utility", "water supply", "water pipe", "water main",
        "pipe burst", "pipe crack", "pipes", "pipe", "gas", "gas leak",
        "internet", "telephone", "optical fiber", "fiber", "fiber cables",
        "hydrant", "fire hydrant", "conduit", "voltage", "electrocution", "spark",
        "live wire", "exposed wire",
    ],
}


def _score_category(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    score = 0
    for kw in keywords:
        # Use word boundary matching for single words, substring for phrases
        if " " in kw:
            if kw.lower() in text_lower:
                score += 2  # Phrase matches get bonus weight
        else:
            pattern = rf"\b{re.escape(kw.lower())}\b"
            if re.search(pattern, text_lower):
                score += 1
    return score


def verify_category(raw_description: str, user_category: Optional[str] = None) -> str:
    """
    [RULE-BASED CLASSIFIER - keyword matching]

    Analyze complaint text and return the verified municipal category.
    If the user-selected category matches the text analysis, it is confirmed.
    If a better category is found, the correction is returned.

    Returns one of the 5 valid categories.
    """
    if not raw_description or not raw_description.strip():
        return user_category if user_category in VALID_CATEGORIES else VALID_CATEGORIES[0]

    # Score each category
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = _score_category(raw_description, keywords)

    # Find best match
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # If no keywords matched at all, trust the user's category
    if best_score == 0:
        if user_category in VALID_CATEGORIES:
            return user_category
        return VALID_CATEGORIES[0]  # Default fallback

    # If user category matches the best, confirm it
    if user_category == best_category:
        logger.info(
            "TASK-030: Category confirmed: '%s' (score=%d)",
            best_category, best_score,
        )
        return best_category

    # Correction: user category doesn't match text analysis
    user_score = scores.get(user_category, 0) if user_category else 0

    # Only override if classifier is meaningfully more confident
    if best_score > user_score:
        logger.info(
            "TASK-030: Category corrected: '%s' → '%s' (scores: %d vs %d)",
            user_category, best_category, user_score, best_score,
        )
        return best_category
    else:
        return user_category if user_category in VALID_CATEGORIES else best_category


def update_report_category(report_id: str, db_path: str) -> dict:
    """
    Load report from DB, verify/correct category, update verified_category.
    Returns dict with verification result.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT raw_description, user_category, verified_category FROM reports WHERE id = ?",
            (report_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": f"Report {report_id} not found"}

        raw_desc = row["raw_description"] or ""
        user_cat = row["user_category"]
        old_verified = row["verified_category"]

        new_verified = verify_category(raw_desc, user_cat)

        cur.execute(
            "UPDATE reports SET verified_category = ? WHERE id = ?",
            (new_verified, report_id),
        )
        conn.commit()

        corrected = new_verified != user_cat
        logger.info(
            "TASK-030: Report %s — user='%s', verified='%s', corrected=%s",
            report_id, user_cat, new_verified, corrected,
        )
        return {
            "report_id": report_id,
            "user_category": user_cat,
            "verified_category": new_verified,
            "was_corrected": corrected,
            "mode": "rule-based-keyword-classifier",
        }
    finally:
        conn.close()

