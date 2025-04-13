from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm
from customers.models import Cart, Customer
from .models import Order, OrderItem


# Create your views here.
@login_required
def checkout(request):
    customer, created = Customer.objects.get_or_create(user=request.user)

    cart = Cart.objects.get(user=request.user)
    if not cart.items.exists():
        return redirect("cart")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if created:
                customer.phone = form.cleaned_data["phone"]
                customer.save()

            # Create order
            order = Order.objects.create(
                customer=customer,
                shipping_address=form.cleaned_data["shipping_address"],
                payment_method=form.cleaned_data["payment_method"],
            )

            # Create order items from cart
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price,
                    total_price=cart_item.book.price * cart_item.quantity,
                )

                # delete the cart item
                cart_item.delete()

            return redirect("order_confirmation", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "orders/order_confirmation.html", {"order": order})
