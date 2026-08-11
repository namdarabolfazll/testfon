from pathlib import PurePosixPath

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageField, ImageFieldFile
from django.utils.text import get_valid_filename, slugify

from .processing import process_image


def normalize_variants(variants):
    normalized = {}
    for name, config in (variants or {}).items():
        if isinstance(config, tuple):
            config = {"size": config, "mode": "cover"}
        size = tuple(config.get("size") or ())
        if len(size) != 2:
            raise ValueError("Image variant size must be a two-item tuple.")
        normalized[name] = {"size": size, "mode": config.get("mode", "cover")}
    return normalized


def safe_webp_name(name):
    path = PurePosixPath(str(name).replace("\\", "/"))
    stem = path.stem or "image"
    ascii_stem = slugify(stem) or get_valid_filename(stem).rsplit(".", 1)[0] or "image"
    return f"{ascii_stem}.webp"


def variant_name(base_name, variant):
    path = PurePosixPath(base_name)
    return str(path.with_name(f"{path.stem}__{variant}.webp"))


class ProcessedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        if content is not None:
            base_name = safe_webp_name(name)
            processed = process_image(content, quality=self.field.quality, method=self.field.method)
            content = ContentFile(processed.content, name=base_name)
            name = base_name
            super().save(name, content, save=save)
            self._save_variants(name)
            return
        super().save(name, content, save=save)

    def _save_variants(self, base_name):
        if not self.name:
            return
        self.open("rb")
        try:
            source = self.file
            for variant, config in self.field.variants.items():
                source.seek(0)
                processed = process_image(
                    source,
                    size=config["size"],
                    mode=config["mode"],
                    quality=self.field.quality,
                    method=self.field.method,
                )
                name = variant_name(self.name, variant)
                if self.storage.exists(name):
                    self.storage.delete(name)
                self.storage.save(name, ContentFile(processed.content, name=PurePosixPath(name).name))
        finally:
            self.close()

    def variant_url(self, variant):
        if variant not in self.field.variants:
            raise ValueError(f"Unknown image variant: {variant}")
        if not self.name:
            return ""
        return self.storage.url(variant_name(self.name, variant))


class ProcessedImageField(ImageField):
    attr_class = ProcessedImageFieldFile

    def __init__(self, *args, variants=None, quality=85, method=6, **kwargs):
        self.variants = normalize_variants(variants)
        self.quality = quality
        self.method = method
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["variants"] = self.variants
        kwargs["quality"] = self.quality
        kwargs["method"] = self.method
        return name, path, args, kwargs

    def clean(self, value, model_instance):
        file_obj = super().clean(value, model_instance)
        if file_obj and hasattr(file_obj, "file"):
            try:
                process_image(file_obj.file, quality=self.quality, method=self.method)
            except ValidationError:
                raise
        return file_obj
