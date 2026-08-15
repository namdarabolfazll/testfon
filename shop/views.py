from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView

from shop.models import (
    Category,
    Product,
    ProductOption,
    ProductVariant,
    VariantOptionValue,
)


# Create your views here.
class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    pass

class ProductListView(ListView):
    """
    Product list page with advanced filters
    """
    model = Product
    template_name = 'pages/shop.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        base_queryset = Product.objects.filter(is_active=True)

        if slug := self.kwargs.get('slug'):
            base_queryset = base_queryset.filter(category__slug=slug)

        category_slug = self.request.GET.get('category')
        if category_slug:
            base_queryset = base_queryset.filter(category__slug=category_slug)

        queryset = base_queryset.select_related('category').prefetch_related(
            'images', 'variants').distinct()
        # .annotate(
        #     # min_base_price=Min('variants__base_price'),
        #     # cheapest_price=Product.cheapest_price_coal(),
        #     max_discount=Coalesce(
        #         Max('variants__discount_percent'),
        #         Value(0),
        #         output_field=FloatField()
        #     ),
        #     total_stock=Coalesce(
        #         Sum('variants__stock'),
        #         Value(0),
        #         output_field=IntegerField()
        #     ),
        #     total_sold=Coalesce(
        #         Sum('variants__sold_count'),
        #         Value(0),
        #         output_field=IntegerField()
        #     )
        # )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_chip'] = self.kwargs.get('slug')
        context['products_count'] = Product.objects.filter(is_active=True).count()
        return context



class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/product-detail.html'

    def get_object(self, queryset=None):
        """Get product by slug from URL with detail-page relations prefetched."""
        product_id = self.kwargs.get('id')
        slug = self.kwargs.get('slug')

        option_value_prefetch = Prefetch(
            'option_values',
            queryset=VariantOptionValue.objects.select_related('option', 'value').order_by(
                'option__sort_order',
                'option__name',
                'value__sort_order',
                'value__value',
            ),
        )
        variants_prefetch = Prefetch(
            'variants',
            queryset=ProductVariant.objects.prefetch_related(option_value_prefetch).order_by('sku'),
        )
        options_prefetch = Prefetch(
            'options',
            queryset=ProductOption.objects.prefetch_related('values').order_by('sort_order', 'name'),
        )
        base_qs = Product.objects.select_related('category').prefetch_related(
            'images',
            variants_prefetch,
            options_prefetch,
        )

        if product_id:
            return get_object_or_404(base_qs, id=product_id, is_active=True)
        return get_object_or_404(base_qs, slug=slug, is_active=True)

    @staticmethod
    def _money(value):
        if value is None:
            return None
        return format(value, 'f').rstrip('0').rstrip('.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        variants = list(product.variants.all())
        active_variants = [variant for variant in variants if variant.is_active]
        selected_variant = next((variant for variant in active_variants if variant.stock_quantity > 0), None)
        selected_variant = selected_variant or (active_variants[0] if active_variants else None)
        selectable_value_ids = {
            option_value.value_id
            for variant in active_variants
            for option_value in variant.option_values.all()
        }

        variant_options = []
        for option in product.options.all():
            values = [value for value in option.values.all() if value.id in selectable_value_ids]
            if values:
                variant_options.append({'option': option, 'values': values})

        variant_payload = []
        for variant in variants:
            values_by_option = {
                str(option_value.option_id): option_value.value_id
                for option_value in variant.option_values.all()
            }
            variant_payload.append({
                'id': variant.id,
                'sku': variant.sku,
                'price': self._money(variant.price),
                'compare_at_price': self._money(variant.compare_at_price),
                'stock_quantity': variant.stock_quantity,
                'is_active': variant.is_active,
                'is_available': variant.is_active and variant.stock_quantity > 0,
                'option_values': values_by_option,
            })

        context.update({
            'selected_variant': selected_variant,
            'variant_options': variant_options,
            'variant_payload': variant_payload,
            'show_variant_selector': len(active_variants) > 1 and bool(variant_options),
            'related_products': Product.objects.filter(
                category=product.category,
                is_active=True,
            ).exclude(pk=product.pk).select_related('category').prefetch_related('images', 'variants')[:4],
        })
        return context


# class CategoryDetailView(ListView):
#     template_name = "pages/category.html"
#     context_object_name = "products"
#     paginate_by = 12
#
#     def get_queryset(self):
#         self.category = get_object_or_404(
#             Category,
#             slug=self.kwargs["slug"],
#         )
#
#         return (
#             Product.objects
#             .filter(
#                 category=self.category,
#                 is_active=True,
#             )
#             .select_related("category")
#             .prefetch_related(
#                 "images",
#                 "variants",
#             )
#             .distinct()
#         )
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         context["category"] = self.category
#         context["products_count"] = self.get_queryset().count()
#
#         return context


class CategoryListView(ListView):
    model = Category
    template_name = "pages/category.html"
    context_object_name = "categories"

    def get_queryset(self):
        return (
            Category.objects
            .filter(is_active=True)
            .select_related("parent")
            .order_by("sort_order", "name")
        )

class CheckoutListView(TemplateView):
    template_name = 'pages/checkout.html'



