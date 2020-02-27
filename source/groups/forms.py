from dal import autocomplete
from django import forms as djf
from groups import models as m
from supernova.widgets import SliderInput


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


class MembershipForm(djf.ModelForm):
    class Meta:
        model = m.Membership
        fields = ('member', 'role', 'group')
        widgets = {
            'member': autocomplete.ModelSelect2(url='users:nickname_ac'),
            'role': autocomplete.ModelSelect2(url='groups:group_role_ac', forward=['group'])}


GroupMembershipFormSet = djf.inlineformset_factory(m.Group, m.Membership, extra=3, form=MembershipForm)
