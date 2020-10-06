import re
from itertools import chain

from django import forms as djf
from college import models as m

IDENTIFIER_EXP = re.compile('(?!^\d+$)^[\da-zA-Z-_.]+$')


class Loggable(djf.ModelForm):
    def get_changes(self):
        changes = {'attrs': self.changed_data}
        old, new = dict(), dict()
        for changed_attr in (attr for attr in self.Meta.loggable_fields if attr in self.changed_data):
            old[changed_attr] = self.initial[changed_attr]
            new[changed_attr] = self.cleaned_data[changed_attr]
        changes['old'] = old
        changes['new'] = new
        return changes


class CourseForm(Loggable, djf.ModelForm):
    class Meta:
        model = m.Course
        fields = ('description', 'department', 'url', 'coordinator')
        loggable_fields = ('description', 'department', 'url')


class DepartmentForm(Loggable, djf.ModelForm):
    class Meta:
        model = m.Department
        fields = ('description', 'building', 'picture', 'url', 'email', 'phone', 'president')
        loggable_fields = ('description', 'phone', 'url', 'email')


class ClassForm(Loggable, djf.ModelForm):
    class Meta:
        model = m.Class
        fields = ('description', 'url')
        loggable_fields = ('description', 'url')


class TeacherForm(Loggable, djf.ModelForm):
    class Meta:
        model = m.Teacher
        fields = ('picture', 'url', 'email', 'phone', 'rank')
        loggable_fields = ('url', 'email', 'phone')


def merge_changes(old_changes, new_changes):
    original = old_changes['old']
    # intermediary = old_changes['new']
    future = new_changes['new']
    attrs = list(set(chain(old_changes['attrs'], new_changes['attrs'])))
    # Check for reverted changes
    for attr in original.keys():
        if attr in future and original[attr] == future[attr]:
            attrs.remove(attr)
            future.pop(original, None)
            future.pop(attr, None)
    return {
        'old': original,
        'new': original,
        'attrs': attrs
    }
