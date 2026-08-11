from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_PIXELS = 40_000_000


def validate_image(image, *, allowed_formats=None, reject_animated=True):
    allowed_formats = allowed_formats or ALLOWED_FORMATS
    image_format = (image.format or "").upper()
    if image_format not in allowed_formats:
        raise ValidationError("Unsupported image format. Upload JPEG, PNG, or WebP images.")
    if reject_animated and getattr(image, "is_animated", False):
        raise ValidationError("Animated images are not supported.")
    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValidationError("Invalid image dimensions.")
    if width * height > MAX_IMAGE_PIXELS:
        raise ValidationError("Image is too large to process safely.")


def validation_error_from_pillow(exc):
    if isinstance(exc, Image.DecompressionBombError):
        return ValidationError("Image is too large to process safely.")
    if isinstance(exc, (Image.DecompressionBombWarning, UnidentifiedImageError, OSError, ValueError)):
        return ValidationError("Upload a valid, non-corrupted image file.")
    return exc
