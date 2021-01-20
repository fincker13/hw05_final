from django.test import Client, TestCase

class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_availability_page_guest_claent(self):
        pages = [
            '/about/author/',
            '/about/tech/',
        ]
        for page in pages:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_about_correct_template(self):
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
