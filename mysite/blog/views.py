from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    """GET - список постов."""

    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, post_slug):
    """RETRIEVE - получение поста по дате и слагу."""

    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post_slug,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
