from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q, F, Value, Count, Avg, Max, Case, When, BooleanField, DecimalField, ExpressionWrapper
from decimal import Decimal
from django.db.models.functions import Length
from .models import Watch, Category, Tag
from .forms import AddWatchModelForm, UploadFileForm
from .utils import DataMixin

# Главная страница
class IndexView(DataMixin, ListView):
    model = Watch
    template_name = 'index.html'
    context_object_name = 'watches'
    title_page = 'Главная страница'

    def get_queryset(self):
        return Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)

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
class WatchDetailView(DataMixin, DetailView):
    model = Watch
    template_name = 'watch_detail.html'
    context_object_name = 'watch'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=self.object.title)

# Список часов с фильтрацией
class WatchListView(DataMixin, ListView):
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
        if sort_by not in ['title', '-title', 'price', '-price']:
            sort_by = 'title'
        queryset = queryset.order_by(sort_by)
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
class AddWatchView(DataMixin, CreateView):
    model = Watch
    form_class = AddWatchModelForm
    template_name = 'add_watch.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавить часы'

# Редактирование часов
class UpdateWatchView(DataMixin, UpdateView):
    model = Watch
    form_class = AddWatchModelForm
    template_name = 'add_watch.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование часов'

# Удаление часов
class DeleteWatchView(DataMixin, DeleteView):
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
class FixMissingSlugsView(View):
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