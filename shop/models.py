from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse

from common.images import ProcessedImageField

PRODUCT_IMAGE_VARIANTS = {
    "detail": {"size": (1200, 1200), "mode": "cover"},
    "card": {"size": (600, 600), "mode": "cover"},
    "thumb": {"size": (300, 300), "mode": "cover"},
}
CATEGORY_IMAGE_VARIANTS = {
    "card": {"size": (640, 480), "mode": "cover"},
}
GALLERY_IMAGE_VARIANTS = {
    "detail": {"size": (1200, 1200), "mode": "cover"},
    "thumb": {"size": (300, 300), "mode": "cover"},
}


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)
    image = ProcessedImageField(upload_to="categories/", variants=CATEGORY_IMAGE_VARIANTS, blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, related_name="children", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)

    class Meta:
        ordering = ("sort_order", "name")
        indexes = [models.Index(fields=("slug",)), models.Index(fields=("parent", "sort_order")), models.Index(fields=("is_active",))]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name

    @property
    def url(self):
        return reverse("shop:categories") + f"?category={self.slug}"

    def clean(self):
        super().clean()
        parent = self.parent
        while parent is not None:
            if parent.pk == self.pk:
                raise ValidationError({"parent": "A category cannot be its own ancestor."})
            parent = parent.parent


class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    categories = models.ManyToManyField(Category, related_name="secondary_products", blank=True)
    short_description = models.CharField(max_length=320, blank=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)

    class Meta:
        ordering = ("-created_at", "name")
        indexes = [models.Index(fields=("slug",)), models.Index(fields=("category", "status")), models.Index(fields=("is_active", "is_featured"))]

    def __str__(self):
        return self.name

    @property
    def image(self):
        primary = self.images.filter(is_primary=True).first() or self.images.first()
        return primary.image if primary else None

    @property
    def gallery(self):
        return self.images.all()

    @property
    def price(self):
        variant = self.variants.filter(is_active=True).order_by("price").first()
        return variant.price if variant else None

    @property
    def discount_price(self):
        variant = self.variants.filter(is_active=True, compare_at_price__gt=models.F("price")).order_by("price").first()
        return variant.price if variant else None

    @property
    def in_stock(self):
        return self.variants.filter(is_active=True, stock_quantity__gt=0).exists()


class Attribute(TimeStampedModel):
    class Type(models.TextChoices):
        TEXT = "text", "Text"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        CHOICE = "choice", "Choice"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    type = models.CharField(max_length=16, choices=Type.choices)
    unit = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    is_filterable = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")
        indexes = [models.Index(fields=("slug",)), models.Index(fields=("type", "is_active"))]

    def __str__(self):
        return self.name


class AttributeValue(TimeStampedModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="choices")
    value = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("attribute", "sort_order", "value")
        constraints = [models.UniqueConstraint(fields=("attribute", "slug"), name="uniq_attribute_value_slug")]

    def clean(self):
        if self.attribute_id and self.attribute.type != Attribute.Type.CHOICE:
            raise ValidationError({"attribute": "Attribute values are only valid for choice attributes."})

    def __str__(self):
        return f"{self.attribute}: {self.value}"


