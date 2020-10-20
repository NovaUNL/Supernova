from django import forms as djf
from supernova import models as m
from supernova.widgets import SliderInput


class SupportPledgeForm(djf.ModelForm):
    class Meta:
        model = m.SupportPledge
        fields = ('pledge_towards', 'anonymous', 'comment')
        widgets = {
            'pledge_towards': djf.RadioSelect(),
            'anonymous': SliderInput(),
        }
