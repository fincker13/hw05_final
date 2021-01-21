import os
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.http import response
from django.urls import reverse

from posts.models import Post, User


INDEX_URL = reverse('index')
NEW_URL = reverse('new')

class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='testuser')
        cls.post = Post.objects.create(
            title = 'Test title',
            text = 'Test text',
            author = PostFormTest.user,
        )
        cls.POST_EDIT_URL = reverse(
            'post_edit', 
            kwargs={'username': 'testuser', 'post_id': PostFormTest.post.id}
            )
        cls.POST_URL = reverse(
            'post', 
            kwargs={'username': 'testuser', 'post_id': PostFormTest.post.id}
            )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_creat_new_post(self):
        """Новый пост создан в базе данных"""
        post_count = Post.objects.count()
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_date ={
            'title': 'Тестовый пост',
            'text': 'Очень содержательный текст',
            'image': uploaded
            }
        response = self.authorized_client.post(
            NEW_URL,
            data=form_date,
            follow=True
            )
        response_index = self.authorized_client.get(INDEX_URL)
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), post_count+1)
        self.assertContains(response_index, 'Очень содержательный текст')

    def test_edit_post(self):
        """Отредактированный пост сохранился в базе данных"""
        post = PostFormTest.post
        post_count = Post.objects.count()
        form_date = {
            'text': 'New test text'
            }
        response = self.authorized_client.post(
            PostFormTest.POST_EDIT_URL,
            data=form_date,
            follow=True
            )
        response_post = self.authorized_client.get(PostFormTest.POST_URL)
        self.assertRedirects(response, PostFormTest.POST_URL)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(Post.objects.get(id=1).text, 'New test text')
        self.assertContains(response_post, 'New test text')