class CategoryAttribute(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_attributes")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="category_attributes")
    is_required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order",)
        constraints = [models.UniqueConstraint(fields=("category", "attribute"), name="uniq_category_attribute")]

    def __str__(self):
        return f"{self.category} - {self.attribute}"


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name="product_values")
    choice_value = models.ForeignKey(AttributeValue, on_delete=models.PROTECT, blank=True, null=True)
    value_text = models.CharField(max_length=320, blank=True)
    value_integer = models.IntegerField(blank=True, null=True)
    value_decimal = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("product", "attribute"), name="uniq_product_attribute")]

    def clean(self):
        if self.product_id and self.attribute_id:
            allowed = CategoryAttribute.objects.filter(category=self.product.category, attribute=self.attribute).exists()
            if not allowed:
                raise ValidationError({"attribute": "This attribute is not allowed for the product category."})
        fields = [self.choice_value_id, self.value_text or None, self.value_integer, self.value_decimal, self.value_boolean]
        if sum(value is not None for value in fields) != 1:
            raise ValidationError("Provide exactly one typed value.")
        if self.attribute_id:
            expected = self.attribute.type
            mapping = {
                Attribute.Type.CHOICE: self.choice_value_id,
                Attribute.Type.TEXT: self.value_text or None,
                Attribute.Type.INTEGER: self.value_integer,
                Attribute.Type.DECIMAL: self.value_decimal,
                Attribute.Type.BOOLEAN: self.value_boolean,
            }
            if mapping[expected] is None:
                raise ValidationError("Typed value does not match the attribute type.")
            if self.choice_value_id and self.choice_value.attribute_id != self.attribute_id:
                raise ValidationError({"choice_value": "Choice value must belong to the selected attribute."})

    def __str__(self):
        return f"{self.product} - {self.attribute}"


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")
        constraints = [models.UniqueConstraint(fields=("product", "slug"), name="uniq_product_option_slug")]

    def __str__(self):
        return f"{self.product} - {self.name}"


class ProductOptionValue(models.Model):
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("option", "sort_order", "value")
        constraints = [models.UniqueConstraint(fields=("option", "slug"), name="uniq_product_option_value_slug")]

    def __str__(self):
        return f"{self.option.name}: {self.value}"


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=80, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("product", "sku")
        indexes = [models.Index(fields=("sku",)), models.Index(fields=("product", "is_active"))]
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name="product_variant_price_non_negative"),
            models.CheckConstraint(check=Q(compare_at_price__isnull=True) | Q(compare_at_price__gte=0), name="product_variant_compare_price_non_negative"),
        ]

    def clean(self):
        if self.compare_at_price is not None and self.compare_at_price < self.price:
            raise ValidationError({"compare_at_price": "Compare-at price cannot be lower than price."})

    def __str__(self):
        return self.sku


class VariantOptionValue(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="option_values")
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name="variant_values")
    value = models.ForeignKey(ProductOptionValue, on_delete=models.PROTECT, related_name="variant_values")

    class Meta:
        constraints = [models.UniqueConstraint(fields=("variant", "option"), name="uniq_variant_option")]

    def clean(self):
        if self.variant_id and self.option_id and self.option.product_id != self.variant.product_id:
            raise ValidationError({"option": "Option must belong to the variant product."})
        if self.value_id and self.option_id and self.value.option_id != self.option_id:
            raise ValidationError({"value": "Option value must belong to the selected option."})
        if self.variant_id:
            pairs = {ov.option_id: ov.value_id for ov in self.variant.option_values.exclude(pk=self.pk)}
            if self.option_id:
                pairs[self.option_id] = self.value_id
            current = sorted(pairs.items())
            for variant in self.variant.product.variants.exclude(pk=self.variant_id):
                other = sorted(variant.option_values.values_list("option_id", "value_id"))
                if other == current:
                    raise ValidationError("This variant option combination already exists for the product.")

    def __str__(self):
        return f"{self.variant}: {self.option}={self.value}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, related_name="images", blank=True, null=True)
    image = ProcessedImageField(upload_to="products/gallery/", variants=GALLERY_IMAGE_VARIANTS)
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")
        indexes = [models.Index(fields=("product", "sort_order")), models.Index(fields=("variant",))]
        constraints = [models.UniqueConstraint(fields=("product",), condition=Q(is_primary=True), name="uniq_primary_image_per_product")]

    @property
    def url(self):
        return self.image.url if self.image else ""

    def variant_url(self, variant):
        return self.image.variant_url(variant) if self.image else ""

    def clean(self):
        if self.variant_id and self.product_id and self.variant.product_id != self.product_id:
            raise ValidationError({"variant": "Image variant must belong to the same product."})

    def __str__(self):
        return self.alt_text or f"Image for {self.product}"
