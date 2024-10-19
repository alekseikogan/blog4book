from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.decorators.http import require_POST

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'  # результат запроса в бд, по умочанию назвается object_list
    paginate_by = 3
    template_name = 'blog/post/list.html'

    # тут пагинатор отдает объект страницы с именем page_obj


# def post_list(request):
#     """GET - список постов."""

#     post_list = Post.published.all()
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)

#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)

#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts})


def post_detail(request, year, month, day, post_slug):
    """RETRIEVE - получение поста по дате и слагу."""

    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post_slug,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()


    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form})


def post_share(request, post_id):
    """Отправка поста другому пользователю."""

    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():  # form.errors список ошибок
            cd = form.cleaned_data  # cleaned_data это словарь значений, которые прошли валидацию
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} советует прочитать пост " \
                f"{post.title}"
            message = f"Посмотри пост {post.title}! Вот ссылка - {post_url}\n\n" \
                f"{cd['name']}\' передает: {cd['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html', {'post': post,
                                 'form': form,
                                 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    
    return render(request, 'blog/post/comment.html',
                                        {'post': post,
                                         'form': form,
                                         'comment': comment})