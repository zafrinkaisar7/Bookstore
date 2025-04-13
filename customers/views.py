from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
    book = Book.objects.get(pk=pk)
    cart = Cart.objects.get(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "book_list"))


@login_required
def update_quantity(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    action = request.POST.get("action")

    if action == "delete":
        cart_item.delete()
    else:
        cart_item.quantity += 1 if action == "increase" else -1
        cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "cart"))
