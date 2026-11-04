from timeit import default_timer

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .models import Order, Product


class ShopIndexView(TemplateView):
    template_name = "shopapp/shop-index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["time_running"] = default_timer()
        context["links"] = [
            ("Products", "shopapp:products_list"),
            ("Create product", "shopapp:create_product"),
            ("Orders", "shopapp:orders_list"),
            ("Create order", "shopapp:create_order"),
        ]
        return context


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    model = Product
    context_object_name = "product"


class ProductFormMixin:
    template_name = "shopapp/product-form.html"
    model = Product
    fields = ["name", "price", "description", "discount"]

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductCreateView(ProductFormMixin, CreateView):
    pass


class ProductUpdateView(ProductFormMixin, UpdateView):
    pass


class ProductArchiveView(DeleteView):
    """Soft delete: keeps the row, because existing orders may refer to it."""

    template_name = "shopapp/product-archive.html"
    queryset = Product.objects.filter(archived=False)
    context_object_name = "product"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        self.object.archived = True
        self.object.save(update_fields=["archived"])
        return HttpResponseRedirect(self.get_success_url())


class OrderQuerysetMixin:
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrdersListView(OrderQuerysetMixin, ListView):
    template_name = "shopapp/orders-list.html"
    context_object_name = "orders"


class OrderDetailsView(OrderQuerysetMixin, DetailView):
    template_name = "shopapp/order-details.html"
    context_object_name = "order"


class OrderFormMixin:
    template_name = "shopapp/order-form.html"
    model = Order
    fields = ["user", "delivery_address", "promocode", "products"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Archived products can't be picked for an order, but those already in
        # the order stay listed, otherwise saving the form would drop them.
        available = Q(archived=False)
        if self.object:
            available |= Q(orders=self.object)
        products_field = form.fields["products"]
        products_field.queryset = Product.objects.filter(available).distinct()
        products_field.label_from_instance = lambda product: f"{product.name} (${product.price})"
        return form

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrderCreateView(OrderFormMixin, CreateView):
    pass


class OrderUpdateView(OrderFormMixin, UpdateView):
    pass


class OrderDeleteView(DeleteView):
    template_name = "shopapp/order-delete.html"
    model = Order
    context_object_name = "order"
    success_url = reverse_lazy("shopapp:orders_list")
