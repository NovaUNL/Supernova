from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from documents.models import Document


class DocumentAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        fields = '__all__'
        model = Document


class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm

admin.site.register(Document, DocumentAdmin)
