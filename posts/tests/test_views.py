import os
import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User, Follow


INDEX_URL = reverse('index')
NEW_URL = reverse('new')
GROUP_URL = reverse('group', kwargs={'slug': 'group-group'})
SECOND_GROUP_URL = reverse('group', kwargs={'slug': 'second-group'})
PROFILE_URL = reverse('profile', kwargs={'username': 'testuser'})
FOLLOW_INDEX = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', kwargs={'username': 'testuser_2'})
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', kwargs={'username': 'testuser_3'})
small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
        )

class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='testuser')
        cls.user_2 = User.objects.create(username='testuser_2')
        cls.user_3 = User.objects.create(username='testuser_3')
        Follow.objects.create(
            user=PostViewTest.user,
            author=PostViewTest.user_3
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='group-group',
            description='Test description',
        )
        Group.objects.create(
            title='вторая тестовая группа',
            slug='second-group',
            description='Test description',
        )
        
        for i in range(1, 15):
            Post.objects.create(
                title=f'Test title:{i}',
                text=f'Test text:{i}',
                author=PostViewTest.user_3,
                group=PostViewTest.group,
            )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
                title='Test title',
                text='Test text',
                author=PostViewTest.user,
                group=PostViewTest.group,
                image=PostViewTest.uploaded
            )
        cls.POST_EDIT_URL = reverse(
            'post_edit',
            kwargs={'username':'testuser','post_id':f'{PostViewTest.post.id}'}
            )
        cls.POST_URL = reverse(
            'post',
            kwargs={'username':'testuser','post_id':f'{PostViewTest.post.id}'}
            )
        cls.COMMENT_URL = reverse(
            'add_comment',
            kwargs={'username':'testuser','post_id':f'{PostViewTest.post.id}'}
            )
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.user)
        
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': INDEX_URL,
            'group.html': GROUP_URL,
            'new.html': NEW_URL
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
    
    def test_index_page_show_correct_context(self):
        """Шаблоны index/group сформированы с правильным контекстом."""
        post = PostViewTest.post
        pages = [INDEX_URL, GROUP_URL]
        for page in pages:
            with self.subTest():  
                response =self.authorized_client.get(page)
                self.assertEqual(response.context.get('page')[0].title, post.title)
                self.assertEqual(response.context.get('page')[0].text, post.text)
                self.assertEqual(response.context.get('page')[0].author, post.author)
                self.assertEqual(response.context.get('page')[0].group, post.group)
                self.assertEqual(response.context.get('page')[0].image, post.image)
        
    def test_now_page_show_correct_context(self):
        """Шаблон new сформированн с правильным контекстом"""
        response = self.authorized_client.get(NEW_URL)
        form_fields ={
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_contains_index(self):
        """После публикации поста новая запись появляется на главной страницах(index/group)"""
        post = PostViewTest.post
        pages = [INDEX_URL,GROUP_URL]
        for page in pages:
            with self.subTest():
                response = self.authorized_client.get(page)
                self.assertContains(response, post.text)

    def test_new_post_not_contains_others_group(self):
        """После публикации поста новая запись не доступна в других круппах"""
        response = self.authorized_client.get(SECOND_GROUP_URL)
        self.assertNotContains(response, PostViewTest.post.text)

    def test_profile_page_show_correct_context(self):
        """Шаблон pofile сформирован с правильным контекстом"""
        post = PostViewTest.post
        response = self.guest_client.get(PROFILE_URL)
        self.assertEqual(response.context.get('page')[0].text, post.text)
        self.assertEqual(response.context.get('page')[0].author, post.author)
        self.assertEqual(response.context.get('page')[0].group, post.group)
        self.assertEqual(response.context.get('page')[0].image, post.image)
        self.assertEqual(response.context.get('post_count'), 1)

    def test_post_new_page_show_correct_context(self):
        """Шаблон post_edit сформированн с правильным контекстом"""
        post = PostViewTest.post
        response = self.authorized_client.get(PostViewTest.POST_EDIT_URL)
        form_fields ={
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
    
    def test_post_show_correct_context(self):
        """Шаблон post_view сформированн с правильным контекстом"""
        post = PostViewTest.post
        response = self.guest_client.get(PostViewTest.POST_URL)
        self.assertEqual(response.context.get('profile').username, 'testuser')
        self.assertEqual(response.context.get('post').text, post.text)
        self.assertEqual(response.context.get('post').author, post.author)
        self.assertEqual(response.context.get('post').group, post.group)
        self.assertEqual(response.context.get('post').image, post.image)
        self.assertEqual(response.context.get('post_count'), 1)

    def test_foolow(self):
        """Авторизованный пользователь может подписываться на других пользователей"""
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['follows'], 2)

    def test_foolow(self):
        """Авторизованный пользователь может отдписываться от других пользователей"""
        self.authorized_client.get(PROFILE_UNFOLLOW_URL)
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['follows'], 0)

    def test_follows_news_lent(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан"""
        response = self.authorized_client.get(FOLLOW_INDEX)
        self.assertContains(response, 'Test text:1')
    
    def test_unfollows_news_nent(self):
        """Новая запись пользователя не появляется в ленте тех, кто на него не подписан"""
        self.authorized_client.get(PROFILE_UNFOLLOW_URL)
        response = self.authorized_client.get(FOLLOW_INDEX)
        self.assertNotContains(response, 'Test text:1')

    def test_comment_authorized(self):
        """Авторизированный пользователь может комментировать посты."""
        self.authorized_client.post(PostViewTest.COMMENT_URL, {'text': 'Test comment'})
        response = self.authorized_client.get(PostViewTest.POST_URL)
        self.assertContains(response, 'Test comment')

    def test_comment_unauthorized(self):
        """Не авторизированный пользователь не может комментировать посты."""
        self.guest_client.post(PostViewTest.COMMENT_URL, {'text': 'Test comment'})
        response = self.authorized_client.get(PostViewTest.POST_URL)
        self.assertNotContains(response, 'Test comment')

    def test_pagenators_index(self):
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.guest_client.get(INDEX_URL + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 5)

    def test_cache_index_page(self):
        self.guest_client.get(INDEX_URL)
        Post.objects.create(
                title='Test title',
                text='Test cache text',
                author=PostViewTest.user,
                group=PostViewTest.group,
        )
        response = self.guest_client.get(INDEX_URL)
        self.assertNotContains(response, 'Test cache text')
        cache.clear()
        response_2 = self.guest_client.get(INDEX_URL)
        self.assertContains(response_2, 'Test cache text')
