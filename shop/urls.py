from django.urls import path

from shop.views import HomePageView, ProductsListView, ProductsDetailView, CheckoutListView, CategoryListView

app_name = 'shop'
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', HomePageView.as_view(), name='about'),
    path('products/', ProductsListView.as_view(), name='products'),
    path('products/detail/', ProductsDetailView.as_view(), name='product-detail'),
    path('checkout/', CheckoutListView.as_view(), name='checkout'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('cart/' , CheckoutListView.as_view(), name='cart'),
]