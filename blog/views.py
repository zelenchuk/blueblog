from django.urls import reverse
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.utils.text import slugify
from django.views.generic import CreateView, TemplateView, UpdateView
from django.http.response import HttpResponseForbidden

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from blog.models import Blog, BlogPost
from blog.forms import BlogForm, PostForm


# https://docs.djangoproject.com/en/4.0/topics/class-based-views/intro/

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            if Blog.objects.filter(owner=self.request.user).exists():
                context['has_blog'] = True
                blog = Blog.objects.get(owner=self.request.user)
                context['blog'] = blog
                context['posts'] = BlogPost.objects.filter(blog=blog)
        else:
            context['posts'] = BlogPost.objects.filter(is_published=True)
        return context


class NewBlogView(CreateView):
    form_class = BlogForm
    template_name = 'blog_settings.html'

    def form_valid(self, form):
        blog_obj = form.save(commit=False)
        blog_obj.owner = self.request.user
        blog_obj.slug = slugify(blog_obj.title)

        blog_obj.save()
        return HttpResponseRedirect(reverse('home'))

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Do something for authenticated users.
            user = request.user
            if Blog.objects.filter(owner=user).exists():
                return HttpResponseForbidden('You can not create more than one blogs per account')
            else:
                return super(NewBlogView, self).dispatch(request, *args, **kwargs)
        else:
            # Do something for anonymous users.
            return HttpResponseNotFound()  # raise 404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Создать блог'
        context['button_name'] = 'Сохранить'
        return context


class UpdateBlogView(UpdateView):
    form_class = BlogForm
    template_name = 'blog_settings.html'
    success_url = '/'
    model = Blog

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать блог'
        context['button_name'] = 'Обновить'
        return context


class NewPostView(CreateView):
    form_class = PostForm
    template_name = 'blog_post.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        blog_post_obj = form.save(commit=False)
        blog_post_obj.blog = Blog.objects.get(owner=self.request.user)
        blog_post_obj.slug = slugify(blog_post_obj.title)
        blog_post_obj.is_published = True

        blog_post_obj.save()
        return HttpResponseRedirect(reverse('home'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Создать пост'
        context['button_name'] = 'Сохранить пост'
        return context


class UpdatePostView(UpdateView):
    form_class = PostForm
    template_name = 'blog_post.html'
    success_url = '/'
    model = BlogPost

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать пост'
        context['button_name'] = 'Обновить пост'
        return context
