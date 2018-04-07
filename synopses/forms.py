from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.forms import Form, CharField, ChoiceField


class SynopsisSectionForm(Form):
    after = ChoiceField(label='Após:')
    name = CharField(label='Título', max_length=100, required=True)
    content = CharField(label='', widget=CKEditorUploadingWidget())
