"""
TASK-031: Concise One-Sentence Multi-Modal Summarization Worker
================================================================
Stage: Stage 2 — Understand / AI Pipeline
Objective: Generate a single-sentence executive summary (< 200 chars, < 25 words)
           for rapid scanning.

Implementation: Rule-based text extraction and compression.
Clearly labelled: [RULE-BASED SUMMARY - extractive compression]
"""

import re
import logging

logger = logging.getLogger("citysense.summary")

# Maximum summary constraints from spec
MAX_CHARS = 200
MAX_WORDS = 25


def _clean_text(text: str) -> str:
    """Remove excess whitespace and normalize."""
    text = re.sub(r"\s+", " ", text.strip())
    return text


def _extract_first_sentence(text: str) -> str:
    """Extract the first sentence from the text."""
    # Split on sentence-ending punctuation
    match = re.match(r"^(.+?[.!?])\s", text)
    if match:
        return match.group(1).strip()
    # If no sentence boundary, return the first clause
    match = re.match(r"^(.+?[,;:])\s", text)
    if match:
        return match.group(1).strip().rstrip(",;:")
    return text


def _compress_to_limit(text: str) -> str:
    """Compress text to fit within MAX_WORDS and MAX_CHARS."""
    words = text.split()
    if len(words) > MAX_WORDS:
        words = words[:MAX_WORDS]
    result = " ".join(words)
    if len(result) > MAX_CHARS:
        result = result[:MAX_CHARS - 3].rsplit(" ", 1)[0] + "..."
    return result


def _remove_filler_phrases(text: str) -> str:
    """Remove common filler phrases to make the summary more concise."""
    fillers = [
        r"\bI would like to report\b",
        r"\bI want to report\b",
        r"\bI am writing to inform\b",
        r"\bI wish to report\b",
        r"\bPlease note that\b",
        r"\bIt should be noted that\b",
        r"\bThere is a?\b",
        r"\bIt has been observed that\b",
        r"\bI noticed that\b",
        r"\bI am reporting\b",
        r"\bThis is to inform you\b",
        r"\bKindly look into\b",
        r"\bPlease look into\b",
        r"\bImmediate attention needed\b",
        r"\bUrgent attention required\b",
    ]
    result = text
    for filler in fillers:
        result = re.sub(filler, "", result, flags=re.IGNORECASE)
    # Clean up
    result = re.sub(r"\s+", " ", result).strip()
    result = re.sub(r"^[.,;:\s]+", "", result)  # Remove leading punctuation
    return result


def generate_summary(raw_description: str) -> str:
    """
    [RULE-BASED SUMMARY - extractive compression]

    Generate a concise one-sentence executive summary from verbose complaint text.

    Strategy:
    1. Clean and normalize text
    2. Remove filler phrases
    3. Extract the first sentence (core issue statement)
    4. Compress to < 25 words and < 200 chars

    Returns a string summary.
    """
    if not raw_description or not raw_description.strip():
        return "No description provided."

    text = _clean_text(raw_description)
    text = _remove_filler_phrases(text)

    if not text:
        return raw_description[:MAX_CHARS]

    # Extract core sentence
    first_sentence = _extract_first_sentence(text)

    # Compress
    summary = _compress_to_limit(first_sentence)

    # Ensure it starts with a capital letter
    if summary and summary[0].islower():
        summary = summary[0].upper() + summary[1:]

    # Ensure it ends with a period
    if summary and not summary.endswith((".", "!", "?")):
        if summary.endswith("..."):
            pass
        else:
            summary += "."

    return summary


def update_report_summary(report_id: str, db_path: str) -> dict:
    """
    Load report from DB, generate summary, update concise_summary.
    Returns dict with summary result.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT raw_description FROM reports WHERE id = ?",
            (report_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": f"Report {report_id} not found"}

        raw_desc = row["raw_description"] or ""
        summary = generate_summary(raw_desc)

        cur.execute(
            "UPDATE reports SET concise_summary = ? WHERE id = ?",
            (summary, report_id),
        )
        conn.commit()

        word_count = len(summary.split())
        char_count = len(summary)
        logger.info(
            "TASK-031: Summary generated for report %s (%d words, %d chars): %s",
            report_id, word_count, char_count, summary,
        )
        return {
            "report_id": report_id,
            "concise_summary": summary,
            "word_count": word_count,
            "char_count": char_count,
            "within_word_limit": word_count <= MAX_WORDS,
            "within_char_limit": char_count <= MAX_CHARS,
            "mode": "rule-based-extractive-compression",
        }
    finally:
        conn.close()

