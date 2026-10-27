from django.urls import path

from .views import orders_list, products_list, shop_index

app_name = "shopapp"

urlpatterns = [
    path("", shop_index, name="index"),
    path("products/", products_list, name="products_list"),
    path("orders/", orders_list, name="orders_list"),
]
