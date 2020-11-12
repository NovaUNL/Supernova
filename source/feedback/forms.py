from django import forms as djf
from django.core.exceptions import ValidationError

from feedback import models as m
from supernova.widgets import StarInput, SliderInput


class SuggestionForm(djf.ModelForm):
    class Meta:
        model = m.Suggestion
        fields = ('title', 'content')


class ReviewForm(djf.ModelForm):
    class Meta:
        model = m.Review
        fields = ('rating', 'text', 'anonymity')
        widgets = {
            'rating': StarInput(),
            'anonymity': SliderInput(),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            raise ValidationError("Bad rating value.")
        return rating
