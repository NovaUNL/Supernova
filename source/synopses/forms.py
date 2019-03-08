from django.core import exceptions as dje
from django import forms as djf
from dal import autocomplete

from documents import models as documents
from synopses import models as synopsis


class AreaForm(djf.ModelForm):
    class Meta:
        model = synopsis.Area
        fields = '__all__'
        widgets = {
            'area': autocomplete.ModelSelect2(url='synopses:area_ac')
        }


class SubareaForm(djf.ModelForm):
    class Meta:
        model = synopsis.Subarea
        fields = '__all__'
        widgets = {
            'name': djf.TextInput(),
            'area': autocomplete.ModelSelect2(url='synopses:area_ac')
        }


class TopicForm(djf.ModelForm):
    # TODO after field (ordering)
    class Meta:
        model = synopsis.Topic
        fields = ('subarea', 'name')
        widgets = {
            'name': djf.TextInput(),
            'subarea': autocomplete.ModelSelect2(url='synopses:subarea_ac')
        }


class SectionForm(djf.ModelForm):
    after = djf.ChoiceField(label='Após:', required=True)
    requirements = djf.ModelMultipleChoiceField(
        widget=autocomplete.Select2Multiple(url='synopses:section_ac'),
        queryset=synopsis.Section.objects.all(),
        required=False)

    class Meta:
        model = synopsis.Section
        fields = ('name', 'content', 'requirements')
        widgets = {
            'name': djf.TextInput()}

    def clean_after(self):
        after = self.cleaned_data['after']
        try:
            after = int(after)
        except ValueError:
            raise dje.ValidationError("Invalid 'after' value.")
        return after


class ClassSectionForm(djf.ModelForm):
    class Meta:
        model = synopsis.ClassSection
        fields = '__all__'
        widgets = {
            'corresponding_class': autocomplete.ModelSelect2(url='class_ac'),
            'section': autocomplete.ModelSelect2(url='synopses:section_ac'),
        }


class SectionSourceForm(djf.ModelForm):
    url = djf.URLField(widget=djf.URLInput(attrs={'placeholder': 'Endreço (opcional)'}), required=False)

    class Meta:
        model = synopsis.SectionSource
        fields = ('title', 'url')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Nome da fonte'})
        }


SectionSourcesFormSet = djf.inlineformset_factory(synopsis.Section, synopsis.SectionSource,
                                                  form=SectionSourceForm, extra=3)


class SectionResourceForm(djf.ModelForm):
    name = djf.CharField(label='Nome')
    resource_type = djf.ChoiceField(choices=((None, ''), (1, 'Página'), (2, 'Documento')), initial=None)
    webpage = djf.URLField(required=False)
    document = djf.ModelChoiceField(queryset=documents.Document.objects.all(), required=False)  # TODO select2

    class Meta:
        model = synopsis.SectionResource
        fields = ('name', 'webpage', 'document')

    def clean_resource_type(self):
        try:
            return int(self.cleaned_data['resource_type'])
        except ValueError:
            raise dje.ValidationError("Tipo de documento inválido")

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


SectionResourcesFormSet = djf.inlineformset_factory(synopsis.Section, synopsis.SectionResource,
                                                    form=SectionResourceForm, extra=3)
