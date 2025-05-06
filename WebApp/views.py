import uuid
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.urls import reverse_lazy
from django.db.models import Q, F, Value, Count, Avg, Max, Min, Case, When, BooleanField, DecimalField, ExpressionWrapper
from django.db.models.functions import Length
from .models import Watch, Category, Tag
from decimal import Decimal
from .forms import AddWatchForm, AddWatchModelForm, UploadFileForm

def index(request):
    watches = Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
    categories = Category.objects.all()
    
    context = {
        'title': 'Главная страница',
        'watches': watches,
        'categories': categories,
        'headline': 'АРХЕТИП',
        'cta': 'Смотреть все часы',
        'description': 'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году, они появились в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...',
    }
    return render(request, 'index.html', context)

def show_category(request, cat_id):
    if cat_id == 0:
        watches = Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
    else:
        watches = Watch.objects.filter(category_id=cat_id, is_published=Watch.WatchStatus.PUBLISHED)
    
    categories = Category.objects.all()
    
    context = {
        'title': 'Категория часов',
        'watches': watches,
        'categories': categories,
        'cat_selected': cat_id,
        'current_sort': 'title',
        'current_search': '',
        'current_category': str(cat_id),
    }
    return render(request, 'watch_list.html', context)

def show_watch(request, watch_id):
    # Получаем данные о конкретных часах из базы данных
    watch = get_object_or_404(Watch, id=watch_id)
    
    context = {
        'title': watch.title,
        'watch': watch,
    }
    return render(request, 'watch.html', context)


# Служебное представление для восстановления слагов
def fix_missing_slugs(request):
    """Исправление отсутствующих слагов для часов и категорий"""
    if not request.user.is_staff:
        return redirect('home')
        
    watches_fixed = 0
    categories_fixed = 0
    
    # Исправляем слаги у часов
    watches = Watch.objects.filter(slug='')
    for watch in watches:
        watch.save()  # метод save() автоматически создаст слаг
        watches_fixed += 1
    
    # Исправляем слаги у категорий
    categories = Category.objects.filter(slug='')
    for category in categories:
        category.save()  # метод save() автоматически создаст слаг
        categories_fixed += 1
    
    return HttpResponse(
        f'<h1>Исправление слагов</h1>'
        f'<p>Исправлено часов: {watches_fixed}</p>'
        f'<p>Исправлено категорий: {categories_fixed}</p>'
        f'<p><a href="/">Вернуться на главную</a></p>'
    )

# Представления для работы с моделью Watch

def watch_list(request):
    watches = Watch.objects.filter(is_published=Watch.WatchStatus.PUBLISHED)
    
    search_query = request.GET.get('search', '')
    if search_query:
        watches = watches.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    category_id = request.GET.get('category_id', '')
    if category_id and category_id.isdigit():
        watches = watches.filter(category_id=int(category_id))
    
    sort_by = request.GET.get('sort', 'title')
    if sort_by not in ['title', '-title', 'price', '-price']:
        sort_by = 'title'
    watches = watches.order_by(sort_by)
    
    # Аннотация: добавляем поле is_expensive с использованием F и Value
    watches = watches.annotate(
        is_expensive=Case(
            When(price__gt=500000, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )
    
    # Пример использования F: добавляем поле discounted_price (цена со скидкой 10%)
    watches = watches.annotate(
        discounted_price=ExpressionWrapper(
            F('price') * Value(Decimal('0.9')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    
    # Аннотация: длина названия
    watches = watches.annotate(title_length=Length('title'))
    
    # Агрегация: средняя цена и количество часов
    stats = watches.aggregate(
        avg_price=Avg('price'),
        total_watches=Count('id')
    )
    
    categories = Category.objects.annotate(total=Count('watch')).filter(total__gt=0)
    
    context = {
        'title': 'Все часы',
        'watches': watches,
        'categories': categories,
        'current_sort': sort_by,
        'current_search': search_query,
        'current_category': category_id,
        'stats': stats,
    }
    return render(request, 'watch_list.html', context)

def watch_detail(request, slug):
    watch = get_object_or_404(Watch, slug=slug, is_published=Watch.WatchStatus.PUBLISHED)
    
    context = {
        'title': watch.title,
        'watch': watch,
    }
    return render(request, 'watch_detail.html', context)

def stats(request):
    # Группировка по категориям
    category_stats = Category.objects.values('name').annotate(
        total_watches=Count('watch'),
        avg_price=Avg('watch__price')
    )
    
    # Группировка по тегам
    tag_stats = Tag.objects.values('name').annotate(
        total_watches=Count('watches'),
        max_price=Max('watches__price')
    )
    
    context = {
        'title': 'Статистика',
        'category_stats': category_stats,
        'tag_stats': tag_stats,
    }
    return render(request, 'stats.html', context)

# Категории
def category_list(request):
    categories = Category.objects.all()
    
    context = {
        'title': 'Категории часов',
        'categories': categories,
    }
    return render(request, 'category_list.html', context)

def show_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    watches = Watch.objects.filter(tags=tag, is_published=Watch.WatchStatus.PUBLISHED)
    categories = Category.objects.all()
    
    context = {
        'title': f'Тег: {tag.name}',
        'watches': watches,
        'categories': categories,
        'current_sort': 'title',
        'current_search': '',
        'current_category': '',
    }
    return render(request, 'watch_list.html', context)

def add_watch(request):
    if request.method == 'POST':
        form = AddWatchModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddWatchModelForm()
    
    context = {
        'title': 'Добавить часы',
        'form': form,
    }
    return render(request, 'add_watch.html', context)

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(form.cleaned_data['file'])
            return redirect('home')
    else:
        form = UploadFileForm()
    
    context = {
        'title': 'Загрузка файла',
        'form': form,
    }
    return render(request, 'upload_file.html', context)

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