from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from supernova.models import Changelog, Catchphrase


class ChangeLogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='complex'))

    class Meta:
        fields = '__all__'
        model = Changelog


class ChangeLogAdmin(admin.ModelAdmin):
    form = ChangeLogAdminForm


admin.site.register(Changelog, ChangeLogAdmin)
admin.site.register(Catchphrase)
