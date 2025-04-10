from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Watch, Category

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

def client(request, client_id):
    if client_id > 3:
        raise Http404()
    
    if request.GET:
        print(request.GET)

    return HttpResponse(f"<h1>Клиент</h1><p>ID: {client_id}</p>")

def event_detail(request, event_date):
    date_if = '2023-01-01'
    if event_date > datetime.strptime(date_if, '%Y-%m-%d'):
        return redirect('/')
    return HttpResponse(f"<h1>Архив за {event_date}</h1>")

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

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
            Q(description__icontains=search_query)
        )
    
    category_id = request.GET.get('category_id', '')
    if category_id and category_id.isdigit():
        watches = watches.filter(category_id=int(category_id))
    
    sort_by = request.GET.get('sort', 'title')
    if sort_by not in ['title', '-title', 'price', '-price']:
        sort_by = 'title'
    watches = watches.order_by(sort_by)
    
    categories = Category.objects.all()
    
    context = {
        'title': 'Все часы',
        'watches': watches,
        'categories': categories,
        'current_sort': sort_by,
        'current_search': search_query,
        'current_category': category_id,
    }
    return render(request, 'watch_list.html', context)

def watch_detail(request, slug):
    watch = get_object_or_404(Watch, slug=slug, is_published=Watch.WatchStatus.PUBLISHED)
    
    context = {
        'title': watch.title,
        'watch': watch,
    }
    return render(request, 'watch_detail.html', context)

# Категории
def category_list(request):
    categories = Category.objects.all()
    
    context = {
        'title': 'Категории часов',
        'categories': categories,
    }
    return render(request, 'category_list.html', context)
