from django.test import Client, TestCase
from django.urls import reverse

class AboutViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        
    def test_about_pages_accessible_by_name(self):
        """URL, генерируемый при помощи имени, доступен."""
        pages = [
            'about:author',
            'about:tech',
        ]
        for page in pages:
            with self.subTest():
                response = self.guest_client.get(reverse(page))
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к страницам применяется правильный шаблон"""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
