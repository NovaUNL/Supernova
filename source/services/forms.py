from dal import autocomplete
from django import forms as djf
from services import models as m
from college import models as college


class ServiceForm(djf.ModelForm):

    # place = djf.ModelChoiceField(
    #     queryset=college.Place.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='college:place_ac')
    # )

    class Meta:
        model = m.Service
        fields = '__all__'
        widgets = {
            'place': autocomplete.ModelSelect2(url='college:place_ac')}
