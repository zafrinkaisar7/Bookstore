from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from books.models import Book
from customers.models import Cart, CartItem, Customer, PointsTransaction


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

    # Check if book is in stock
    if book.stock <= 2:
        messages.error(request, f"Sorry, {book.title} is currently out of stock.")
        return redirect("book_detail", book_id=pk)

    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    # Check if adding this item would exceed available stock
    if not created:
        if cart_item.quantity + 1 > book.stock:
            messages.error(
                request, f"Sorry, only {book.stock} copies of {book.title} are available."
            )
            return redirect("book_detail", book_id=pk)
        cart_item.quantity += 1
    else:
        # For new cart items, check if at least 1 copy is available
        if book.stock < 1:
            messages.error(request, f"Sorry, {book.title} is currently out of stock.")
            return redirect("book_detail", book_id=pk)
        cart_item.quantity = 1

    cart_item.save()

    messages.success(request, f"{book.title} added to cart!")
    return redirect("book_detail", book_id=pk)


@login_required
def update_quantity(request, pk):
    cart_item = CartItem.objects.get(pk=pk)
    action = request.POST.get("action")

    if action == "delete":
        cart_item.delete()
    else:
        if action == "increase":
            # Check if increasing quantity would exceed available stock
            if cart_item.quantity + 1 > cart_item.book.stock:
                messages.error(
                    request,
                    f"Sorry, only {cart_item.book.stock} copies of {cart_item.book.title} are available.",
                )
                return redirect("cart")
            cart_item.quantity += 1
        else:  # decrease
            cart_item.quantity -= 1
            # Remove item if quantity becomes 0 or negative
            if cart_item.quantity <= 0:
                cart_item.delete()
                messages.success(request, f"{cart_item.book.title} removed from cart.")
                return redirect("cart")

        cart_item.save()

    return redirect("cart")


@login_required
def points_dashboard(request):
    """Display user's points dashboard with transaction history and rewards"""
    customer, created = Customer.objects.get_or_create(user=request.user)

    # Get recent transactions
    recent_transactions = PointsTransaction.objects.filter(customer=customer)[:10]

    # Calculate points statistics
    total_earned = (
        PointsTransaction.objects.filter(
            customer=customer, transaction_type__in=["earned", "bonus"]
        ).aggregate(total=Sum("points"))["total"]
        or 0
    )

    total_spent = abs(
        PointsTransaction.objects.filter(customer=customer, transaction_type="spent").aggregate(
            total=Sum("points")
        )["total"]
        or 0
    )

    # Calculate available discount amounts
    points_to_discount = {
        100: 5.00,  # 100 points = ৳5 discount
        200: 12.00,  # 200 points = ৳12 discount
        500: 35.00,  # 500 points = ৳35 discount
        1000: 80.00,  # 1000 points = ৳80 discount
    }

    available_discounts = []
    for points_needed, discount_amount in points_to_discount.items():
        if customer.points >= points_needed:
            available_discounts.append(
                {
                    "points_needed": points_needed,
                    "discount_amount": discount_amount,
                    "can_afford": True,
                }
            )
        else:
            available_discounts.append(
                {
                    "points_needed": points_needed,
                    "discount_amount": discount_amount,
                    "can_afford": False,
                    "points_short": points_needed - customer.points,
                }
            )

    context = {
        "customer": customer,
        "recent_transactions": recent_transactions,
        "total_earned": total_earned,
        "total_spent": total_spent,
        "available_discounts": available_discounts,
    }

    return render(request, "customers/points_dashboard.html", context)
