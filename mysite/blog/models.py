from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class PublishedManager(models.Manager):
    """Переопределение менеджера объектов для 
    получения всех опубликованных постов."""

    def get_queryset(self):
        return super().get_queryset()\
                      .filter(status=Post.Status.PUBLISHED)  


# class PostQuerySet(models.QuerySet):
#     """Второй вариант для модификации менеджера."""

#     def published(self):
#         return self.objects.filter(status=Post.status.PUBLISHED)


class Post(models.Model):
    """Класс Публикация."""

    class Status(models.TextChoices):
       """Класс Статус для публикации."""

       DRAFT = 'DF', 'Draft'
       PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250, verbose_name='Заголовок')
    slug = models.SlugField(max_length=250, verbose_name='Slug')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts')
    body = models.TextField(verbose_name='Содержание')
    publish = models.DateTimeField(default=timezone.now, verbose_name='Опубликовано')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Изменено')
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус')
    
    objects = models.Manager()
    published = PublishedManager()
    
    # objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-publish']
        indexes = [
         models.Index(fields=['-publish'])]
    
    def __str__(self):
        return self.title