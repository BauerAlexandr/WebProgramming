from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, F, Value, Count, Avg, Max, Case, When, BooleanField, DecimalField, ExpressionWrapper, IntegerField
from decimal import Decimal
from django.db.models.functions import Length
from .models import Watch, Category, Tag, UserContent, Comment, Like, Cart, CartItem
from .forms import AddWatchModelForm, UploadFileForm, UserContentForm, CommentForm
from .utils import DataMixin
import uuid
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

# Главная страница
class IndexView(DataMixin, ListView):
    model = Watch
    template_name = 'index.html'
    context_object_name = 'watches'
    title_page = 'Главная страница'

    def get_queryset(self):
        queryset = Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
        # Предварительная аннотация
        queryset = queryset.annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes__is_like=True)),
            dislikes_count=Count('likes', distinct=True, filter=Q(likes__is_like=False)),
            comment_count=Count('comments', distinct=True)
        )
        for watch in queryset:
            watch.like_count = watch.likes_count - watch.dislikes_count
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
            headline='АРХЕТИП',
            cta='Смотреть все часы',
            description=(
                'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены '
                'немецкими колесами дня и месяца. Созданные в 1989 году, они появились '
                'в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...'
            )
        )

# Часы по категории
class CategoryView(DataMixin, ListView):
    model = Watch
    template_name = 'watch_list.html'
    context_object_name = 'watches'
    allow_empty = False
    title_page = 'Категория часов'

    def get_queryset(self):
        cat_id = self.kwargs.get('cat_id')
        if cat_id == 0:
            return Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
        return Watch.objects.filter(
            category_id=cat_id, is_published=Watch.WatchStatus.PUBLISHED
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
            cat_selected=self.kwargs.get('cat_id'),
            current_sort='title',
            current_search='',
            current_category=str(self.kwargs.get('cat_id'))
        )

# Детали часов
class WatchDetailView(PermissionRequiredMixin, DataMixin, DetailView):
    permission_required = 'WebApp.view_watch'
    raise_exception = True
    model = Watch
    template_name = 'watch_detail.html'
    context_object_name = 'watch'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watch = self.get_object()
        user = self.request.user
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(watch=watch, is_approved=True)
        context['can_edit'] = user.is_authenticated and user.has_perm('WebApp.change_watch')
        if user.is_authenticated:
            context['has_liked'] = Like.objects.filter(user=user, watch=watch, is_like=True).exists()
            context['has_disliked'] = Like.objects.filter(user=user, watch=watch, is_like=False).exists()
            context['like_count'] = watch.likes.filter(is_like=True).count()
            context['dislike_count'] = watch.likes.filter(is_like=False).count()
        return self.get_mixin_context(context, title=self.object.title)

# Список часов с фильтрацией
class WatchListView(PermissionRequiredMixin, DataMixin, ListView):
    permission_required = 'WebApp.view_watch'
    raise_exception = True
    model = Watch
    template_name = 'watch_list.html'
    context_object_name = 'watches'
    title_page = 'Все часы'

    def get_queryset(self):
        queryset = Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        category_id = self.request.GET.get('category_id', '')
        if category_id and category_id.isdigit():
            queryset = queryset.filter(category_id=int(category_id))
        sort_by = self.request.GET.get('sort', 'title')
        if sort_by in ['title', '-title', 'price', '-price']:
            queryset = queryset.order_by(sort_by)
        else:
            sort_by = 'title'
        # Аннотация для подсчета лайков и комментариев
        queryset = queryset.annotate(
            likes_count=Count('likes', distinct=True, filter=Q(likes__is_like=True)),
            dislikes_count=Count('likes', distinct=True, filter=Q(likes__is_like=False)),
            comment_count=Count('comments', distinct=True)
        )
        for watch in queryset:
            watch.like_count = watch.likes_count - watch.dislikes_count
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
            current_sort=self.request.GET.get('sort', 'title'),
            current_search=self.request.GET.get('search', ''),
            current_category=self.request.GET.get('category_id', ''),
            stats=self.get_queryset().aggregate(
                avg_price=Avg('price'),
                total_watches=Count('id')
            )
        )

