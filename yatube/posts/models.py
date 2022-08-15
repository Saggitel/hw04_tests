from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы', max_length=200)
    slug = models.SlugField(verbose_name='slug', unique=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу поста'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
