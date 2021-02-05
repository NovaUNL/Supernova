from django import forms as djf
from dal import autocomplete
from ckeditor.widgets import CKEditorWidget
from django.db import transaction
from django.db.models import Max

from learning import models as m
from learning.widgets import ExerciseWidget


class AreaForm(djf.ModelForm):
    class Meta:
        model = m.Area
        fields = '__all__'
        widgets = {
            'area': autocomplete.ModelSelect2(url='learning:area_ac')
        }


class SubareaForm(djf.ModelForm):
    class Meta:
        model = m.Subarea
        fields = '__all__'
        widgets = {
            'title': djf.TextInput(),
            'area': autocomplete.ModelSelect2(url='learning:area_ac')}


class SectionCreateForm(djf.ModelForm):
    class Meta:
        model = m.Section
        fields = ('title', 'content', 'subarea', 'requirements', 'type')
        widgets = {
            'title': djf.TextInput(),
            'subarea': djf.HiddenInput(),
            'requirements': autocomplete.Select2Multiple(url='learning:section_ac')}


class SectionEditForm(djf.ModelForm):
    class Meta:
        model = m.Section
        fields = ('title', 'content', 'subarea', 'parents', 'classes', 'requirements', 'type')
        widgets = {
            'title': djf.TextInput(),
            'subarea': autocomplete.ModelSelect2(url='learning:subarea_ac'),
            'requirements': autocomplete.Select2Multiple(url='learning:section_ac'),
            'parents': autocomplete.Select2Multiple(url='learning:section_ac'),
            'classes': autocomplete.Select2Multiple(url='college:class_ac'),
        }

    def save(self, commit=True):
        instance = super(SectionEditForm, self).save(commit=False)

        with transaction.atomic():
            parents = self.cleaned_data['parents']
            for parent in parents.exclude(id__in=instance.parents.values_list('id', flat=True)):
                next_index = m.SectionSubsection.objects.filter(parent=parent).aggregate(Max('index'))['index__max']
                next_index = 0 if next_index is None else next_index + 1
                m.SectionSubsection.objects.create(parent=parent, section=instance, index=next_index)

            classes = self.cleaned_data['classes']
            for class_ in classes.exclude(id__in=instance.classes.values_list('id', flat=True)):
                next_index = m.ClassSection.objects.filter(corresponding_class=class_).aggregate(Max('index'))[
                    'index__max']
                next_index = 0 if next_index is None else next_index + 1
                m.ClassSection.objects.create(corresponding_class=class_, section=instance, index=next_index)

            if commit:
                instance.save()
                self.save_m2m()
        return instance


class ClassSectionForm(djf.ModelForm):
    class Meta:
        model = m.ClassSection
        fields = '__all__'
        widgets = {
            'corresponding_class': autocomplete.ModelSelect2(url='class_ac'),
            'section': autocomplete.ModelSelect2(url='learning:section_ac'),
        }


class SectionSourceForm(djf.ModelForm):
    class Meta:
        model = m.SectionSource
        fields = ('title', 'url')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Nome da fonte*'}),
            'url': djf.URLInput(attrs={'placeholder': 'URL*'}),
        }


class SectionWebpageResourceForm(djf.ModelForm):
    class Meta:
        model = m.SectionWebResource
        fields = ('title', 'url')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Descritivo*'}),
            'url': djf.URLInput(attrs={'placeholder': 'URL'}),
        }


class SectionDocumentResourceForm(djf.ModelForm):
    class Meta:
        model = m.SectionDocumentResource
        fields = ('title', 'document')
        widgets = {
            'title': djf.TextInput(attrs={'placeholder': 'Descritivo*'}),
            # 'document': autocomplete.ModelSelect2(url='document_ac'), # TODO select2
        }


SectionDocumentResourcesFormSet = djf.inlineformset_factory(
    m.Section,
    m.SectionDocumentResource,
    form=SectionDocumentResourceForm,
    extra=3)

SectionWebpageResourcesFormSet = djf.inlineformset_factory(
    m.Section,
    m.SectionWebResource,
    form=SectionWebpageResourceForm,
    extra=3)

SectionSourcesFormSet = djf.inlineformset_factory(
    m.Section,
    m.SectionSource,
    form=SectionSourceForm,
    extra=3)


