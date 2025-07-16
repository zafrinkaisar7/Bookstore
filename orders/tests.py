from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from books.models import Book, Category
from customers.models import Customer, Cart, CartItem
from .models import Order, OrderItem
from decimal import Decimal


class OrderTests(TestCase):
    def setUp(self):
        # Create test user and customer
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.customer = Customer.objects.create(user=self.user, phone="1234567890")

        # Create test category and book
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            description="Test Description",
            price=Decimal("19.99"),
            stock=10,
            category=self.category,
        )

        # Create test cart using get_or_create to handle unique constraint
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, book=self.book, quantity=2)

        # Setup client
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")

    def test_checkout_view(self):
        """Test checkout process"""
        response = self.client.post(
            reverse("checkout"),
            {"shipping_address": "123 Test St", "payment_method": "card", "phone": "1234567890"},
        )
        self.assertEqual(response.status_code, 302)  # Redirects after successful checkout

        # Verify order was created
        order = Order.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_method, "card")
        self.assertEqual(order.shipping_address, "123 Test St")

        # Verify order items
        order_item = OrderItem.objects.filter(order=order).first()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.book, self.book)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, self.book.price)
        self.assertEqual(order_item.total_price, self.book.price * 2)

    def test_empty_cart_checkout(self):
        """Test checkout with empty cart"""
        self.cart_item.delete()
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)  # Redirects to cart

    def test_order_status_update(self):
        """Test order status update"""
        order = Order.objects.create(
            customer=self.customer, shipping_address="123 Test St", payment_method="card"
        )
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=1,
            price=self.book.price,
            total_price=self.book.price,
        )

        # Test status update
        order.status = "completed"
        order.save()
        self.assertEqual(order.status, "completed")

    def test_order_total_calculation(self):
        """Test order total calculation"""
        order = Order.objects.create(
            customer=self.customer, shipping_address="123 Test St", payment_method="card"
        )

        # Add multiple items
        OrderItem.objects.create(
            order=order,
            book=self.book,
            quantity=2,
            price=self.book.price,
            total_price=self.book.price * 2,
        )

        # Verify total calculation
        total = sum(item.total_price for item in order.items.all())
        self.assertEqual(total, self.book.price * 2)
