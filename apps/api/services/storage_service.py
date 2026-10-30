import os
import uuid
from pathlib import Path
from apps.api.utils.image_sanitizer import strip_exif_metadata

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class StorageService:
    def __init__(self, upload_dir: Path = UPLOAD_DIR):
        self.upload_dir = upload_dir

    def store_incident_media(self, file_bytes: bytes, original_filename: str = "upload.jpg") -> str:
        """Sanitize EXIF and persist media file, returning relative accessible URL."""
        if not file_bytes:
            return None
        
        sanitized_bytes = strip_exif_metadata(file_bytes)
        file_ext = Path(original_filename).suffix or ".jpg"
        unique_name = f"report_{uuid.uuid4().hex[:12]}{file_ext}"
        target_path = self.upload_dir / unique_name

        with open(target_path, "wb") as f:
            f.write(sanitized_bytes)

        return f"/uploads/{unique_name}"

storage_service = StorageService()

