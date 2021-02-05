from django import forms
from django.contrib import admin
from markdownx.widgets import MarkdownxWidget

from documents.models import Document


class DocumentAdminForm(forms.ModelForm):
    content = forms.CharField(widget=MarkdownxWidget())

    class Meta:
        fields = '__all__'
        model = Document


class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm

admin.site.register(Document, DocumentAdmin)
