from django.test import TestCase

from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
            title='Test group',
            slug='group-group',
            description='Test description',
        )
        cls.post = Post.objects.create(
            id=1,
            title='Test title',
            text='Test text',
            author=PostModelTest.user,
            group=PostModelTest.group,
        )
    
    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses_post = {
            'title': 'Заголовок',
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses_post.items():
          with self.subTest(value=value):
              self.assertEqual(
                  post._meta.get_field(value).verbose_name, expected)  

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses_group = {
            'title': 'Название группы',
            'slug': 'Слаг',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses_group.items():
          with self.subTest(value=value):
              self.assertEqual(
                  group._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts_post = {
            'title': 'Дайте короткое название',
            'text': 'Напишите текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Имя автора',
            'group': 'Выберете группу. Это не обязательно'
        }
        for value, expected in field_help_texts_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)  

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts_group = {
            'title': 'Дайте короткое название группе',
            'slug': ('Укажите адрес для страницы задачи. Используйте '
                     'только латиницу, цифры, дефисы и знаки '
                     'подчёркивания'),
            'description': 'Дайте короткое описание группы',
        }
        for value, expected in field_help_texts_group.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str_post_model(self):
        """__str__ совпадает с ожидаемым."""
        post = PostModelTest.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post))

    def test_str_group_model(self):
        """__str__ совпадает с ожидаемым."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
                    