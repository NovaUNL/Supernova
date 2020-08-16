from django.forms.widgets import HiddenInput


class ExerciseWidget(HiddenInput):
    template_name = 'widgets/editor.html'

    class Media:
        css = {
            'all': ('exercises/style.css',)
        }
        js = ("exercises/editor.js",)
