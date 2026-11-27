import uuid
import os
import io
from PIL import Image, UnidentifiedImageError

from app.core.config import settings

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_BYTES = 5 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
# Evita "bombas" de imagem: arquivos pequenos que viram imagens gigantes na memória.
Image.MAX_IMAGE_PIXELS = 40_000_000


class InvalidImage(ValueError):
    """O arquivo enviado não é uma foto aceita. A mensagem pode ser mostrada ao usuário."""


def _open_image(file_bytes: bytes) -> Image.Image:
    if len(file_bytes) > MAX_BYTES:
        raise InvalidImage("Foto muito grande. Máximo 5MB.")
    # O tipo informado pelo navegador pode ser falso, então o conteúdo é conferido aqui.
    try:
        probe = Image.open(io.BytesIO(file_bytes))
        probe.verify()
        img = Image.open(io.BytesIO(file_bytes))
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError, ValueError):
        raise InvalidImage("O arquivo não é uma foto válida. Use JPG, PNG ou WebP.")
    if img.format not in ALLOWED_FORMATS:
        raise InvalidImage("Formato de imagem inválido. Use JPG, PNG ou WebP.")
    return img


def upload_photo(file_bytes: bytes, folder: str = "family") -> tuple[str, str]:
    img = _open_image(file_bytes)
    img.thumbnail((800, 800), Image.LANCZOS)

    # A foto é sempre regravada: isso também apaga dados escondidos, como a localização (EXIF).
    if img.format == "PNG" or img.mode in ("RGBA", "LA", "P"):
        fmt, ext = "PNG", "png"
    else:
        fmt, ext = "JPEG", "jpg"
        img = img.convert("RGB")
    key = f"{folder}/{uuid.uuid4()}.{ext}"

    path = os.path.join(UPLOAD_DIR, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    buffer = io.BytesIO()
    img.save(buffer, format=fmt, quality=85)
    with open(path, "wb") as f:
        f.write(buffer.getvalue())

    url = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/uploads/{key}"
    return url, key


def delete_photo(key: str) -> None:
    path = os.path.join(UPLOAD_DIR, key)
    if os.path.exists(path):
        os.remove(path)
