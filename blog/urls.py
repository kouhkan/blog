from django.urls import path
from . import views
from .feeds import ListPostFeed


app_name = 'blog'


urlpatterns = [
	path('', views.post_list, name='post_list'),
	path('feed/', ListPostFeed(), name='post_feeds'),
	path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
	path('post-share/<int:post_id>/', views.post_share, name='post_share'),
	path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
]