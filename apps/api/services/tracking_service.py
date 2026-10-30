import secrets
import string
from sqlalchemy.orm import Session
from apps.api.models import Report

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Excluded ambiguous characters like 0, O, 1, I

def generate_random_tracking_code() -> str:
    """Generate a format 'CS-XXXX-XXXX' string (12 chars total)."""
    p1 = "".join(secrets.choice(ALPHABET) for _ in range(4))
    p2 = "".join(secrets.choice(ALPHABET) for _ in range(4))
    return f"CS-{p1}-{p2}"

def issue_unique_tracking_id(db: Session, max_retries: int = 5) -> str:
    """Generate a guaranteed unique tracking ID checked against database."""
    for _ in range(max_retries):
        candidate = generate_random_tracking_code()
        exists = db.query(Report).filter(Report.tracking_id == candidate).first()
        if not exists:
            return candidate
    raise RuntimeError("Failed to allocate a unique tracking ID after maximum retries.")

