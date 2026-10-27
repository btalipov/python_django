from timeit import default_timer

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Order, Product


def shop_index(request: HttpRequest) -> HttpResponse:
    links = [
        ("Products", "shopapp:products_list"),
        ("Orders", "shopapp:orders_list"),
    ]
    context = {
        "time_running": default_timer(),
        "links": links,
    }
    return render(request, "shopapp/shop-index.html", context=context)


def products_list(request: HttpRequest) -> HttpResponse:
    context = {
        "products": Product.objects.all(),
    }
    return render(request, "shopapp/products-list.html", context=context)


def orders_list(request: HttpRequest) -> HttpResponse:
    context = {
        "orders": Order.objects.select_related("user").prefetch_related("products").all(),
    }
    return render(request, "shopapp/orders-list.html", context=context)
