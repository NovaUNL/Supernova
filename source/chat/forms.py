from django import forms as djf

from chat import models as m


class MessageForm(djf.ModelForm):
    class Meta:
        model = m.Message
        fields = ('content',)
