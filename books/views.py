from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import OrderItem
from .forms import BookForm, ReviewForm
from .models import Book, Review, Category
from django.contrib import messages
from customers.models import Cart, CartItem


# Create your views here.
def check_purchased(request, book_id):
    if not request.user.is_authenticated:
        return False
    return OrderItem.objects.filter(order__customer__user=request.user, book_id=book_id).exists()


def add_book(request):
    # only superusers can add books
    if not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()
    return render(request, "books/book_form.html", {"form": form})


@login_required
def update_book(request, pk):
    # only superusers can update books
    if not request.user.is_superuser:
        return redirect("home")

    book = Book.objects.get(pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("manage_books")
    else:
        form = BookForm(instance=book)
    return render(request, "books/book_form.html", {"form": form, "update": True})


def book_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get("category")
    search_query = request.GET.get("q", "")

    books = Book.objects.all()
    if selected_category:
        books = books.filter(category_id=selected_category)
    if search_query:
        books = books.filter(title__icontains=search_query)

    # Calculate total value of displayed books
    total_value = sum(book.price for book in books)

    context = {
        "books": books,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query,
        "total_value": total_value,
    }
    return render(request, "books/book_list.html", context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # get all reviews for this book
    reviews = Review.objects.filter(book=book)
    # check if the book is purchased by the user
    is_purchased = check_purchased(request, book_id)

    form = ReviewForm()
    return render(
        request,
        "books/book_detail.html",
        {"book": book, "form": form, "reviews": reviews, "is_purchased": is_purchased},
    )


@login_required
def add_book_review(request, pk):
    print(request.POST)
    # Check if user has purchased this book
    purchased = check_purchased(request, pk)

    if not purchased:
        return redirect("book_detail", pk=pk)

    # if purchased, add review
    book = Book.objects.get(pk=pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.book = book
        review.user = request.user
        review.save()
    return redirect("book_detail", pk=pk)


@login_required
def submit_review(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Check if user has purchased this book
    if not check_purchased(request, pk):
        messages.error(request, "You must purchase this book before reviewing it.")
        return redirect("book_detail", book_id=pk)

    # Check if user has already reviewed this book
    if Review.objects.filter(book=book, user=request.user).exists():
        messages.error(request, "You have already reviewed this book.")
        return redirect("book_detail", book_id=pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted!")
            return redirect("book_detail", book_id=pk)
    else:
        form = ReviewForm()

    return render(
        request,
        "books/book_detail.html",
        {
            "book": book,
            "form": form,
            "reviews": Review.objects.filter(book=book),
            "is_purchased": True,
        },
    )


@login_required
def manage_books(request):
    # only superusers can manage books
    if not request.user.is_superuser:
        return redirect("home")

    books = Book.objects.all()
    return render(request, "books/manage_books.html", {"books": books})
