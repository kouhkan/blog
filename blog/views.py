from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def post_share(request, post_id):
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False
	if request.method == "POST":
		form = EmailPostForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = f"{cd['name']} recommends you read {post.title}"
			message = f"Read {post.title} at {post_url} \n\n{cd['name']}\'s comments: {cd['comments']}"
			send_mail(subject, message, settings.EMAIL_HOST_USER, (cd['to'], ))
			sent = True
	else:
		form = EmailPostForm()

	context = {
		'form': form,
		'post': post,
		'sent': sent
	}
	return render(request, 'blog/share.html', context)


# class PostListView(ListView):
# 	queryset = Post.published.all()
# 	context_object_name = 'posts'
# 	paginate_by = 3
# 	template_name = 'blog/list.html'


def post_list(request, tag_slug=None):
	tag = None

	object_list = Post.published.all()

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])

	paginator = Paginator(object_list, 3)
	page = request.GET.get('page')
	try:
		object_list = paginator.page(page)
	except PageNotAnInteger:
		object_list = paginator.page(1)
	except EmptyPage:
		object_list = paginator.page(paginator.num_pages)

	context = {
		'posts': object_list,
		'page': page,
		'tag': tag
	}
	return render(request, 'blog/list.html', context)


def post_detail(request, year, month, day, slug):
	post = get_object_or_404(Post,
	                         status='published',
	                         publish__year=year,
	                         publish__month=month,
	                         publish__day=day,
	                         slug=slug)
	# Retrieve
	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

	new_comment = None
	if request.method == 'POST':
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.post = post
			new_comment.save()
	else:
		comment_form = CommentForm()

	context = {
		'post': post,
		'new_comment': new_comment,
		'comment_form': comment_form,
		'similar_posts': similar_posts,
		'comments': Comment.objects.filter(active=True)
	}
	return render(request, 'blog/detail.html', context)


def post_search(request):
	form = SearchForm()
	query = None
	results = []

	if 'query' in request.GET:
		form = SearchForm(request.GET)
		if form.is_valid():
			search_vector = SearchVector('title', 'body')
			search_query = SearchQuery(query)
			results = Post.published.annotate(
					search=search_vector,
					rank=SearchRank(search_vector, search_query)
			).filter(search=search_query).order_by('-rank')

	context = {
		'form': form,
		'query': query,
		'results': results
	}
	return render(request, 'blog/search.html', context)