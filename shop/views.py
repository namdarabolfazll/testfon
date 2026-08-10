
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView , ListView


# Create your views here.
class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    pass

class ProductsListView(TemplateView):
    template_name = 'pages/shop.html'


class ProductsDetailView(TemplateView):
    template_name = 'pages/product-detail.html'

class CategoryListView(TemplateView):
    template_name = 'pages/category.html'

class CheckoutListView(TemplateView):
    template_name = 'pages/checkout.html'



