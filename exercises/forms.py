from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django.forms import ModelForm, TextInput, CharField, formset_factory, Form

from exercises.models import Exercise


class ExerciseForm(ModelForm):
    """
    | Base exercise form. Enough to validate returns, yet meant to be extended client side.
    | Ideally this would have a custom widget to create and return the whole model ``content``.
    """
    source_url = CharField(required=False,
                           widget=TextInput(attrs={'placeholder': 'https://site.com/exercicios'}),
                           label='Endreço (opcional):')

    class Meta:
        model = Exercise
        fields = ('synopses_sections', 'introduction', 'source', 'source_url')
        widgets = {
            'synopses_sections': autocomplete.ModelSelect2Multiple(url='synopses:section_ac'),
            'source': TextInput(attrs={'placeholder': '1.4, exercícios de xyz'}),
            'introduction': CKEditorUploadingWidget()
        }


class AnswerForm(Form):
    """
    Generic rich text answer
    """
    answer = CharField(widget=CKEditorWidget(), label="Resposta:")


#: A formset which will be used to return 1..n answers at once
AnswerFormSet = formset_factory(AnswerForm, extra=1)
