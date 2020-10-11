from django.forms import Widget
from django.forms.utils import to_current_timezone
from django.forms.widgets import boolean_check, MultiWidget, DateInput, TimeInput


class SliderInput(Widget):
    # input_type = 'checkbox'
    template_name = 'widgets/slider.html'

    def __init__(self, attrs=None, check_test=None):
        super().__init__(attrs)
        # check_test is a callable that takes a value and returns True
        # if the checkbox should be checked for that value.
        self.check_test = boolean_check if check_test is None else check_test

    def format_value(self, value):
        """Only return the 'value' attribute if value isn't empty."""
        if value is True or value is False or value is None or value == '':
            return
        return str(value)

    def get_context(self, name, value, attrs):
        if self.check_test(value):
            if attrs is None:
                attrs = {}
            attrs['checked'] = True
        return super().get_context(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            # A missing value means False because HTML form submission does not
            # send results for unselected checkboxes.
            return False
        value = data.get(name)
        # Translate true and false strings to boolean values.
        values = {'true': True, 'false': False}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return bool(value)

    def value_omitted_from_data(self, data, files, name):
        # HTML checkboxes don't appear in POST data if not checked, so it's
        # never known if the value is actually omitted.
        return False


class StarInput(Widget):
    template_name = 'widgets/star_rating_picker.html'

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass


class NativeDateInput(DateInput):
    input_type = 'date'


class NativeTimeInput(TimeInput):
    input_type = 'time'


class NativeSplitDateTimeWidget(MultiWidget):
    supports_microseconds = False
    template_name = 'django/forms/widgets/splitdatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        widgets = (
            NativeDateInput(
                attrs=attrs if date_attrs is None else date_attrs,
                format=date_format,
            ),
            NativeTimeInput(
                attrs=attrs if time_attrs is None else time_attrs,
                format=time_format,
            ),
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time()]
        return [None, None]
