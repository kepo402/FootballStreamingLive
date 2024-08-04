# matches/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('live/', views.live_matches, name='live_matches'),
    path('blog/<int:pk>/', views.blog_post_detail, name='blog_post_detail'),
    path('donate/', views.donate, name='donate'),  # URL pattern for donate
]

