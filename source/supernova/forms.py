from django import forms as djf
from supernova import models as m


class ChangelogForm(djf.ModelForm):
    broadcast_notification = djf.BooleanField(required=False)

    class Meta:
        model = m.Changelog
        fields = '__all__'
