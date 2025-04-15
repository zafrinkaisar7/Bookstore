from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/<int:book_id>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/update/", views.update_book, name="update_book"),
    path("books/<int:pk>/review/", views.submit_review, name="submit_review"),
    path("books/manage/", views.manage_books, name="manage_books"),
]
