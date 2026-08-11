from dataclasses import dataclass
from io import BytesIO

from django.core.exceptions import ValidationError
from PIL import Image, ImageOps, UnidentifiedImageError

from .validators import MAX_IMAGE_PIXELS, validate_image, validation_error_from_pillow

Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


@dataclass(frozen=True)
class ProcessedImage:
    content: bytes
    width: int
    height: int
    format: str = "WEBP"


def open_validated_image(file_obj):
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        image = Image.open(file_obj)
        validate_image(image)
        image = ImageOps.exif_transpose(image)
        image.load()
        validate_image(image)
        return image
    except Exception as exc:  # Pillow raises several concrete exceptions for broken files.
        converted = validation_error_from_pillow(exc)
        if isinstance(converted, ValidationError):
            raise converted
        raise


def has_alpha(image):
    if image.mode in ("RGBA", "LA"):
        return True
    if image.mode == "P" and "transparency" in image.info:
        return True
    return "A" in image.getbands()


def normalize_mode(image):
    if has_alpha(image):
        return image.convert("RGBA")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def resize_cover_without_upscale(image, size):
    target_width, target_height = size
    if not target_width or not target_height:
        return image.copy()
    width, height = image.size
    scale = max(target_width / width, target_height / height)
    if scale > 1:
        resized = image.copy()
    else:
        resized = image.resize((max(1, round(width * scale)), max(1, round(height * scale))), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_width) // 2)
    top = max(0, (resized.height - target_height) // 2)
    right = min(resized.width, left + min(target_width, resized.width))
    bottom = min(resized.height, top + min(target_height, resized.height))
    return resized.crop((left, top, right, bottom))


def process_image(file_obj, *, size=None, mode="cover", quality=85, method=6):
    image = normalize_mode(open_validated_image(file_obj))
    if size:
        if mode != "cover":
            raise ValidationError("Unsupported resize mode.")
        image = resize_cover_without_upscale(image, size)
    output = BytesIO()
    image.save(output, format="WEBP", quality=quality, method=method)
    return ProcessedImage(output.getvalue(), image.width, image.height)
