from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django.forms import ModelForm, TextInput, CharField, formset_factory, Form, forms

from exercises.models import Exercise
from exercises.widgets import ExerciseWidget


class ExerciseForm(ModelForm):
    """
    | Base exercise form. Enough to validate returns, yet meant to be extended client side.
    | Ideally this would have a custom widget to create and return the whole model ``content``.
    """

    class Meta:
        model = Exercise
        fields = ("content", "source", "source_url", "synopses_sections")
        widgets = {
            'content': ExerciseWidget(),
            'synopses_sections': autocomplete.ModelSelect2Multiple(url='synopses:section_ac'),
            'source': TextInput(attrs={'placeholder': '1.4, exercícios de xyz'}),
            'source_url': TextInput(attrs={'placeholder': 'https://exemplo.com/exercicios'}),
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        self._validate_exercise(content)
        return content

    # TODO move this to a custom Field and throw proper exceptions
    @staticmethod
    def _validate_exercise(exercise, min_length=10):
        if 'type' not in exercise:
            raise forms.ValidationError(f"Exercício com tipo em falta.")
        etype = exercise['type']
        if etype == "group":
            if 'enunciation' not in exercise or 'subproblems' not in exercise:
                raise forms.ValidationError("Grupo com campos em falta")
            enunciation, subproblems = exercise['enunciation'], exercise['subproblems']
            if type(enunciation) is not str or type(subproblems) is not list or len(subproblems) < 2:
                raise forms.ValidationError("Grupo com tipos inválidos")
            exercise['enunciation'] = enunciation = enunciation.strip()
            map(ExerciseForm._validate_exercise, subproblems)
        elif etype == "write":
            if 'enunciation' not in exercise or 'answer' not in exercise:
                raise forms.ValidationError("Questão com campos em falta")
            enunciation, answer = exercise['enunciation'], exercise['answer']
            if type(enunciation) is not str or type(answer) is not str:
                raise forms.ValidationError("Questão com tipos inválidos")
            enunciation, _ = exercise['enunciation'], exercise['answer'] = enunciation.strip(), answer.strip()
        elif etype == "select":
            if 'enunciation' not in exercise or 'candidates' not in exercise or 'answerIndex' not in exercise:
                raise forms.ValidationError("Escolha múltipla com parametros em falta")
            enunciation, candidates, index = exercise['enunciation'], exercise['candidates'], exercise['answerIndex']
            if type(enunciation) is not str or type(candidates) is not list or type(index) is not int:
                raise forms.ValidationError("Escolha múltipla com tipos inválidos")
            if (candidate_count := len(candidates)) < 2 \
                    or not all(map(lambda x: type(x) is str, candidates)) \
                    or index < 0 \
                    or index >= candidate_count:
                raise forms.ValidationError("Escolha múltipla com parametros inválidos")
            exercise['enunciation'] = enunciation = enunciation.strip()
            for i, candidate in enumerate(candidates):
                if len(s := candidate.strip()) > 0:
                    candidates[i] = s
                else:
                    raise forms.ValidationError("Alinea vazia")
        else:
            raise forms.ValidationError(f"Tipo de exercício desconhecido: '{exercise['type']}'")

        if (l := len(enunciation)) < min_length:
            raise forms.ValidationError(f"Enunciado demasiado curto. ({l} caráteres)")

        return True


class AnswerForm(Form):
    """
    Generic rich text answer
    """
    answer = CharField(widget=CKEditorWidget(), label="Resposta:")


#: A formset which will be used to return 1..n answers at once
AnswerFormSet = formset_factory(AnswerForm, extra=1)
