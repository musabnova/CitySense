import io
import logging

logger = logging.getLogger(__name__)

def strip_exif_metadata(image_bytes: bytes) -> bytes:
    """Strip all EXIF tags (GPS, camera serials, timestamp) from image buffer."""
    if not image_bytes:
        return b""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        # Copy image data without exif
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)

        output = io.BytesIO()
        image_without_exif.save(output, format="JPEG", quality=85)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"EXIF stripping skipped or failed ({e}); passing raw bytes.")
        return image_bytes

