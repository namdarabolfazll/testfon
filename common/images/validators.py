from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_PIXELS = 40_000_000

from django.core.exceptions import ValidationError
from PIL import Image


ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}



def validate_image(image):
    if image.format not in {"JPEG", "PNG", "WEBP"}:
        raise ValidationError(
            "Unsupported image format. Upload JPEG, PNG, or WebP images."
        )

    if getattr(image, "is_animated", False):
        raise ValidationError(
            "Animated images are not supported."
        )
def validation_error_from_pillow(exc):
    if isinstance(exc, Image.DecompressionBombError):
        return ValidationError("Image is too large to process safely.")
    if isinstance(exc, (Image.DecompressionBombWarning, UnidentifiedImageError, OSError, ValueError)):
        return ValidationError("Upload a valid, non-corrupted image file.")
    return exc
