from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
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

            # Handle points redemption
            points_discount = Decimal("0")
            points_used = 0

            if (
                form.cleaned_data.get("use_points")
                and form.cleaned_data.get("points_to_use", 0) > 0
            ):
                points_to_use = form.cleaned_data["points_to_use"]
                if points_to_use <= customer.points:
                    # Calculate discount (100 points = $5 discount)
                    points_discount = Decimal(points_to_use) / Decimal(
                        "20"
                    )  # 100 points = $5, so 1 point = $0.05
                    points_used = points_to_use
                else:
                    messages.error(request, "You don't have enough points for this redemption.")
                    return render(request, "orders/checkout.html", {"form": form, "cart": cart})

            # Create order
            order = Order.objects.create(
                customer=customer,
                shipping_address=form.cleaned_data["shipping_address"],
                payment_method=form.cleaned_data["payment_method"],
            )

            # Create order items from cart and calculate total
            total_order_value = Decimal("0")
            for cart_item in cart.items.all():
                item_total = cart_item.book.price * cart_item.quantity
                total_order_value += item_total

                OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price,
                    total_price=item_total,
                )

                # delete the cart item
                cart_item.delete()

            # Apply points discount if used
            if points_used > 0:
                customer.spend_points(
                    points_used, f"Points redemption for Order #{order.id}", order=order
                )
                messages.success(
                    request, f"You saved ${points_discount:.2f} using {points_used} points!"
                )

            # Award points based on order value (1 point per $1 spent)
            points_earned = int(total_order_value)
            if points_earned > 0:
                customer.add_points(
                    points_earned, f"Purchase reward for Order #{order.id}", order=order
                )
                messages.success(
                    request, f"Congratulations! You earned {points_earned} loyalty points!"
                )

            # Mark order as completed
            order.status = "completed"
            order.save()

            return redirect("order_confirmation", order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


@login_required
def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "orders/order_confirmation.html", {"order": order})
