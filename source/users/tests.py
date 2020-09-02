from datetime import datetime, timedelta

from django.contrib import auth
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

import settings
from users import models as m, forms as f
from college import models as college


class InviteRegistrationTest(TestCase):
    def setUp(self):
        self.user_admin = m.User.objects.create(
            nickname="admin",
            username="admin",
            password="",
            is_staff=True,
            is_superuser=True)
        self.user_standalone = m.User.objects.create(
            nickname="standalone_nick",
            username="standalone_user",
            password="")
        self.user_student = m.User.objects.create(
            nickname="student_nick",
            username="student_user",
            password="")
        self.student_free = college.Student.objects.create(abbreviation='existing')
        self.student_associated = college.Student.objects.create(abbreviation='associated', user=self.user_student)

    def test_campus_email_enforcement(self):
        m.Invite.objects.create(
            token='CAMPUSEMAIL',
            issuer=self.user_standalone,
            expiration=datetime.now() + timedelta(days=1))
        college.Student.objects.create(
            abbreviation='campusemailtest')
        registration_data = {
            'username': 'campusemailtest',
            'nickname': 'campusemailtest',
            'student': 'campusemailtest',
            'email': 'campusemailtest@' + settings.CAMPUS_EMAIL_SUFFIX,
            'invite': 'CAMPUSEMAIL',
            'password': 'queijo-123',
            'password_confirmation': 'queijo-123'}

        form = f.RegistrationForm(data=registration_data)
        self.assertTrue(form.is_valid())
        registration_data['email'] = 'campusemailtest@fct.unl.pt'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['email'] = 'campusemailtest@xmail.pom'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())

    def test_name_policy(self):
        invite = m.Invite.objects.create(
            token='NAMEPOLICY',
            issuer=self.user_standalone,
            expiration=datetime.now() + timedelta(days=1))
        student = college.Student.objects.create(abbreviation='namepolicy')
        unused_identifier = 'unused'
        registration_data = {
            'username': unused_identifier,
            'nickname': unused_identifier,
            'student': student.abbreviation,
            'email': f"{student.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}",
            'invite': invite.token,
            'password': 'queijo-123',
            'password_confirmation': 'queijo-123'}

        # Valid data
        form = f.RegistrationForm(data=registration_data)
        self.assertTrue(form.is_valid())
        # Nickname conflict
        registration_data['nickname'] = self.student_free.abbreviation
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['nickname'] = unused_identifier
        # Username conflict
        registration_data['username'] = self.student_free.abbreviation
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        # Bad username
        registration_data['username'] = unused_identifier + ' space'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['username'] = '>' + unused_identifier
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['username'] = '12345'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['username'] = ''
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['username'] = unused_identifier
        # Bad nickname
        registration_data['nickname'] = unused_identifier + ' space'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['nickname'] = '>' + unused_identifier
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['nickname'] = '12345'
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['nickname'] = ''
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['nickname'] = unused_identifier
        # Test with email conflict
        registration_data['email'] = f"{self.student_associated.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}"
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['email'] = f"{student.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}"
        registration_data['student'] = self.student_associated.abbreviation
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['student'] = student.abbreviation
        # Test with student-email mismatch
        registration_data['student'] = self.student_free.abbreviation
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['student'] = student.abbreviation
        registration_data['email'] = f"{self.student_free.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}"
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        registration_data['email'] = f"{student.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}"

    def test_invite_expiration(self):
        revoked_invite = m.Invite.objects.create(
            token='REVOKEDINVITE',
            issuer=self.user_standalone,
            expiration=datetime.now() + timedelta(days=1),
            revoked=True)
        old_invite = m.Invite.objects.create(
            token='OLDINVITE',
            issuer=self.user_standalone,
            expiration=datetime.now() - timedelta(days=1))
        student = college.Student.objects.create(abbreviation='invitexpiration')

        registration_data = {
            'username': 'free',
            'nickname': 'free',
            'student': student.abbreviation,
            'email': f"{student.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}",
            'invite': revoked_invite.token,
            'password': 'queijo-123',
            'password_confirmation': 'queijo-123'}
        # Register with revoked invite
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())
        # Register with old invite
        registration_data['registration_data'] = old_invite.token
        form = f.RegistrationForm(data=registration_data)
        self.assertFalse(form.is_valid())

    def test_registration(self):
        invite = m.Invite.objects.create(
            token='REGISTRATION',
            issuer=self.user_standalone,
            expiration=datetime.now() + timedelta(days=1))
        student = college.Student.objects.create(abbreviation='registration-user')
        client = Client()
        page = client.post(
            reverse('registration'),
            data={
                'username': 'registration-user',
                'nickname': 'registration-user',
                'student': student.abbreviation,
                'email': f"{student.abbreviation}@{settings.CAMPUS_EMAIL_SUFFIX}",
                'invite': invite.token,
                'password': 'queijo-123',
                'password_confirmation': 'queijo-123'})
        invite.refresh_from_db()
        registration = invite.registration
        self.assertIsNotNone(registration)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(registration.token in mail.outbox[0].body)
        self.assertEquals(page.url, reverse('registration_validation'))
        page = client.post(
            reverse('registration_validation'),
            data={
                'email': registration.email,
                'token': registration.token})
        invite.refresh_from_db()
        logged_user = auth.get_user(client)
        created_user = invite.resulting_user
        self.assertEquals(logged_user, created_user)
        self.assertIsNotNone(created_user)
        self.assertEquals(page.url, reverse('users:profile', args=[created_user.nickname]))
        self.assertTrue(student in created_user.students.all())
