"""blueblog URL Configuration
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
"""

from unicodedata import name
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path

from accounts.views import UserRegistrationView
from django.contrib.auth import views as auth_views

from blog.views import NewBlogView, HomeView, UpdateBlogView, NewPostView, UpdatePostView


# https://docs.djangoproject.com/en/4.0/topics/auth/default/

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', HomeView.as_view(), name='home'),
    path('new-user/', UserRegistrationView.as_view(), name='user_registration'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('blog/new/', NewBlogView.as_view(), name='new-blog'),
    path('blog/<int:pk>/edit-blog/', UpdateBlogView.as_view(), name='edit-blog'),
    
    path('blog/new-post/', NewPostView.as_view(), name='new-post'),
    path('blog/<int:pk>/edit-post/', UpdatePostView.as_view(), name='edit-post'),
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
