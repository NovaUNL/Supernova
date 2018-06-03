from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django.forms import ModelForm, TextInput, CharField, formset_factory, Form, NumberInput

from exercises.models import Exercise, MultipleChoiceExercise


class ExerciseForm(ModelForm):
    source_url = CharField(required=False,
                           widget=TextInput(attrs={'placeholder': 'https://site.com/exercicios'}),
                           label='Endreço (opcional):')

    class Meta:
        model = Exercise
        fields = ('synopses_sections', 'enunciation', 'explanation', 'source', 'source_url', 'answer')
        widgets = {
            'synopses_sections': autocomplete.ModelSelect2Multiple(url='synopses:section_ac'),
            'source': TextInput(attrs={'placeholder': '1.4, exercícios de xyz'}),
            'enunciation': CKEditorUploadingWidget(),
            'explanation': CKEditorUploadingWidget(),
            'answer': CKEditorUploadingWidget(),
        }


class MultipleChoiceExerciseForm(ModelForm):
    source_url = CharField(required=False,
                           widget=TextInput(attrs={'placeholder': 'https://site.com/exercicios'}),
                           label='Endreço (opcional):')

    class Meta:
        model = MultipleChoiceExercise
        fields = (
            'synopses_sections', 'enunciation', 'explanation', 'source', 'source_url', 'correct_answer')
        widgets = {
            'synopses_sections': autocomplete.ModelSelect2Multiple(url='synopses:section_ac'),
            'source': TextInput(attrs={'placeholder': '1.4, exercícios de xyz'}),
            'enunciation': CKEditorUploadingWidget(),
            'explanation': CKEditorUploadingWidget(),
            'correct_answer': NumberInput(attrs={'min': '1', 'max': '5'})
        }


class AnswerForm(Form):
    answer = CharField(widget=CKEditorWidget(), label="Resposta:")


AnswerFormSet = formset_factory(AnswerForm, extra=5)
