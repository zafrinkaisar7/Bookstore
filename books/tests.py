from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Book, Category, Review
from decimal import Decimal


class BookTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.admin_user = User.objects.create_superuser(username="admin", password="admin123")

        # Create test category
        self.category = Category.objects.create(name="Fiction")

        # Create test book
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            description="Test Description",
            price=Decimal("19.99"),
            stock=10,
            category=self.category,
        )

        # Setup client
        self.client = Client()

    def test_book_list_view(self):
        """Test that book list view returns 200 and contains book"""
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_book_detail_view(self):
        """Test that book detail view returns 200 and contains book details"""
        response = self.client.get(reverse("book_detail", args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")
        self.assertContains(response, "Test Author")

    def test_add_book_unauthorized(self):
        """Test that unauthorized users cannot add books"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 302)  # Redirects to home

    def test_add_book_authorized(self):
        """Test that admin users can add books"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("add_book"))
        self.assertEqual(response.status_code, 200)

    def test_book_stock_status(self):
        """Test book stock status methods"""
        # Test in stock
        self.assertEqual(self.book.get_stock_status(), "In Stock (10 available)")
        self.assertFalse(self.book.is_out_of_stock)

        # Test low stock
        self.book.stock = 2
        self.book.save()
        self.assertEqual(self.book.get_stock_status(), "Out of Stock")
        self.assertTrue(self.book.is_out_of_stock)

    def test_book_review(self):
        """Test adding a book review"""
        self.client.login(username="testuser", password="testpass123")

        # Create a review directly
        review = Review.objects.create(
            book=self.book, user=self.user, rating=5, comment="Great book!"
        )

        # Verify the review was created
        self.assertTrue(Review.objects.filter(book=self.book).exists())
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great book!")

    def test_update_book(self):
        """Test updating a book as admin"""
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            reverse("update_book", args=[self.book.id]),
            {
                "title": "Updated Book",
                "author": "Updated Author",
                "description": "Updated Description",
                "price": "29.99",
                "stock": 15,
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects after update
        updated_book = Book.objects.get(id=self.book.id)
        self.assertEqual(updated_book.title, "Updated Book")
        self.assertEqual(updated_book.price, Decimal("29.99"))

    def test_book_str_representation(self):
        """Test book string representation"""
        self.assertEqual(str(self.book), "Test Book")

    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "Fiction")

    def test_book_without_category(self):
        """Test creating a book without category"""
        book = Book.objects.create(
            title="No Category Book",
            author="Test Author",
            description="Test Description",
            price=Decimal("19.99"),
            stock=10,
        )
        self.assertIsNone(book.category)

    def test_book_negative_price(self):
        """Test creating a book with negative price should fail"""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Invalid Book",
                author="Test Author",
                description="Test Description",
                price=Decimal("-19.99"),
                stock=10,
                category=self.category,
            )

    def test_book_negative_stock(self):
        """Test creating a book with negative stock should fail"""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Invalid Book",
                author="Test Author",
                description="Test Description",
                price=Decimal("19.99"),
                stock=-10,
                category=self.category,
            )
