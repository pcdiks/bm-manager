from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Collection


class HomeViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass")
        self.collection1 = Collection.objects.create(
            name="c1", owner=self.user1
        )

    def test_user_cannot_access_others_collection(self):
        """Home view should return 404 for a collection not owned by the user."""
        self.client.login(username="user2", password="pass")
        response = self.client.get(
            reverse("home"), {"collection": self.collection1.id}
        )
        self.assertEqual(response.status_code, 404)

