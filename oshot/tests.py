from django.contrib.auth.models import User, AnonymousUser, Permission
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils import translation
from django.test import TestCase
from django.conf import settings

from social_auth.tests.client import SocialClient

from entities.models import Domain, Division, Entity
from qa.models import Question, Answer

class QuestionTest(TestCase):

    def setUp(self):
        domain = Domain.objects.create(name="test")
        division = Division.objects.create(name="localities", domain=domain, index="3")
        self.entity = Entity.objects.create(name="the moon", division=division,
                                            id=settings.QNA_DEFAULT_ENTITY_ID,
                                            code="1111")
        self.common_user = User.objects.create_user("commoner", 
                                "commmon@example.com", "pass")
        self.candidate_user = User.objects.create_user("candidate", 
                                "candidate@example.com", "pass")
        self.candidate_user.profile.locality = self.entity
        self.candidate_user.profile.is_candidate = True
        self.candidate_user.profile.save()
        self.editor_user = User.objects.create_user("editor", 
                                "editor@example.com", "pass")
        self.editor_user.profile.locality = self.entity
        self.editor_user.profile.is_editor = True
        self.editor_user.profile.save()
        self.q = Question.objects.create(author = self.common_user,
                        subject="why?", entity=self.entity)
        self.a = self.q.answers.create(author = self.candidate_user,
                        content="because the world is round")
        self.site1 = Site.objects.create(domain='abc.com')
        self.site2 = Site.objects.create(domain='fun.com')
        self.q.tags.create(name="abc")
        self.q.tags.create(name="def")
        translation.deactivate_all()

    def test_home_redirect(self):
        """
        According to issue #263, entity urls should only use id's.
        """
        c = Client()
        response = c.get(reverse('local_home'))
        self.assertRedirects(response, reverse('local_home',
                                   kwargs={'entity_id': self.entity.id}))

    def tearDown(self):
        self.q.delete()
        User.objects.all().delete()