# Статистика
class StatsView(DataMixin, TemplateView):
    template_name = 'stats.html'
    title_page = 'Статистика'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context,
            category_stats=Category.objects.values('name').annotate(
                total_watches=Count('watch'),
                avg_price=Avg('watch__price')
            ),
            tag_stats=Tag.objects.values('name').annotate(
                total_watches=Count('watches'),
                max_price=Max('watches__price')
            )
        )

# Список категорий
class CategoryListView(DataMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    title_page = 'Категории часов'

# Часы по тегу
class TagView(DataMixin, ListView):
    model = Watch
    template_name = 'watch_list.html'
    context_object_name = 'watches'
    allow_empty = False

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return Watch.objects.filter(tags=tag, is_published=Watch.WatchStatus.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context,
            title=f'Тег: {tag.name}',
            current_sort='title',
            current_search='',
            current_category='',
            stats=self.get_queryset().aggregate(
                avg_price=Avg('price'),
                total_watches=Count('id')
            )
        )

# Добавление часов
class AddWatchView(PermissionRequiredMixin, DataMixin, CreateView):
    permission_required = 'WebApp.add_watch'
    raise_exception = True
    model = Watch
    form_class = AddWatchModelForm
    template_name = 'add_watch.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавить часы'

# Редактирование часов
class UpdateWatchView(PermissionRequiredMixin, DataMixin, UpdateView):
    permission_required = 'WebApp.change_watch'
    raise_exception = True
    model = Watch
    form_class = AddWatchModelForm
    template_name = 'add_watch.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование часов'

# Удаление часов
class DeleteWatchView(PermissionRequiredMixin, DataMixin, DeleteView):
    permission_required = 'WebApp.delete_watch'
    raise_exception = True
    model = Watch
    template_name = 'watch_delete.html'
    success_url = reverse_lazy('home')
    title_page = 'Удаление часов'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, watch=self.object)

# Загрузка файла
class UploadFileView(DataMixin, FormView):
    form_class = UploadFileForm
    template_name = 'upload_file.html'
    success_url = reverse_lazy('home')
    title_page = 'Загрузка файла'

    def form_valid(self, form):
        handle_uploaded_file(form.cleaned_data['file'])
        return super().form_valid(form)

# Исправление слагов (опционально как CBV)
class FixMissingSlugsView(PermissionRequiredMixin, View):
    permission_required = 'WebApp.change_watch'
    raise_exception = True

    def get(self, request):
        if not request.user.is_staff:
            return redirect('home')
        watches_fixed = 0
        categories_fixed = 0
        watches = Watch.objects.filter(slug='')
        for watch in watches:
            watch.save()
            watches_fixed += 1
        categories = Category.objects.filter(slug='')
        for category in categories:
            category.save()
            categories_fixed += 1
        return HttpResponse(
            f'<h1>Исправление слагов</h1>'
            f'<p>Исправлено часов: {watches_fixed}</p>'
            f'<p>Исправлено категорий: {categories_fixed}</p>'
            f'<p><a href="/">Вернуться на главную</a></p>'
        )

