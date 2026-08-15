from django.db.models import Min, Value, Max
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView , ListView
from django.db.models import Min, Max, Sum, Value, IntegerField, FloatField, Prefetch, Q, F, Subquery, OuterRef, Count

from shop import models
from shop.models import Product, Category


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
        """Get product by id and slug from URL"""
        product_id = self.kwargs.get('id')
        slug = self.kwargs.get('slug')

        base_qs = Product.objects.select_related('category').prefetch_related(
            'images',
            'variants',
            'options'
        )

        if product_id:
            return get_object_or_404(
                base_qs,
                id=product_id,
                is_active=True
            )
        return get_object_or_404(
            base_qs,
            slug=slug,
            is_active=True
        )

    # @staticmethod
    # def _variant_natural_key(variant):
    #     code = variant.variant_code or ''
    #     persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    #     english_digits = '0123456789'
    #     code_en = code.translate(str.maketrans(persian_digits, english_digits))
    #
    #     match = re.search(r'\d+', code_en)
    #     if match:
    #         return (0, int(match.group()))
    #     return (1, code)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from shop.models import Category, Product


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

from django.views.generic import ListView

from shop.models import Category


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



