from dal import autocomplete
from django.forms import ChoiceField, ModelForm, TextInput
from django import forms

from synopses.models import Area, Subarea, Topic, Section


class AreaForm(ModelForm):
    class Meta:
        model = Area
        fields = '__all__'
        widgets = {
            'area': autocomplete.ModelSelect2(url='synopses:area_ac'),
            'img_url': forms.URLInput()  # TODO URL Field?
        }


class SubareaForm(ModelForm):
    class Meta:
        model = Subarea
        fields = ('area', 'name', 'description', 'img_url')
        widgets = {
            'name': TextInput(),
            'area': autocomplete.ModelSelect2(url='synopses:area_ac'),
            'img_url': forms.URLInput()  # TODO URL Field?
        }


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ('subarea', 'name', 'sections')
        widgets = {
            'name': TextInput(),
            'subarea': autocomplete.ModelSelect2(url='synopses:subarea_ac'),
            'sections': autocomplete.Select2Multiple(url='synopses:section_ac')
        }


class SectionForm(ModelForm):
    after = ChoiceField(label='Após:', required=True)

    class Meta:
        model = Section
        fields = ('name', 'content')
        widgets = {
            'name': TextInput()
        }
