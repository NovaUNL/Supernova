from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from kleep.models import ChangeLog, Catchphrase


class ChangeLogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        fields = '__all__'
        model = ChangeLog


class ChangeLogAdmin(admin.ModelAdmin):
    form = ChangeLogAdminForm


admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(Catchphrase)
