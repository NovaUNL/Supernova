from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse

from users import models as users
from college import models as college
from learning import models as m
from learning import forms as f
from learning import views as v


class LearningTest(TestCase):
    def setUp(self):
        self.privileged_user = users.User.objects.create(
            username='privileged',
            nickname='privileged',
            password='whatever')
        self.privileged_user.user_permissions.add(
            Permission.objects.get(
                codename='add_section',
                content_type=ContentType.objects.get_for_model(m.Section)))
        self.privileged_user.user_permissions.add(
            Permission.objects.get(
                codename='change_section',
                content_type=ContentType.objects.get_for_model(m.Section)))
        self.regular_user = users.User.objects.create(
            username='normie',
            nickname='normie',
            password='whatever')
        self.area = m.Area.objects.create(title="Area")
        self.subarea = m.Subarea.objects.create(title="Subrea", area=self.area)
        self.section = m.Section.objects.create(title="Subsection")
        self.class_ = college.Class.objects.create(name='Foo', department=college.Department.objects.create(name='Foo'))
        m.ClassSection(corresponding_class=self.class_, section=self.section, index=0)
        m.SectionSubsection(parent=self.section, section=self.section, index=0)

    def test_area_form(self):
        area_form_data = {'title': 'test_areas'}
        area_form = f.AreaForm(data=area_form_data)
        self.assertTrue(area_form.is_valid())
        subarea_form_data = {
            'title': 'test_areas',
            'description': 'Lorem Ipsum',
            'area': self.area.id
        }
        subarea_form = f.AreaForm(data=subarea_form_data)
        self.assertTrue(subarea_form.is_valid())

    def test_section_creation_views(self):
        initial_section_count = m.Section.objects.count()
        no_formsets_data = {
            'sources-TOTAL_FORMS': '0',
            'sources-INITIAL_FORMS': '0',
            'sources-MAX_NUM_FORMS': '',
            'wp_resources-TOTAL_FORMS': '0',
            'wp_resources-INITIAL_FORMS': '0',
            'wp_resources-MAX_NUM_FORMS': '',
            'doc_resources-TOTAL_FORMS': '0',
            'doc_resources-INITIAL_FORMS': '0',
            'doc_resources-MAX_NUM_FORMS': ''}
        some_formset_data = {
            'sources-TOTAL_FORMS': '1',
            'sources-INITIAL_FORMS': '0',
            'sources-MIN_NUM_FORMS': '0',
            'sources-MAX_NUM_FORMS': '1000',
            'sources-0-id': '',
            'sources-0-title': 'Test 123',
            'sources-0-url': 'http://example.com',
            'wp_resources-TOTAL_FORMS': '1',
            'wp_resources-INITIAL_FORMS': '0',
            'wp_resources-MIN_NUM_FORMS': '0',
            'wp_resources-MAX_NUM_FORMS': '1000',
            'wp-resources-0-id': '',
            'wp-resources-0-title': 'Test 123',
            'wp-resources-0-url': 'http://example.com',
            'doc_resources-TOTAL_FORMS': '0',
            'doc_resources-INITIAL_FORMS': '0',
            'doc_resources-MIN_NUM_FORMS': '0',
            'doc_resources-MAX_NUM_FORMS': '1000'}
        client = Client()

        # # Before logging in
        # response = client.post(
        #     reverse('learning:subarea_section_create', args=[self.subarea.id]),
        #     data={
        #         'title': 'Testing section creation 1',
        #         'content_md': 'Lorem ipsum',
        #         'subarea': self.subarea.id,
        #         'requirements': []})
        # self.assertRedirects(response, reverse('login'))
        # self.assertEqual(section_count, m.Section.objects.count())
        # response = client.post(
        #     reverse('learning:subsection_create', args=[self.section.id]),
        #     data={
        #         'title': 'Testing section creation 2',
        #         'content_md': 'Lorem ipsum',
        #         'requirements': []})
        # self.assertRedirects(response, reverse('login'))
        # self.assertEqual(section_count, m.Section.objects.count())

        # Submission with lack os privileges
        client.force_login(self.regular_user)
        response = client.post(
            reverse('learning:subarea_section_create', args=[self.subarea.id]),
            data={
                'title': 'Testing section creation 1',
                'content_md': 'Lorem ipsum',
                'requirements': []})
        self.assertEqual(403, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count, m.Section.objects.count())
        response = client.post(
            reverse('learning:subsection_create', args=[self.section.id]),
            data={
                'title': 'Testing section creation 2',
                'content_md': 'Lorem ipsum',
                'requirements': []})
        self.assertEqual(403, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count, m.Section.objects.count())

        # Submission without formsets
        client.force_login(self.privileged_user)
        response = client.post(
            reverse('learning:subarea_section_create', args=[self.subarea.id]),
            data={
                'title': 'Testing section creation 3',
                'content_md': 'Lorem ipsum',
                'requirements': [],
                **no_formsets_data
            })
        self.assertEqual(302, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count + 1, m.Section.objects.count())
        section = m.Section.objects.get(title='Testing section creation 3')
        self.assertEqual(section.content_md, 'Lorem ipsum')
        self.assertEqual(section.subarea, self.subarea)
        self.assertEqual(section.sources.count(), 0)
        self.assertEqual(section.resources.count(), 0)
        response = client.post(
            reverse('learning:subsection_create', args=[self.section.id]),
            data={
                'title': 'Testing section creation 4',
                'content_md': 'Lorem ipsum',
                'requirements': [],
                **no_formsets_data
            })
        self.assertEqual(302, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count + 2, m.Section.objects.count())
        section = m.Section.objects.get(title='Testing section creation 4')
        self.assertEqual(section.subarea, None)
        self.assertTrue(self.section in section.parents.all())
        self.assertEqual(section.sources.count(), 0)
        self.assertEqual(section.resources.count(), 0)

        # Now with formsets
        response = client.post(
            reverse('learning:subarea_section_create', args=[self.subarea.id]),
            data={
                'title': 'Testing section creation 5',
                'content_md': 'Lorem ipsum',
                'requirements': [],
                **some_formset_data
            })
        self.assertEqual(302, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count + 3, m.Section.objects.count())
        section = m.Section.objects.get(title='Testing section creation 5')
        self.assertEqual(section.subarea, self.subarea)
        self.assertEqual(section.sources.count(), 1)
        self.assertEqual(section.sources.first().title, "Test 123")
        self.assertEqual(section.sources.first().url, "http://example.com")
        self.assertEqual(section.resources.count(), 1)
        response = client.post(
            reverse('learning:subsection_create', args=[self.section.id]),
            data={
                'title': 'Testing section creation 6',
                'content_md': 'Lorem ipsum',
                'requirements': [],
                **some_formset_data
            })
        self.assertEqual(302, response.status_code)
        self.assertEqual(response.resolver_match.func, v.section_create_view)
        self.assertEqual(initial_section_count + 4, m.Section.objects.count())
        section = m.Section.objects.get(title='Testing section creation 6')
        self.assertEqual(section.subarea, None)
        self.assertTrue(self.section in section.parents.all())
        self.assertEqual(section.sources.count(), 1)
        self.assertEqual(section.sources.first().title, "Test 123")
        self.assertEqual(section.sources.first().url, "http://example.com")
        self.assertEqual(section.resources.count(), 1)
