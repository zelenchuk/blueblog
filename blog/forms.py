from django import forms

from blog.models import Blog, BlogPost, Comment


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog

        fields = [
            'title'
        ]


class PostForm(forms.ModelForm):
    class Meta:
        model = BlogPost

        fields = [
            'title',
            'body',
            'is_published',
        ]


class CommentModelForm(forms.ModelForm):
    link_pk = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Comment
        fields = ('body',)
