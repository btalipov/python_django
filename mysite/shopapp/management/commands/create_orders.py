from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates orders and links them with existing products
    """

    def handle(self, *args, **options):
        self.stdout.write("Create orders")

        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if user is None:
            self.stderr.write("No users found. Run `createsuperuser` first.")
            return

        products = list(Product.objects.all())
        if not products:
            self.stderr.write("No products found. Run `create_products` first.")
            return

        orders = [
            ("ul Pupkina, d 8", "SALE123", products),
            ("ul Lenina, d 1", "", products[:1]),
        ]
        for delivery_address, promocode, order_products in orders:
            order, created = Order.objects.get_or_create(
                delivery_address=delivery_address,
                promocode=promocode,
                user=user,
            )
            order.products.add(*order_products)
            self.stdout.write(f"Created {order}" if created else f"{order} already exists")

        self.stdout.write(self.style.SUCCESS("Orders created"))
