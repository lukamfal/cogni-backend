import uuid
import os
import io
from PIL import Image

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_photo(file_bytes: bytes, content_type: str, folder: str = "family") -> tuple[str, str]:
    img = Image.open(io.BytesIO(file_bytes))
    img.thumbnail((800, 800), Image.LANCZOS)

    fmt = "JPEG" if "jpeg" in content_type else "PNG"
    ext = "jpg" if fmt == "JPEG" else "png"
    key = f"{folder}/{uuid.uuid4()}.{ext}"

    path = os.path.join(UPLOAD_DIR, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    buffer = io.BytesIO()
    img.save(buffer, format=fmt, quality=85)
    buffer.seek(0)

    with open(path, "wb") as f:
        f.write(buffer.read())

    url = f"http://localhost:8000/uploads/{key}"
    return url, key


def delete_photo(key: str) -> None:
    path = os.path.join(UPLOAD_DIR, key)
    if os.path.exists(path):
        os.remove(path)