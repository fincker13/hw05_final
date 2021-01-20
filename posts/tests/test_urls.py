from django.contrib.auth import REDIRECT_FIELD_NAME
from posts.tests.test_views import GROUP_URL, PROFILE_URL, PostViewTest
from django.http import response
from django.test import TestCase, Client

from posts.models import Group, Post, User


INDEX_URL = '/'
NEW_URL = '/new/'
GROUP_URL = '/group/group-group/'
PROFILE_URL = '/testuser/'
REDIRECT_URL = '/auth/login/?next='

class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.user_2 = User.objects.create(username = 'testuser_2') 
        cls.group = Group.objects.create(
            title='Test group',
            slug='group-group',
            description='Test description',
        )
        cls.post = Post.objects.create(
            title='Test title',
            text='Test text',
            author=PostURLTests.user,
            group=PostURLTests.group,
        )
        cls.POST_URL = f'/testuser/{PostURLTests.post.id}/'
        cls.POST_EDIT_URL = f'/testuser/{PostURLTests.post.id}/edit/'
        cls.post_2 = Post.objects.create(
            title='какоу-то название',
            text='какой-то текст',
            author=PostURLTests.user_2,
            group=PostURLTests.group,
        )
        cls.POST_2_URL = f'/testuser_2/{PostURLTests.post_2.id}/'
        cls.POST_2_EDIT_URL = f'/testuser_2/{PostURLTests.post_2.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)        
    
    def test_availability_page_guest_claent(self):
        """Страници доступны любым пользователям"""
        post = PostURLTests.post
        pages = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            PostURLTests.POST_URL,
            ]

        for page in pages:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)
    
    def test_availability_page_auth_claent(self):
        """Страница доступна авторизованному пользователю/автору поста"""
        post = PostURLTests.post
        pages = [
            NEW_URL,
            PostURLTests.POST_EDIT_URL,
            ]

        for page in pages:
            with self.subTest():
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, 200) 

    def test_redirects_page(self):
        """Страница переадресует на нужные страници"""
        post = PostURLTests.post
        redirects_pages = {
            '/new/': REDIRECT_URL+NEW_URL,
            PostURLTests.POST_EDIT_URL:
            REDIRECT_URL+PostURLTests.POST_EDIT_URL,
        }
        for page, redirect_page in redirects_pages.items():
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertRedirects(response, redirect_page)

    def test_not_author_post(self):
        """Страница post_edit не доступна не владельцу поста."""
        post_2 = PostURLTests.post_2
        response = self.authorized_client.get(
            PostURLTests.POST_2_EDIT_URL)
        self.assertRedirects(response, INDEX_URL)

    def test_urls_uses_correct_template(self):
        post = PostURLTests.post
        templates_url_names = {
            'index.html': INDEX_URL,
            'group.html': GROUP_URL,
            'new.html': NEW_URL,
            'post_new.html':PostURLTests.POST_EDIT_URL
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
