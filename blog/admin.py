from django.contrib import admin
from blog.models import Blog, BlogPost, Comment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    pass


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass