from pyexpat import model
from django.urls import reverse
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.utils.text import slugify
from django.views.generic import CreateView, TemplateView, UpdateView, View, DetailView, DeleteView
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
                context['shared_posts'] = blog.shared_posts.all()
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

    def get_queryset(self):
        queryset = super(UpdateBlogView, self).get_queryset()
        return queryset.filter(owner=self.request.user)

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

    def get_queryset(self):
        queryset = super(UpdatePostView, self).get_queryset()
        return queryset.filter(blog__owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Редактировать пост'
        context['button_name'] = 'Обновить пост'
        return context


class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'post_detail.html'


class ShareBlogPostView(TemplateView):
    template_name = 'share_blog_post.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShareBlogPostView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, pk, **kwargs):
        blog_post = BlogPost.objects.get(pk=pk)
        currently_shared_with = blog_post.shared_to.all()
        currently_shared_with_ids = map(lambda x: x.pk, currently_shared_with)
        exclude_from_can_share_list = [
            blog_post.blog.pk] + list(currently_shared_with_ids)

        can_be_shared_with = Blog.objects.exclude(
            pk__in=exclude_from_can_share_list)

        return {
            'post': blog_post,
            'is_shared_with': currently_shared_with,
            'can_be_shared_with': can_be_shared_with
        }


class SharePostWithBlog(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SharePostWithBlog, self).dispatch(request, *args, **kwargs)

    def get(self, request, post_pk, blog_pk):
        blog_post = BlogPost.objects.get(pk=post_pk)
        if blog_post.blog.owner != request.user:
            return HttpResponseForbidden('You can only share posts that you created')

        blog = Blog.objects.get(pk=blog_pk)
        blog_post.shared_to.add(blog)

        return HttpResponseRedirect(reverse('home'))


class StopSharingPostWithBlog(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StopSharingPostWithBlog, self).dispatch(request, *args, **kwargs)

    def get(self, request, post_pk, blog_pk):
        blog_post = BlogPost.objects.get(pk=post_pk)
        if blog_post.blog.owner != request.user:
            return HttpResponseForbidden('You can only stop sharing posts that you created')

        blog = Blog.objects.get(pk=blog_pk)
        blog_post.shared_to.remove(blog)

        return HttpResponseRedirect(reverse('home'))


class PostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('home')
    template_name = 'confirm_delete.html'
