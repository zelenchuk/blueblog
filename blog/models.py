from django.contrib.auth.models import User
from django.db import models


class Blog(models.Model):
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=500)

    slug = models.CharField(max_length=500, editable=False)


class BlogPost(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=500)
    body = models.TextField('Основной текст')
    is_published = models.BooleanField('Опубликован?', default=False)
    slug = models.SlugField(max_length=500, editable=False)
    shared_to = models.ManyToManyField(Blog, related_name='shared_posts')


class Comment(models.Model):
    body = models.TextField("Комментарий")

    commented_on = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    in_reply_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.DO_NOTHING)

    commented_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
