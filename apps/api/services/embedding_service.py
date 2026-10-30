"""
TASK-029: Text & Multi-Modal Vector Embedding Generation Worker
================================================================
Stage: Stage 2 — Understand / AI Pipeline
Objective: Generate 768-dimensional dense vector from incident description.

Implementation: Deterministic hash-based embedding generator.
Since sentence-transformers (all-mpnet-base-v2) requires native C extensions
that are blocked by the host Application Control policy, this module provides
a deterministic hash-based 768-dim float vector from description text.

Clearly labelled: [MOCK EMBEDDING - deterministic hash-based]
When sentence-transformers becomes available, the real model activates automatically.
"""

import hashlib
import json
import math
import logging
from typing import Optional

logger = logging.getLogger("citysense.embedding")

EMBEDDING_DIM = 768

# ── Attempt real model (graceful fallback) ────────────────────────────────────
_REAL_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    _REAL_MODEL = SentenceTransformer("all-mpnet-base-v2")
    logger.info("Loaded real embedding model: all-mpnet-base-v2")
except Exception:
    logger.warning(
        "[MOCK EMBEDDING - deterministic hash-based] "
        "sentence-transformers unavailable; using hash-based 768-dim vectors."
    )


def _normalize_vector(vec: list[float]) -> list[float]:
    """L2-normalize a vector to unit length."""
    magnitude = math.sqrt(sum(x * x for x in vec))
    if magnitude == 0:
        return vec
    return [x / magnitude for x in vec]


def generate_embedding(text: str) -> list[float]:
    """
    Generate a 768-dimensional embedding vector from text.

    Returns a list of 768 floats (L2-normalized).

    If sentence-transformers is available, uses the real model.
    Otherwise, generates a deterministic hash-based mock embedding.
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIM

    if _REAL_MODEL is not None:
        embedding = _REAL_MODEL.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    # ── MOCK: Deterministic feature-hashed token & subword embedding ─────────
    # Subword/bag-of-words hashing gives high cosine similarity for texts
    # sharing municipal problem terminology, without requiring a neural model.
    import re
    words = re.findall(r"\b\w+\b", text.lower())
    tokens = list(words)
    clean = re.sub(r"\s+", " ", text.lower().strip())
    for i in range(len(clean) - 3):
        tokens.append(clean[i:i+4])

    raw_floats = [0.0] * EMBEDDING_DIM
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        idx = h % EMBEDDING_DIM
        sign = 1.0 if (h >> 16) & 1 else -1.0
        raw_floats[idx] += sign

    return _normalize_vector(raw_floats)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors. Returns value in [-1, 1]."""
    if len(vec_a) != len(vec_b) or len(vec_a) == 0:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def cosine_distance(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine distance = 1 - cosine_similarity. Range [0, 2]."""
    return 1.0 - cosine_similarity(vec_a, vec_b)


def update_report_embedding(report_id: str, db_path: str) -> dict:
    """
    Load report from DB, generate embedding, store as JSON in description_embedding_json.
    Returns dict with embedding metadata.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT raw_description FROM reports WHERE id = ?", (report_id,))
        row = cur.fetchone()
        if not row:
            return {"error": f"Report {report_id} not found"}

        text = row["raw_description"] or ""
        embedding = generate_embedding(text)
        embedding_json = json.dumps(embedding)

        cur.execute(
            "UPDATE reports SET description_embedding_json = ? WHERE id = ?",
            (embedding_json, report_id),
        )
        conn.commit()

        mode = "real:all-mpnet-base-v2" if _REAL_MODEL else "mock:hash-based-768d"
        logger.info(
            "TASK-029: Embedding generated for report %s (mode=%s, dims=%d)",
            report_id, mode, len(embedding),
        )
        return {
            "report_id": report_id,
            "embedding_dim": len(embedding),
            "mode": mode,
            "status": "populated",
        }
    finally:
        conn.close()

