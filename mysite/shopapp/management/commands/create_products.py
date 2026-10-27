from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write("Create products")

        products = [
            ("Laptop", "Powerful laptop for work and games", 1999, 10),
            ("Desktop", "Desktop computer for the office", 2999, 0),
            ("Smartphone", "Modern smartphone with a great camera", 999, 5),
        ]
        for name, description, price, discount in products:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "discount": discount,
                },
            )
            self.stdout.write(f"Created product {product.name}" if created else f"Product {product.name} already exists")

        self.stdout.write(self.style.SUCCESS("Products created"))
