import datetime as dt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from posts.forms import CommentForm
from posts.forms import PostForm
from posts.models import Follow
from posts.models import Group
from posts.models import Post

User = get_user_model()


def index(request):
    """Returns page with all posts."""
    posts = Post.objects.all()
    page = get_paginator_page(request, posts)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    """Returns Group page with related posts."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = get_paginator_page(request, posts)
    return render(
        request,
        'group.html',
        {'page': page,
         'group': group}
    )


@login_required
def add_comment(request, username, post_id):
    """Adds comment and redirects to post view page."""
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=user, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect(
        reverse(
            'post',
            kwargs={'username': username,
                    'post_id': post_id}
        )
    )


@login_required
def new_post(request):
    """Returns new post page and redirects to home page if post added."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    """Returns profile page with user's posts."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = author.posts.count()
    page = get_paginator_page(request, posts)
    context = {
        'author': author,
        'count': count,
        'page': page
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
        context['following'] = following
    return render(
        request,
        'profile.html',
        context
    )


def post_view(request, username, post_id):
    """Returns single post page."""
    form = CommentForm()
    author = get_object_or_404(User, username=username)
    post = author.posts.get(pk=post_id)
    count = author.posts.count()
    comments = post.comments.all()
    return render(
        request,
        'post.html',
        {'post': post,
         'author': author,
         'comments': comments,
         'form': form,
         'count': count}
    )


@login_required
def post_edit(request, username, post_id):
    """Returns page for editing the post."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    if request.user != author:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if request.method == 'POST' and form.is_valid():
        post.pub_date = dt.datetime.today()
        form.save()
        return redirect(
            "post",
            username=request.user.username,
            post_id=post_id
        )

    return render(
        request, 'new.html', {'form': form, 'post': post},
    )


@login_required
def follow_index(request):
    """Returns page with followed users' posts."""
    posts = Post.objects.filter(author__following__user=request.user)
    page = get_paginator_page(request, posts)
    return render(
        request,
        'follow.html',
        {'page': page, }
    )


@login_required
def profile_follow(request, username):
    """Follows user and redirects po profile page."""
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if request.user != author and not following:
        Follow.objects.create(user=request.user, author=author)
    return redirect(
        reverse(
            'profile',
            kwargs={'username': username, }
        )
    )


@login_required
def profile_unfollow(request, username):
    """Unfollows user and redirects po profile page."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(
        reverse(
            'profile',
            kwargs={'username': username, }
        )
    )


def page_not_found(request, exception):
    """Returns custom 404 error page."""
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Returns custom 500 error page."""
    return render(request, "misc/500.html", status=500)


def get_paginator_page(request, object_list):
    """Helper function that returns paginator object."""
    paginator = Paginator(object_list, settings.RECORDS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
