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
            'title': djf.TextInput(),
            'area': autocomplete.ModelSelect2(url='synopses:area_ac')}


class SubareaSectionForm(djf.ModelForm):
    class Meta:
        model = synopsis.Section
        fields = ('title', 'content_ck', 'subarea', 'requirements')
        widgets = {
            'title': djf.TextInput(),
            'subarea': djf.HiddenInput(),
            'requirements': autocomplete.Select2Multiple(url='synopses:section_ac')}


class SectionChildForm(djf.ModelForm):
    class Meta:
        model = synopsis.Section
        fields = ('title', 'content_ck', 'requirements')
        widgets = {
            'title': djf.TextInput(),
            'requirements': autocomplete.Select2Multiple(url='synopses:section_ac')}


class SectionEditForm(djf.ModelForm):
    class Meta:
        model = synopsis.Section
        fields = ('title', 'content_ck', 'content_md', 'subarea', 'parents', 'requirements')
        widgets = {
            'title': djf.TextInput(),
            'subarea': autocomplete.ModelSelect2(url='synopses:subarea_ac'),
            'requirements': autocomplete.Select2Multiple(url='synopses:section_ac'),
            'parents': autocomplete.Select2Multiple(url='synopses:section_ac')}

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
    class Meta:
        model = synopsis.SectionSource
        fields = ('title', 'url')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Nome da fonte*'}),
            'url': djf.URLInput(attrs={'placeholder': 'URL*'}),
        }


class SectionWebpageResourceForm(djf.ModelForm):
    class Meta:
        model = synopsis.SectionWebResource
        fields = ('title', 'url')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Descritivo*'}),
            'url': djf.URLInput(attrs={'placeholder': 'URL'}),
        }


class SectionDocumentResourceForm(djf.ModelForm):
    # document = djf.ModelChoiceField(queryset=documents.Document.objects.all(), required=False)  # TODO select2

    class Meta:
        model = synopsis.SectionDocumentResource
        fields = ('title', 'document')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Descritivo*'})
        }


SectionDocumentResourcesFormSet = djf.inlineformset_factory(
    synopsis.Section,
    synopsis.SectionDocumentResource,
    form=SectionDocumentResourceForm,
    extra=3)

SectionWebpageResourcesFormSet = djf.inlineformset_factory(
    synopsis.Section,
    synopsis.SectionWebResource,
    form=SectionWebpageResourceForm,
    extra=3)

SectionSourcesFormSet = djf.inlineformset_factory(
    synopsis.Section,
    synopsis.SectionSource,
    form=SectionSourceForm,
    extra=3)
