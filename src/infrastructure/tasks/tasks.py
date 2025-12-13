from src.infrastructure.tasks.celery_config import celery_app
from PIL import Image
from pathlib import Path


@celery_app.task
def create_thumbnail(image_path: str, thumbnail_path: str, size: tuple[float, float] = (128, 128)) -> str:
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            img.thumbnail(size, Image.Resampling.LANCZOS)
            Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(thumbnail_path, quality=90, optimize=True)

        return thumbnail_path
    except Exception as err:
        raise Exception(err)
