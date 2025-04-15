from django import forms
from .models import Book, Review


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "description", "price", "stock", "category", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "star-rating"}),
        label="Rating",
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Write your review here..."}),
        label="Review",
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
