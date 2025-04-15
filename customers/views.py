from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from books.models import Book
from customers.models import Cart, CartItem


# Create your views here.
@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    return render(request, "customers/cart.html", {"cart": cart})


@login_required
def add_to_cart(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    # Update cart totals
    cart.total_items = cart.items.count()
    cart.total_price = sum(item.book.price * item.quantity for item in cart.items.all())
    cart.save()

    messages.success(request, f"{book.title} added to cart!")
    return redirect("book_detail", book_id=pk)


@login_required
def update_quantity(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    action = request.POST.get("action")

    if action == "delete":
        cart_item.delete()
    else:
        cart_item.quantity += 1 if action == "increase" else -1
        cart_item.save()

    # Update cart totals
    cart = cart_item.cart
    cart.total_items = cart.items.count()
    cart.total_price = sum(item.book.price * item.quantity for item in cart.items.all())
    cart.save()

    return redirect("cart")
