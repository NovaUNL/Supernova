from django.forms import SplitDateTimeField

from supernova.widgets import NativeSplitDateTimeWidget


class NativeSplitDateTimeField(SplitDateTimeField):
    widget = NativeSplitDateTimeWidget
