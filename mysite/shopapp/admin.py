from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Order, Product


class OrderInline(admin.TabularInline):
    model = Product.orders.through
    extra = 0


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        OrderInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "created_at", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description", "price", "discount"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide",),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        }),
    ]

    @admin.display(description="Description")
    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


class ProductInline(admin.TabularInline):
    model = Order.products.through
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    list_display = "pk", "delivery_address", "promocode", "created_at", "user_verbose"
    list_display_links = "pk", "delivery_address"
    search_fields = "delivery_address", "promocode", "user__username"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return Order.objects.select_related("user").prefetch_related("products")

    @admin.display(description="User")
    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