def handle_uploaded_file(f):
    name = f.name
    ext = ''
    if '.' in name:
        ext = name[name.rindex('.'):]
        name = name[:name.rindex('.')]
    suffix = str(uuid.uuid4())
    with open(f"media/uploads/{name}_{suffix}{ext}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@permission_required('WebApp.can_discount_watch', raise_exception=True)
def apply_discount(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    watch.price = watch.price * Decimal('0.90')  # Скидка 10%
    watch.save()
    return redirect('watch', slug=watch.slug)

# Пользовательский контент - список
class UserContentListView(DataMixin, ListView):
    model = UserContent
    template_name = 'user_content_list.html'
    context_object_name = 'contents'
    title_page = 'Пользовательский контент'

    def get_queryset(self):
        return UserContent.objects.filter(is_published=True)

# Пользовательский контент - детальная страница
class UserContentDetailView(DataMixin, DetailView):
    model = UserContent
    template_name = 'user_content_detail.html'
    context_object_name = 'content'
    slug_url_kwarg = 'slug'
    title_page = 'Контент'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()
        user = self.request.user
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            user_content=content, is_approved=True
        )
        context['can_edit'] = user.is_authenticated and user == content.author
        if user.is_authenticated:
            context['has_liked'] = Like.objects.filter(
                user=user, user_content=content, is_like=True
            ).exists()
            context['has_disliked'] = Like.objects.filter(
                user=user, user_content=content, is_like=False
            ).exists()
            context['like_count'] = content.likes.filter(is_like=True).count()
            context['dislike_count'] = content.likes.filter(is_like=False).count()
        return self.get_mixin_context(context, title=content.title)

# Создание пользовательского контента
class AddUserContentView(LoginRequiredMixin, DataMixin, CreateView):
    model = UserContent
    form_class = UserContentForm
    template_name = 'add_user_content.html'
    success_url = reverse_lazy('user_content_list')
    title_page = 'Добавить контент'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# Редактирование пользовательского контента
class UpdateUserContentView(LoginRequiredMixin, DataMixin, UpdateView):
    model = UserContent
    form_class = UserContentForm
    template_name = 'add_user_content.html'
    success_url = reverse_lazy('user_content_list')
    title_page = 'Редактировать контент'

    def get_queryset(self):
        return UserContent.objects.filter(author=self.request.user)

# Удаление пользовательского контента
class DeleteUserContentView(LoginRequiredMixin, DataMixin, DeleteView):
    model = UserContent
    template_name = 'user_content_delete.html'
    success_url = reverse_lazy('user_content_list')
    title_page = 'Удаление контента'

    def get_queryset(self):
        return UserContent.objects.filter(author=self.request.user)

# Добавление комментария
class AddCommentView(LoginRequiredMixin, DataMixin, FormView):
    form_class = CommentForm
    template_name = 'add_comment.html'
    title_page = 'Добавить комментарий'

    def form_valid(self, form):
        watch = None
        user_content = None
        if 'slug' in self.kwargs:
            watch = get_object_or_404(Watch, slug=self.kwargs['slug'])
        elif 'content_slug' in self.kwargs:
            user_content = get_object_or_404(UserContent, slug=self.kwargs['content_slug'])
        
        Comment.objects.create(
            watch=watch,
            user_content=user_content,
            author=self.request.user,
            text=form.cleaned_data['text']
        )
        if watch:
            return HttpResponseRedirect(reverse_lazy('watch', kwargs={'slug': watch.slug}))
        return HttpResponseRedirect(reverse_lazy('user_content', kwargs={'slug': user_content.slug}))

# Лайк/дизлайк
class LikeActionView(LoginRequiredMixin, View):
    def get(self, request, slug=None, content_slug=None, action=None):
        user = request.user
        if slug:
            obj = get_object_or_404(Watch, slug=slug)
            like, created = Like.objects.get_or_create(
                user=user, watch=obj, defaults={'is_like': action == 'like'}
            )
            if not created:
                like.is_like = action == 'like'
                like.save()
            return redirect('watch', slug=slug)
        elif content_slug:
            obj = get_object_or_404(UserContent, slug=content_slug)
            like, created = Like.objects.get_or_create(
                user=user, user_content=obj, defaults={'is_like': action == 'like'}
            )
            if not created:
                like.is_like = action == 'like'
                like.save()
            return redirect('user_content', slug=content_slug)
        return redirect('home')

@login_required
def add_to_cart(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, watch=watch)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('watch', slug=slug)

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    cart_total = sum(item.watch.price * item.quantity for item in cart_items)
    # Добавляем итоговую стоимость для каждого товара
    cart_items_with_totals = [{'item': item, 'total': item.watch.price * item.quantity} for item in cart_items]

    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        if action == 'update':
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
                item.quantity = quantity
                item.save()
        elif action == 'remove':
            item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            item.delete()
        return redirect('cart')

    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items_with_totals,
        'cart_total': cart_total,
    })