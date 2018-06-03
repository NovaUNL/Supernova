from django.contrib import admin

from exercises.models import Exercise, MultipleChoiceExercise

admin.site.register(Exercise)
admin.site.register(MultipleChoiceExercise)  # TODO proper widget for the ArrayField
