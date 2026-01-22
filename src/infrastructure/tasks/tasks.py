from pathlib import Path

from PIL import Image

from src.infrastructure.tasks.exceptions import ImageProcessingError
from src.infrastructure.tasks.factory import celery_app


@celery_app.task(bind=True, name="create_thumbnail", max_retries=3, default_retry_delay=60)
def create_thumbnail(image_path: str, thumbnail_path: str, size: tuple[float, float] = (128, 128)) -> str | None:
    """Create a thumbnail for the given image."""
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            img.thumbnail(size, Image.Resampling.LANCZOS)
            Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(thumbnail_path, quality=90, optimize=True)
            return thumbnail_path

    except Exception:
        raise ImageProcessingError from None
