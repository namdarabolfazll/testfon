# Image processing

The project uses `common.images.ProcessedImageField` for catalog images. The field accepts JPEG, PNG, and WebP uploads, validates the actual image content with Pillow, applies EXIF orientation, rejects animated/corrupted/unsafe images, and stores WebP output through Django's configured storage backend.

## Variants

Variants are declared on the field and saved next to the main image:

```python
image = ProcessedImageField(
    upload_to="products/gallery/",
    variants={
        "detail": {"size": (1200, 1200), "mode": "cover"},
        "thumb": {"size": (300, 300), "mode": "cover"},
    },
    quality=85,
    method=6,
)
```

The original upload is not stored separately. The main field value is an optimized WebP, and variants use predictable names such as `plate__thumb.webp`.

## Template access

Use the main URL for default display:

```django
{{ product.image.url }}
```

Use the `image_variant` filter for optimized variants:

```django
{% load image_variants %}
<img src="{{ product.image|image_variant:'card' }}" width="600" height="600">
```

Python code can call:

```python
product.image.variant_url("card")
```

## Current catalog variants

- Product card: `600x600`, cover crop.
- Product detail: `1200x1200`, cover crop.
- Product thumbnail/cart: `300x300`, cover crop.
- Category card: `640x480`, cover crop.
- Product gallery detail: `1200x1200`, cover crop.
- Product gallery thumb: `300x300`, cover crop.

Small images are never upscaled.

## Celery

Celery is not required now because image uploads are expected to be admin/catalog operations and only a small number of useful variants are generated. The processing logic lives in `common/images/processing.py`, so a future Celery task can call the same service without changing catalog models or templates.
