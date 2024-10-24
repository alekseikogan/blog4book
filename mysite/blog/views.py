from django.contrib.postgres.search import SearchVector
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm
from .models import Post

POST_PER_PAGE = 4

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'  # результат запроса в бд, по умочанию назвается object_list
    paginate_by = POST_PER_PAGE
    template_name = 'blog/post/list.html'

    # тут пагинатор отдает объект страницы с именем page_obj


def post_list(request, tag_slug=None):
    """GET - список постов."""

    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        # используется взаимосвязь многие-ко-многим, 
        # необходимо фильтровать записи по тегам, содержащимся в заданном 
        # списке, который в данном случае содержит только один элемент.
        # используется операция __in поиска по полю
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, POST_PER_PAGE)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag})


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

    # возвращает кортежи со значениями заданных полей. Ему передается параметр flat=True, чтобы 
    # получить одиночные значения
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                            .exclude(id=post.id)
    # similar_posts - число тегов, общих со всеми запрошенными тегами
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


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
    """Публикация комментария к записи."""

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


def post_search(request):
    """Поиск по вектору полей title и body."""

    form = SearchForm
    query = None
    results = []

    if query in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                search=SearchVector('title', 'body'),
            ).filter(search=query)
        
        return render(request,
                      'blog/post/search.html',
                      {'form': form,
                       'query': query,
                       'results': results})
