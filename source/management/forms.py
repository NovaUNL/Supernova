from dal import autocomplete
from django import forms as djf
from django.core.exceptions import ValidationError

from supernova import models as supernova
from users import models as users, triggers
from college import models as college
from users.registrations import generate_token


class ChangelogForm(djf.ModelForm):
    broadcast_notification = djf.BooleanField(required=False)

    class Meta:
        model = supernova.Changelog
        fields = '__all__'


class ReputationOffsetForm(djf.ModelForm):
    class Meta:
        model = users.ReputationOffset
        fields = ('receiver', 'amount', 'reason')
        widgets = {'receiver': autocomplete.ModelSelect2(url='users:nickname_ac')}


class BindStudentToUserForm(djf.Form):
    user = djf.IntegerField(widget=autocomplete.Select2(url='users:nickname_ac'))
    student = djf.IntegerField(widget=autocomplete.Select2(url='college:unreg_student_ac'))

    def clean_user(self):
        user_id = self.cleaned_data.get("user")
        return users.User.objects.filter(id=user_id).first()

    def clean_student(self):
        student_id = self.cleaned_data.get("student")
        return college.Student.objects.filter(id=student_id, user=None).first()

    def save(self):
        user: users.User = self.cleaned_data.get('user')
        student: college.Student = self.cleaned_data.get('student')
        if student.user is not None:
            triggers.student_assignment(user, student)
        else:
            raise ValidationError(f"Student {student.name} is already assigned to user {student.user.nickname}")


class BindTeacherToUserForm(djf.Form):
    user = djf.IntegerField(widget=autocomplete.Select2(url='users:nickname_ac'))
    teacher = djf.IntegerField(widget=autocomplete.Select2(url='college:unreg_teacher_ac'))

    def clean_user(self):
        user_id = self.cleaned_data.get("user")
        return users.User.objects.filter(id=user_id).first()

    def clean_teacher(self):
        teacher_id = self.cleaned_data.get("teacher")
        return college.Teacher.objects.filter(id=teacher_id, user=None).first()

    def save(self):
        user: users.User = self.cleaned_data.get('user')
        teacher: college.Teacher = self.cleaned_data.get('teacher')
        if teacher.user is None:
            triggers.teacher_assignment(user, teacher)
        else:
            raise ValidationError(f"Teacher {teacher.name} is already assigned to user {teacher.user.nickname}")


class PasswordResetForm(djf.Form):
    user = djf.IntegerField(widget=autocomplete.Select2(url='users:nickname_ac'))

    def clean_user(self):
        user_id = self.cleaned_data.get("user")
        return users.User.objects.filter(id=user_id).first()

    def save(self):
        user: users.User = self.cleaned_data.get('user')
        new_password = generate_token(length=10)
        user.set_password(new_password)
        user.save()
        return new_password
