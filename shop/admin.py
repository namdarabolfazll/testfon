from django.contrib import admin

from .models import (
    Attribute,
    AttributeValue,
    Category,
    CategoryAttribute,
    Product,
    ProductAttributeValue,
    ProductImage,
    ProductOption,
    ProductOptionValue,
    ProductVariant,
    VariantOptionValue,
)


class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    extra = 1
    autocomplete_fields = ("attribute",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("parent",)
    ordering = ("sort_order", "name")
    inlines = (CategoryAttributeInline,)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "variant", "is_primary", "sort_order")
    autocomplete_fields = ("variant",)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("sku", "price", "compare_at_price", "stock_quantity", "low_stock_threshold", "barcode", "is_active")


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    autocomplete_fields = ("attribute", "choice_value")


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "is_featured", "is_active", "price", "updated_at")
    list_filter = ("status", "is_featured", "is_active", "category")
    search_fields = ("name", "slug", "short_description", "brand")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "categories")
    ordering = ("-created_at",)
    inlines = (ProductImageInline, ProductVariantInline, ProductAttributeValueInline, ProductOptionInline)


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    prepopulated_fields = {"slug": ("value",)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "unit", "is_active", "is_filterable", "sort_order")
    list_filter = ("type", "is_active", "is_filterable")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    inlines = (AttributeValueInline,)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "slug", "sort_order")
    list_filter = ("attribute",)
    search_fields = ("value", "slug", "attribute__name")
    prepopulated_fields = {"slug": ("value",)}
    autocomplete_fields = ("attribute",)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute")
    list_filter = ("attribute",)
    search_fields = ("product__name", "attribute__name")
    autocomplete_fields = ("product", "attribute", "choice_value")


class ProductOptionValueInline(admin.TabularInline):
    model = ProductOptionValue
    extra = 1
    prepopulated_fields = {"slug": ("value",)}


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "slug", "sort_order")
    search_fields = ("product__name", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("product",)
    inlines = (ProductOptionValueInline,)


class VariantOptionValueInline(admin.TabularInline):
    model = VariantOptionValue
    extra = 1
    autocomplete_fields = ("option", "value")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "price", "stock_quantity", "low_stock_threshold", "is_active")
    list_filter = ("is_active", "product__category")
    search_fields = ("sku", "barcode", "product__name")
    autocomplete_fields = ("product",)
    ordering = ("product", "sku")
    inlines = (VariantOptionValueInline,)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "variant", "alt_text", "is_primary", "sort_order", "created_at")
    list_filter = ("is_primary", "product__category")
    search_fields = ("product__name", "alt_text")
    autocomplete_fields = ("product", "variant")


admin.site.register(CategoryAttribute)
admin.site.register(ProductOptionValue)
admin.site.register(VariantOptionValue)
