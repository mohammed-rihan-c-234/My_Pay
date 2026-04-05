from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Document


@override_settings(SECURE_SSL_REDIRECT=False)
class DocumentVaultTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="rihan", password="12345")

    def test_dashboard_uploads_document_for_logged_in_user(self):
        self.client.login(username="rihan", password="12345")
        response = self.client.post(
            reverse("dashboard"),
            {
                "action": "add_document",
                "document_type": Document.TYPE_AADHAAR,
                "theme": Document.THEME_AURORA,
                "holder_name": "Rihan",
                "date_of_birth": "2001-01-15",
                "aadhaar_number": "123456789012",
                "notes": "Front copy",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.get().user, self.user)
        self.assertEqual(Document.objects.get().aadhaar_number, "1234 5678 9012")

    def test_pan_document_requires_valid_pan_number(self):
        self.client.login(username="rihan", password="12345")
        response = self.client.post(
            reverse("dashboard"),
            {
                "action": "add_document",
                "document_type": Document.TYPE_PAN,
                "theme": Document.THEME_ROYAL,
                "holder_name": "Rihan",
                "pan_number": "12345",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Use a valid PAN format like ABCDE1234F.")
        self.assertEqual(Document.objects.count(), 0)
