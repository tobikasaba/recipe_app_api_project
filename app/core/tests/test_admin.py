"""Tests for django admin modifications"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):
    """Tests for Django admin"""

    # set up method allows us to set up some modules at the beginning of the different test i the class
    # this is run before every test
    def setUp(self):
        """Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_users_list(self):
        """Test that users are listed on page."""

        """
        Generate the URL for the admin user changelist page
        reverse('admin:core_user_changelist'): This is a Django utility function (reverse) that generates the URL for a
        given view. In this case, it generates the URL for the Django admin view where the list of users is displayed.
        The 'admin:core_user_changelist' is the URL name for the user changelist in the Django admin.
        The reverse() function ensures the URL is generated dynamically, so if you change the URL pattern,
        you don't have to update the test manually.
        """
        url = reverse('admin:core_user_changelist')

        # Send a GET request to the URL and store the response in 'res'
        res = self.client.get(url)

        # Check if the user's name is included in the response content
        self.assertContains(res, self.user.name)
        # Check if the user's email is included in the response content
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user pade works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
