from django.urls import path
from . import views

app_name = 'blog'


urlpatterns = [
	path('', views.PostListView.as_view(), name='post_list'),
	path('post-share/<int:post_id>/', views.post_share, name='post_share'),
	path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
]