class ExerciseForm(djf.ModelForm):
    """
    | Base exercise form. Enough to validate returns, yet meant to be extended client side.
    | Ideally this would have a custom widget to create and return the whole model ``content``.
    """

    class Meta:
        model = m.Exercise
        fields = ("content", "source", "source_url", "synopses_sections")
        widgets = {
            'content': ExerciseWidget(),
            'synopses_sections': autocomplete.ModelSelect2Multiple(url='learning:section_ac'),
            'source': djf.TextInput(attrs={'placeholder': '1.4, exercícios de xyz'}),
            'source_url': djf.TextInput(attrs={'placeholder': 'https://exemplo.com/exercicios'}),
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        self._validate_exercise(content)
        return content

    # TODO move this to a custom Field and throw proper exceptions
    @staticmethod
    def _validate_exercise(exercise, min_length=10):
        if 'type' not in exercise:
            raise djf.ValidationError(f"Exercício com tipo em falta.")
        etype = exercise['type']
        if etype == "group":
            if 'enunciation' not in exercise or 'subproblems' not in exercise:
                raise djf.ValidationError("Grupo com campos em falta")
            enunciation, subproblems = exercise['enunciation'], exercise['subproblems']
            if type(enunciation) is not str or type(subproblems) is not list:
                raise djf.ValidationError("Grupo com tipos inválidos")
            if len(subproblems) < 2:
                raise djf.ValidationError("Grupo com menos de dois sub-problemas")
            exercise['enunciation'] = enunciation = enunciation.strip()
            map(ExerciseForm._validate_exercise, subproblems)
        elif etype == "write":
            if 'enunciation' not in exercise or 'answer' not in exercise:
                raise djf.ValidationError("Questão com campos em falta")
            enunciation, answer = exercise['enunciation'], exercise['answer']
            if type(enunciation) is not str or type(answer) is not str:
                raise djf.ValidationError("Questão com tipos inválidos")
            enunciation, _ = exercise['enunciation'], exercise['answer'] = enunciation.strip(), answer.strip()
        elif etype == "select":
            if 'enunciation' not in exercise or 'candidates' not in exercise or 'answerIndexes' not in exercise:
                raise djf.ValidationError("Escolha múltipla com parametros em falta")
            enunciation, candidates = exercise['enunciation'], exercise['candidates']
            indexes = exercise['answerIndexes']
            if type(enunciation) is not str \
                    or type(candidates) is not list \
                    or type(indexes) is not list \
                    or not all(map(lambda index: type(index) is int, indexes)):
                raise djf.ValidationError("Escolha múltipla com tipos inválidos")
            indexes = list(set(indexes))
            if (candidate_count := len(candidates)) < 2 \
                    or not all(map(lambda x: type(x) is str, candidates)) \
                    or len(indexes) == 0 \
                    or any(map(lambda i: type(i) < 0, indexes)) \
                    or any(map(lambda i: type(i) >= candidate_count, indexes)):
                raise djf.ValidationError("Escolha múltipla com parametros inválidos")
            exercise['enunciation'] = enunciation = enunciation.strip()
            for i, candidate in enumerate(candidates):
                if len(s := candidate.strip()) > 0:
                    candidates[i] = s
                else:
                    raise djf.ValidationError("Alinea vazia")
        else:
            raise djf.ValidationError(f"Tipo de exercício desconhecido: '{exercise['type']}'")

        if (l := len(enunciation)) < min_length:
            raise djf.ValidationError(f"Enunciado demasiado curto. ({l} caráteres)")

        return True


class AnswerForm(djf.Form):
    """
    Generic rich text answer
    """
    answer = djf.CharField(widget=CKEditorWidget(), label="Resposta:")


#: A formset which will be used to return 1..n answers at once
AnswerFormSet = djf.formset_factory(AnswerForm, extra=1)


class QuestionForm(djf.ModelForm):
    class Meta:
        model = m.Question
        fields = ('title', 'content', 'linked_sections', 'linked_classes', 'linked_exercises')
        widgets = {
            'linked_classes': autocomplete.ModelSelect2Multiple(url='college:class_ac'),
            'linked_sections': autocomplete.ModelSelect2Multiple(url='learning:section_ac'),
            'linked_exercises': autocomplete.ModelSelect2Multiple(url='learning:exercise_ac'),
        }


class AnswerForm(djf.ModelForm):
    class Meta:
        model = m.Answer
        fields = ('content',)


class CommentForm(djf.ModelForm):
    class Meta:
        model = m.Answer
        fields = ('content',)
