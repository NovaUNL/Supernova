from dal import autocomplete
from django import forms as djf
from supernova import models as supernova
from users import models as users


class ChangelogForm(djf.ModelForm):
    broadcast_notification = djf.BooleanField(required=False)

    class Meta:
        model = supernova.Changelog
        fields = '__all__'


class ReputationOffsetForm(djf.ModelForm):
    class Meta:
        model = users.ReputationOffset
        fields = ('receiver', 'amount', 'reason')
        widgets = {'receiver': autocomplete.ModelSelect2(url='users:nickname_ac')}
