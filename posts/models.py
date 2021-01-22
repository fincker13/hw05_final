from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE


User = get_user_model() 

class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        blank=True, 
        null=True, 
        help_text='Дайте короткое название группе',
        )
    slug = models.SlugField(
        'Слаг',
        unique=True,
        help_text=('Укажите адрес для страницы задачи. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания')
        )
    description = models.TextField(
        'Описание группы',
        help_text='Дайте короткое описание группы'
    )
    objects = models.Manager()

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=100,
        blank=True, 
        null=True, 
        help_text='Дайте короткое название',
    )
    text = models.TextField(
        'Текст',
        help_text='Напишите текст записи'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации'
    )
    author = models.ForeignKey(
        User, 
        verbose_name='Автор',
        on_delete=models.CASCADE, 
        related_name="posts",
        help_text='Имя автора',
    )
    group = models.ForeignKey(
        Group, 
        verbose_name='Группа',
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name="group",
        help_text='Выберете группу. Это не обязательно',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
    )
    objects = models.Manager()
    
    class Meta:
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий',
        on_delete=models.CASCADE,
        help_text= 'Напите комментарий'
    )
    author = models.ForeignKey(
        User, 
        verbose_name='Автор',
        on_delete=models.CASCADE, 
        related_name="comment",
        help_text='Имя автора',
    )
    text = models.TextField(
        'Текст',
        help_text='Напишите текст записи'
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации коммента',
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:5]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=CASCADE,
        related_name='following',
    )
    objects = models.Manager()
