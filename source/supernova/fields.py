from django.forms import SplitDateTimeField

from supernova import widgets


class NativeSplitDateTimeField(SplitDateTimeField):
    widget = widgets.NativeSplitDateTimeWidget


class NativeDateField(SplitDateTimeField):
    widget = widgets.NativeDateInput


class NativeTimeField(SplitDateTimeField):
    widget = widgets.NativeTimeInput
