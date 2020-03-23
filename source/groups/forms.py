from dal import autocomplete
from django import forms as djf
from groups import models as m
from supernova.fields import NativeSplitDateTimeField
from supernova.widgets import SliderInput, NativeTimeInput


class GroupForm(djf.ModelForm):
    def __init__(self, group, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['default_role'].queryset = group.roles

    class Meta:
        model = m.Group
        fields = ('description', 'image', 'outsiders_openness', 'default_role', 'place')
        widgets = {
            'place': autocomplete.ModelSelect2(url='college:place_ac')
        }


# TODO audit the usage of this
class RoleForm(djf.ModelForm):
    class Meta:
        model = m.Role
        fields = '__all__'
        exclude = ('group',)
        widgets = {
            'is_admin': SliderInput(),
            'can_modify_roles': SliderInput(),
            'can_assign_roles': SliderInput(),
            'can_announce': SliderInput(),
            'can_read_conversations': SliderInput(),
            'can_write_conversations': SliderInput(),
            'can_read_internal_conversations': SliderInput(),
            'can_write_internal_conversations': SliderInput(),
            'can_read_internal_documents': SliderInput(),
            'can_write_internal_documents': SliderInput(),
            'can_write_public_documents': SliderInput(),
            'can_change_schedule': SliderInput()}


# TODO audit the usage of this
class MembershipForm(djf.ModelForm):
    class Meta:
        model = m.Membership
        fields = ('member', 'role', 'group')
        widgets = {
            'member': autocomplete.ModelSelect2(url='users:nickname_ac'),
            'role': autocomplete.ModelSelect2(url='groups:group_role_ac', forward=['group'])}


# TODO figure how to limit a form field queryset through this
# to prevent attacks such as asking for a role from other group
GroupMembershipFormSet = djf.inlineformset_factory(m.Group, m.Membership, extra=3, form=MembershipForm)


class AnnounceForm(djf.ModelForm):
    class Meta:
        model = m.Announcement
        fields = ('title', 'content')


class ScheduleOnceForm(djf.ModelForm):
    datetime = NativeSplitDateTimeField()

    class Meta:
        model = m.ScheduleOnce
        fields = ('title', 'datetime', 'duration')
        widgets = {'duration': djf.NumberInput(attrs={'min': 0, 'max': 24 * 60, 'size': 3})}


GroupScheduleOnceFormset = djf.inlineformset_factory(m.Group, m.ScheduleOnce, extra=1, form=ScheduleOnceForm)


class SchedulePeriodicForm(djf.ModelForm):
    start_date = NativeSplitDateTimeField()
    end_date = NativeSplitDateTimeField()

    class Meta:
        model = m.SchedulePeriodic
        fields = ('title', 'weekday', 'time', 'duration', 'start_date', 'end_date')
        widgets = {
            'time': NativeTimeInput(),
            'duration': djf.NumberInput(attrs={'min': 0, 'max': 24 * 60, 'size': 3})
        }


GroupSchedulePeriodicFormset = djf.inlineformset_factory(m.Group, m.SchedulePeriodic, extra=1,
                                                         form=SchedulePeriodicForm)
