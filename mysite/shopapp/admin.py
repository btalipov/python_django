from django.contrib import admin

from .models import Order, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "price", "discount", "created_at", "archived"
    list_display_links = "pk", "name"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = "pk", "delivery_address", "promocode", "created_at", "user"
    list_display_links = "pk", "delivery_address"
