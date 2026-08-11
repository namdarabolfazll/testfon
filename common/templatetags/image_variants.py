from django import template

register = template.Library()


@register.filter
def image_variant(image, variant):
    if not image:
        return ""
    if hasattr(image, "variant_url"):
        return image.variant_url(variant)
    return getattr(image, "url", "")
