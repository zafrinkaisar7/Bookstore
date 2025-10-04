from django.db import models
from django.contrib.auth.models import User
from books.models import Book


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=15)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def add_points(self, points, description="", order=None):
        """Add points to customer and create transaction record"""
        self.points += points
        self.save()
        PointsTransaction.objects.create(
            customer=self,
            points=points,
            transaction_type="earned",
            description=description,
            order=order,
        )

    def spend_points(self, points, description="", order=None):
        """Spend points from customer and create transaction record"""
        if self.points >= points:
            self.points -= points
            self.save()
            PointsTransaction.objects.create(
                customer=self,
                points=-points,
                transaction_type="spent",
                description=description,
                order=order,
            )
            return True
        return False


class PointsTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("earned", "Earned"),
        ("spent", "Spent"),
        ("bonus", "Bonus"),
        ("expired", "Expired"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="points_transactions"
    )
    points = models.IntegerField()  # Positive for earned, negative for spent
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="points_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.user.username} - {self.points} points ({self.transaction_type})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items = models.IntegerField(default=0)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
