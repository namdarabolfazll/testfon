from io import BytesIO
from tempfile import TemporaryDirectory
from unittest import mock
import warnings
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from PIL import Image, ImageOps

from common.images.fields import safe_webp_name
from common.images.processing import process_image
from shop.models import (
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


def image_file(name="sample.jpg", mode="RGB", size=(800, 800), fmt="JPEG", color=None):
    color = color if color is not None else ((255, 0, 0, 128) if mode == "RGBA" else (255, 0, 0))
    image = Image.new(mode, size, color)
    output = BytesIO()
    save_kwargs = {"format": fmt}
    image.save(output, **save_kwargs)
    return SimpleUploadedFile(name, output.getvalue(), content_type=f"image/{fmt.lower()}")


class ProcessedImageTests(TestCase):
    def test_jpeg_png_webp_and_rgba_uploads_become_webp(self):
        for name, mode, fmt in [("a.jpg", "RGB", "JPEG"), ("b.png", "RGB", "PNG"), ("c.webp", "RGB", "WEBP"), ("d.png", "RGBA", "PNG")]:
            result = process_image(image_file(name, mode, fmt=fmt), size=(300, 300))
            opened = Image.open(BytesIO(result.content))
            self.assertEqual(opened.format, "WEBP")
            self.assertLessEqual(opened.width, 300)
            self.assertLessEqual(opened.height, 300)

    def test_exif_orientation_is_applied(self):
        image = Image.new("RGB", (80, 40), "red")
        exif = Image.Exif()
        exif[274] = 6
        output = BytesIO()
        image.save(output, format="JPEG", exif=exif)
        result = process_image(SimpleUploadedFile("phone.jpg", output.getvalue()), quality=80)
        opened = Image.open(BytesIO(result.content))
        self.assertEqual(opened.size, (40, 80))

    def test_invalid_and_corrupted_images_are_rejected(self):
        with self.assertRaises(ValidationError):
            process_image(SimpleUploadedFile("fake.jpg", b"not an image"))

    def test_extension_mismatch_uses_actual_content(self):
        result = process_image(image_file("wrong.txt", fmt="JPEG"), size=(200, 200))
        self.assertEqual(Image.open(BytesIO(result.content)).format, "WEBP")

    def test_decompression_bomb_warning_is_rejected(self):
        upload = image_file("big.jpg", size=(20, 20), fmt="JPEG")
        with mock.patch("PIL.Image.MAX_IMAGE_PIXELS", 1):
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with self.assertRaises(ValidationError):
                    process_image(upload)

    def test_animated_webp_is_rejected(self):
        frames = [Image.new("RGB", (32, 32), "red"), Image.new("RGB", (32, 32), "blue")]
        output = BytesIO()
        frames[0].save(output, format="WEBP", save_all=True, append_images=frames[1:], duration=100, loop=0)
        with self.assertRaises(ValidationError):
            process_image(SimpleUploadedFile("anim.webp", output.getvalue()))

    def test_no_upscaling_and_filename_normalization(self):
        result = process_image(image_file("small.jpg", size=(100, 80)), size=(300, 300))
        self.assertEqual((result.width, result.height), (100, 80))
        self.assertEqual(safe_webp_name("../../My Plate.JPG"), "my-plate.webp")


class CatalogModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Mugs", slug="mugs")
        self.product = Product.objects.create(name="Ceramic Mug", slug="ceramic-mug", category=self.category, status=Product.Status.ACTIVE)

    def test_category_hierarchy(self):
        child = Category(name="Espresso Cups", slug="espresso", parent=self.category)
        child.full_clean()
        child.save()
        self.category.parent = child
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    def test_product_variant_and_price_api(self):
        ProductVariant.objects.create(product=self.product, sku="MUG-W-350", price="120.00", stock_quantity=20, is_active=True)
        self.assertEqual(self.product.price, Decimal("120.00"))
        self.assertTrue(self.product.in_stock)

    def test_duplicate_sku_is_rejected(self):
        ProductVariant.objects.create(product=self.product, sku="SKU1", price="10.00")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductVariant.objects.create(product=self.product, sku="SKU1", price="11.00")

    def test_attribute_and_product_attribute_value(self):
        material = Attribute.objects.create(name="Material", slug="material", type=Attribute.Type.CHOICE)
        ceramic = AttributeValue.objects.create(attribute=material, value="Ceramic", slug="ceramic")
        CategoryAttribute.objects.create(category=self.category, attribute=material)
        pav = ProductAttributeValue(product=self.product, attribute=material, choice_value=ceramic)
        pav.full_clean()
        pav.save()
        self.assertEqual(ProductAttributeValue.objects.count(), 1)

    def test_attribute_must_be_allowed_for_category(self):
        width = Attribute.objects.create(name="Width", slug="width", type=Attribute.Type.INTEGER)
        pav = ProductAttributeValue(product=self.product, attribute=width, value_integer=10)
        with self.assertRaises(ValidationError):
            pav.full_clean()

    def test_product_options_and_duplicate_variant_combination_validation(self):
        color = ProductOption.objects.create(product=self.product, name="Color", slug="color")
        white = ProductOptionValue.objects.create(option=color, value="White", slug="white")
        v1 = ProductVariant.objects.create(product=self.product, sku="MUG-W", price="10.00")
        v2 = ProductVariant.objects.create(product=self.product, sku="MUG-W2", price="10.00")
        VariantOptionValue.objects.create(variant=v1, option=color, value=white)
        duplicate = VariantOptionValue(variant=v2, option=color, value=white)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    @override_settings(MEDIA_ROOT=TemporaryDirectory().name)
    def test_product_image_gallery_api(self):
        ProductImage.objects.create(product=self.product, image=image_file("Main Image.JPG"), is_primary=True)
        self.assertTrue(str(self.product.image).endswith("main-image.webp"))
        self.assertEqual(self.product.gallery.count(), 1)

class ProductDetailVariantTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cookware", slug="cookware")
        self.product = Product.objects.create(
            name="ست قابلمه ۱۰ پارچه",
            slug="cookware-set",
            category=self.category,
            status=Product.Status.ACTIVE,
            is_active=True,
        )
        self.color = ProductOption.objects.create(product=self.product, name="رنگ", slug="color", sort_order=1)
        self.material = ProductOption.objects.create(product=self.product, name="جنس", slug="material", sort_order=2)
        self.black = ProductOptionValue.objects.create(option=self.color, value="مشکی", slug="black", sort_order=1)
        self.white = ProductOptionValue.objects.create(option=self.color, value="سفید", slug="white", sort_order=2)
        self.granite = ProductOptionValue.objects.create(option=self.material, value="گرانیتی", slug="granite", sort_order=1)
        self.steel = ProductOptionValue.objects.create(option=self.material, value="استیل", slug="steel", sort_order=2)

    def _variant(self, sku, price="100.00", stock=1, active=True, compare_at_price=None, values=None):
        variant = ProductVariant.objects.create(
            product=self.product,
            sku=sku,
            price=price,
            compare_at_price=compare_at_price,
            stock_quantity=stock,
            is_active=active,
        )
        for option, value in (values or []):
            VariantOptionValue.objects.create(variant=variant, option=option, value=value)
        return variant

    def test_product_without_variant_keeps_selector_hidden(self):
        response = self.client.get(f"/products/{self.product.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["show_variant_selector"])
        self.assertNotContains(response, 'data-variant-selector')

    def test_single_variant_keeps_selector_hidden_but_cart_gets_variant(self):
        variant = self._variant("COOK-001", values=[(self.color, self.black), (self.material, self.granite)])
        response = self.client.get(f"/products/{self.product.slug}/")
        self.assertFalse(response.context["show_variant_selector"])
        self.assertContains(response, f'data-selected-variant-id="{variant.id}"')

    def test_multiple_variants_render_database_options_and_payload(self):
        self._variant("COOK-001", price="6800000.00", stock=6, compare_at_price="7500000.00", values=[(self.color, self.black), (self.material, self.granite)])
        inactive = self._variant("COOK-002", active=False, values=[(self.color, self.white), (self.material, self.steel)])
        response = self.client.get(f"/products/{self.product.slug}/")
        self.assertTrue(response.context["show_variant_selector"])
        self.assertContains(response, "مشکی")
        self.assertNotContains(response, "سفید")
        payload = response.context["variant_payload"]
        self.assertEqual(len(payload), 2)
        self.assertFalse(next(item for item in payload if item["id"] == inactive.id)["is_available"])

    def test_out_of_stock_variant_disables_initial_add_to_cart_when_no_available_stock(self):
        self._variant("COOK-001", stock=0, values=[(self.color, self.black), (self.material, self.granite)])
        response = self.client.get(f"/products/{self.product.slug}/")
        self.assertContains(response, "disabled aria-disabled")
