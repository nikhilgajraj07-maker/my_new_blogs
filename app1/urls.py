from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView, custom_logout_view, contact_view
from .views import import_data

urlpatterns = [
    # Home pages
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('homepage/', views.homepage, name='homepage'),
    path('app2/', views.homepage2, name='homepage2'),

    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile', views.profile, name='profile'),
    path("import-data/", import_data),
    

    # Static pages
    path('about/', views.about, name='about'),

    # Blog related
    path('blog/', views.blog_view, name='blog_view'),
    path('blog/', views.blog_view, name='blog'),
    path('blog_page/', views.blog_view, name='blog_page'),
    path("blogs/<int:blog_id>/", views.blog_detail, name="blog_detail"),
    path("blogs/<int:blog_id>/comment/", views.add_comment, name="add_comment"),
    path("comments/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path('single-blog/<int:blog_id>/', views.single_blog, name='single_blog'),
    path('blog/<int:pk>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    # Searchable blogs list
    path('blogs/', views.all_blogs, name='blogs'),
    path('all-blogs/', views.all_blogs, name='all_blogs'),

    # Feedback and Contact
    path('feedback/', views.feedback_view, name='feedback'),
    path('contact/', contact_view, name='contact'),

    # Load more
    path("load-more-blogs/", views.load_more_blogs, name="load_more_blogs"),

    # Image upload for Quill
    
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("ai-assistant/", views.ai_assistant, name="ai_assistant"),
    path("blogs/<int:pk>/like/", views.toggle_like, name="blog_like"),
    path("blogs/<int:pk>/bookmark/", views.toggle_bookmark, name="blog_bookmark"),
]
