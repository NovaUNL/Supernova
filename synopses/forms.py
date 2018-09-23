from dal import autocomplete
from django.core.exceptions import ValidationError
from django.forms import ChoiceField, ModelForm, TextInput, inlineformset_factory, URLInput, URLField, CharField, \
    ModelChoiceField
from django import forms

from documents.models import Document
from synopses.models import Area, Subarea, Topic, Section, ClassSection, SectionSource, SectionResource


class AreaForm(ModelForm):
    class Meta:
        model = Area
        fields = '__all__'
        widgets = {
            'area': autocomplete.ModelSelect2(url='synopses:area_ac')
        }


class SubareaForm(ModelForm):
    class Meta:
        model = Subarea
        fields = '__all__'
        widgets = {
            'name': TextInput(),
            'area': autocomplete.ModelSelect2(url='synopses:area_ac')
        }


class TopicForm(ModelForm):
    # TODO after field (ordering)
    class Meta:
        model = Topic
        fields = ('subarea', 'name')
        widgets = {
            'name': TextInput(),
            'subarea': autocomplete.ModelSelect2(url='synopses:subarea_ac')
        }


class SectionForm(ModelForm):
    after = ChoiceField(label='Após:', required=True)
    requirements = forms.ModelMultipleChoiceField(
        widget=autocomplete.Select2Multiple(url='synopses:section_ac'),
        queryset=Section.objects.all(),
        required=False)

    class Meta:
        model = Section
        fields = ('name', 'content', 'requirements')
        widgets = {
            'name': TextInput()}

    def clean_after(self):
        after = self.cleaned_data['after']
        try:
            after = int(after)
        except ValueError:
            raise ValidationError("Invalid 'after' value.")
        return after


class ClassSectionForm(ModelForm):
    class Meta:
        model = ClassSection
        fields = '__all__'
        widgets = {
            'corresponding_class': autocomplete.ModelSelect2(url='class_ac'),
            'section': autocomplete.ModelSelect2(url='synopses:section_ac'),
        }


class SectionSourceForm(ModelForm):
    url = URLField(widget=URLInput(attrs={'placeholder': 'Endreço (opcional)'}), required=False)

    class Meta:
        model = SectionSource
        fields = ('title', 'url')
        widgets = {
            'title': TextInput(attrs={'placeholder': 'Nome da fonte'})
        }


SectionSourcesFormSet = inlineformset_factory(Section, SectionSource, form=SectionSourceForm, extra=3)


class SectionResourceForm(ModelForm):
    name = CharField(label='Nome')
    resource_type = ChoiceField(choices=((None, ''), (1, 'Página'), (2, 'Documento')), initial=None)
    webpage = URLField(required=False)
    document = ModelChoiceField(queryset=Document.objects.all(), required=False)  # TODO select2

    class Meta:
        model = SectionResource
        fields = ('name', 'webpage', 'document')

    def clean_resource_type(self):
        try:
            return int(self.cleaned_data['resource_type'])
        except ValueError:
            raise ValidationError("Tipo de documento inválido")

    def clean_webpage(self):
        webpage = self.cleaned_data['webpage'].strip()
        return None if webpage == '' else webpage

    def clean(self):
        data = super().clean()
        resource_type = data.get('resource_type')
        if resource_type == 1 and self.cleaned_data['webpage'] is None:
            self.add_error('webpage', 'Link em falta')
        elif resource_type == 2 and self.cleaned_data['document'] is None:
            self.add_error('webpage', 'Documento por escolher.')


SectionResourcesFormSet = inlineformset_factory(Section, SectionResource, form=SectionResourceForm, extra=3)
