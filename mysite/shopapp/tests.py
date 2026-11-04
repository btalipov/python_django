from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Order, Product


@override_settings(THROTTLING_INTERVAL=0)
class ProductViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(name="Phone", price=999)
        cls.archived = Product.objects.create(name="Old phone", price=99, archived=True)

    def test_list_links_to_details_and_hides_archived(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertEqual(list(response.context["products"]), [self.product])
        self.assertContains(response, reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.assertNotContains(response, self.archived.name)

    def test_details_has_links(self):
        kwargs = {"pk": self.product.pk}
        response = self.client.get(reverse("shopapp:product_details", kwargs=kwargs))
        self.assertContains(response, self.product.name)
        self.assertContains(response, reverse("shopapp:products_list"))
        self.assertContains(response, reverse("shopapp:update_product", kwargs=kwargs))
        self.assertContains(response, reverse("shopapp:archive_product", kwargs=kwargs))

    def test_create(self):
        url = reverse("shopapp:create_product")
        self.assertContains(self.client.get(url), 'name="name"')
        data = {"name": "Laptop", "price": "1999.99", "description": "Good one", "discount": 10}
        response = self.client.post(url, data)
        product = Product.objects.get(name="Laptop")
        self.assertRedirects(response, reverse("shopapp:product_details", kwargs={"pk": product.pk}))
        self.assertEqual(str(product.price), "1999.99")

    def test_update_form_is_prefilled_and_saves(self):
        url = reverse("shopapp:update_product", kwargs={"pk": self.product.pk})
        self.assertContains(self.client.get(url), 'value="Phone"')
        response = self.client.post(url, {"name": "New phone", "price": "500", "description": "", "discount": 5})
        self.assertRedirects(response, reverse("shopapp:product_details", kwargs={"pk": self.product.pk}))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "New phone")
        self.assertEqual(self.product.discount, 5)

    def test_archive_asks_on_get_and_archives_on_post(self):
        url = reverse("shopapp:archive_product", kwargs={"pk": self.product.pk})
        self.assertContains(self.client.get(url), "Are you sure")
        self.product.refresh_from_db()
        self.assertFalse(self.product.archived)

        response = self.client.post(url)
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.product.refresh_from_db()
        self.assertTrue(self.product.archived)

    def test_archived_product_details_has_no_archive_link(self):
        kwargs = {"pk": self.archived.pk}
        response = self.client.get(reverse("shopapp:product_details", kwargs=kwargs))
        self.assertContains(response, "Archived")
        self.assertNotContains(response, reverse("shopapp:archive_product", kwargs=kwargs))
        self.assertEqual(self.client.post(reverse("shopapp:archive_product", kwargs=kwargs)).status_code, 404)


@override_settings(THROTTLING_INTERVAL=0)
class OrderViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="bob", password="qwerty")
        cls.other_user = User.objects.create_user(username="alice", password="qwerty")
        cls.product = Product.objects.create(name="Phone", price=999)
        cls.second_product = Product.objects.create(name="Laptop", price=1999)
        cls.archived = Product.objects.create(name="Old phone", price=99, archived=True)
        cls.order = Order.objects.create(user=cls.user, delivery_address="ul. Pupkina, d. 8")
        cls.order.products.add(cls.product)

    def test_list_shows_link_user_and_products(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, reverse("shopapp:order_details", kwargs={"pk": self.order.pk}))
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.product.name)

    def test_list_query_count_does_not_depend_on_orders(self):
        for _ in range(3):
            order = Order.objects.create(user=self.other_user)
            order.products.add(self.second_product)
        # One query for orders with users and one for their products.
        with self.assertNumQueries(2):
            self.client.get(reverse("shopapp:orders_list"))

    def test_details_shows_properties_and_links(self):
        kwargs = {"pk": self.order.pk}
        response = self.client.get(reverse("shopapp:order_details", kwargs=kwargs))
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.product.name)
        self.assertContains(response, reverse("shopapp:orders_list"))
        self.assertContains(response, reverse("shopapp:update_order", kwargs=kwargs))
        self.assertContains(response, reverse("shopapp:delete_order", kwargs=kwargs))

    def test_create_form_hides_archived_products(self):
        response = self.client.get(reverse("shopapp:create_order"))
        self.assertContains(response, self.product.name)
        self.assertNotContains(response, self.archived.name)

    def test_create(self):
        data = {
            "user": self.other_user.pk,
            "delivery_address": "ul. Lenina, d. 1",
            "promocode": "SALE",
            "products": [self.product.pk, self.second_product.pk],
        }
        response = self.client.post(reverse("shopapp:create_order"), data)
        order = Order.objects.get(user=self.other_user)
        self.assertRedirects(response, reverse("shopapp:order_details", kwargs={"pk": order.pk}))
        self.assertCountEqual(order.products.all(), [self.product, self.second_product])

    def test_create_rejects_archived_product(self):
        data = {"user": self.user.pk, "products": [self.archived.pk]}
        response = self.client.post(reverse("shopapp:create_order"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].has_error("products"))
        self.assertEqual(Order.objects.count(), 1)

    def test_update_form_is_prefilled_and_saves(self):
        url = reverse("shopapp:update_order", kwargs={"pk": self.order.pk})
        form = self.client.get(url).context["form"]
        self.assertEqual(form["user"].value(), self.user.pk)
        self.assertEqual(form["products"].value(), [self.product.pk])

        data = {
            "user": self.other_user.pk,
            "delivery_address": "ul. Lenina, d. 1",
            "promocode": "",
            "products": [self.second_product.pk],
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("shopapp:order_details", kwargs={"pk": self.order.pk}))
        self.order.refresh_from_db()
        self.assertEqual(self.order.user, self.other_user)
        self.assertEqual(list(self.order.products.all()), [self.second_product])

    def test_update_keeps_product_archived_after_ordering(self):
        self.order.products.add(self.archived)
        url = reverse("shopapp:update_order", kwargs={"pk": self.order.pk})
        self.assertContains(self.client.get(url), self.archived.name)

        data = {"user": self.user.pk, "products": [self.product.pk, self.archived.pk]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertCountEqual(self.order.products.all(), [self.product, self.archived])

    def test_delete_asks_on_get_and_deletes_on_post(self):
        url = reverse("shopapp:delete_order", kwargs={"pk": self.order.pk})
        self.assertContains(self.client.get(url), "Are you sure")
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

        response = self.client.post(url)
        self.assertRedirects(response, reverse("shopapp:orders_list"))
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
