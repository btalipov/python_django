from django.urls import path

from .views import (
    OrderCreateView,
    OrderDeleteView,
    OrderDetailsView,
    OrdersListView,
    OrderUpdateView,
    ProductArchiveView,
    ProductCreateView,
    ProductDetailsView,
    ProductsListView,
    ProductUpdateView,
    ShopIndexView,
)

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="create_product"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="update_product"),
    path("products/<int:pk>/archive/", ProductArchiveView.as_view(), name="archive_product"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create/", OrderCreateView.as_view(), name="create_order"),
    path("orders/<int:pk>/", OrderDetailsView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="update_order"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="delete_order"),
]
