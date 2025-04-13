from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Cart, CartItem


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


def update_cart_totals_helper(cart):
    cart_items = cart.items.all()
    cart.total_items = sum(item.quantity for item in cart_items)
    cart.total_price = sum(item.book.price * item.quantity for item in cart_items)
    cart.save()


@receiver(post_save, sender=CartItem)
def update_cart_totals(sender, instance, created, **kwargs):
    update_cart_totals_helper(instance.cart)


@receiver(post_delete, sender=CartItem)
def update_cart_totals_on_delete(sender, instance, **kwargs):
    update_cart_totals_helper(instance.cart)
