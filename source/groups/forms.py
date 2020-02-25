from dal import autocomplete
from django import forms as djf
from groups import models as m


class RoleForm(djf.ModelForm):
    class Meta:
        model = m.Role
        fields = '__all__'


RolesFormSet = djf.inlineformset_factory(m.Group, m.Role, form=RoleForm, extra=1)


class GroupMemberForm(djf.ModelForm):
    class Meta:
        model = m.GroupMember
        fields = ('member', 'role', 'group')
        widgets = {
            'member': autocomplete.ModelSelect2(url='users:nickname_ac'),
            'role': autocomplete.ModelSelect2(url='groups:group_role_ac', forward=['group']),
        }


# GroupMembershipFormSet = djf.inlineformset_factory(m.User, m.Role, form=GroupMemberForm, extra=3)
GroupMembershipFormSet = djf.inlineformset_factory(m.Group, m.GroupMember, extra=3, form=GroupMemberForm)
