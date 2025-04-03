from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Watch, WatchStatus, Category

def index(request):
    # Получаем данные из базы данных
    watches = Watch.objects.all()
    categories = Category.objects.all()
    
    context = {
        'headline': 'АРХЕТИП',
        'description': 'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году, они появились в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...',
        'cta': 'Доступно сейчас',
        'image_url': 'images/Urban.webp',
        'title': 'Главная страница',
        'watches': watches,
        'categories': categories,
        'cat_selected': 0,
    }
    return render(request, 'index.html', context)

def show_category(request, cat_id):
    # Получаем данные о часах по категории из базы данных
    if cat_id == 0:
        watches = Watch.objects.all()
    else:
        watches = Watch.objects.by_category(cat_id)
    
    categories = Category.objects.all()
    
    context = {
        'headline': 'АРХЕТИП',
        'description': 'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году, они появились в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...',
        'cta': 'Доступно сейчас',
        'image_url': 'images/123.jpg',
        'title': 'Категория часов',
        'watches': watches,
        'categories': categories,
        'cat_selected': cat_id,
    }
    return render(request, 'index.html', context)

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
    """Список всех часов с возможностью фильтрации и сортировки"""
    watches = Watch.objects.all()
    
    # Фильтрация
    search_query = request.GET.get('search', '')
    if search_query:
        watches = watches.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    category_id = request.GET.get('category_id', '')
    if category_id and category_id.isdigit():
        watches = watches.filter(category_id=int(category_id))
    
    status = request.GET.get('status', '')
    if status:
        watches = watches.filter(status=status)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'title')
    if sort_by not in ['title', '-title', 'price', '-price']:
        sort_by = 'title'
    watches = watches.order_by(sort_by)
    
    # Получаем все категории
    categories = Category.objects.all()
    
    context = {
        'title': 'Все часы',
        'watches': watches,
        'categories': categories,
        'statuses': WatchStatus,
        'current_sort': sort_by,
        'current_search': search_query,
        'current_category': category_id,
        'current_status': status,
    }
    return render(request, 'watch_list.html', context)

def watch_detail(request, slug):
    """Детальное представление часов по слагу"""
    watch = get_object_or_404(Watch, slug=slug)
    category = Category.objects.filter(id=watch.category_id).first()
    
    context = {
        'title': watch.title,
        'watch': watch,
        'category': category,
    }
    return render(request, 'watch_detail.html', context)

def watch_create(request):
    """Создание новых часов"""
    if request.method == 'POST':
        # Обработка формы
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        # Безопасное преобразование цены в decimal
        try:
            price = request.POST.get('price', '0')
            # Заменяем запятую на точку, если она есть
            price = price.replace(',', '.')
            # Проверяем, что значение можно преобразовать в число
            price = float(price)
        except (ValueError, TypeError):
            price = 0
            
        category_id = request.POST.get('category_id')
        status = request.POST.get('status', 'AVAILABLE')
        image = request.POST.get('image', '')
        
        if title and category_id:
            watch = Watch(
                title=title,
                description=description,
                price=price,
                category_id=category_id,
                status=status,
                image=image
            )
            watch.save()
            return redirect('watch_detail', slug=watch.slug)
    
    # Получаем все категории для формы
    categories = Category.objects.all()
    
    # Отображение формы
    context = {
        'title': 'Добавление часов',
        'categories': categories,
        'statuses': WatchStatus,
    }
    return render(request, 'watch_form.html', context)

def watch_update(request, slug):
    """Обновление часов"""
    watch = get_object_or_404(Watch, slug=slug)
    
    if request.method == 'POST':
        # Обработка формы
        watch.title = request.POST.get('title')
        watch.description = request.POST.get('description', '')
        
        # Безопасное преобразование цены в decimal
        try:
            price = request.POST.get('price', '0')
            # Заменяем запятую на точку, если она есть
            price = price.replace(',', '.')
            # Проверяем, что значение можно преобразовать в число
            watch.price = float(price)
        except (ValueError, TypeError):
            watch.price = 0
            
        watch.category_id = request.POST.get('category_id')
        watch.status = request.POST.get('status', 'AVAILABLE')
        watch.image = request.POST.get('image', '')
        
        watch.save()
        return redirect('watch_detail', slug=watch.slug)
    
    # Получаем все категории для формы
    categories = Category.objects.all()
    
    # Отображение формы
    context = {
        'title': 'Редактирование часов',
        'watch': watch,
        'categories': categories,
        'statuses': WatchStatus,
    }
    return render(request, 'watch_form.html', context)

def watch_delete(request, slug):
    """Удаление часов"""
    watch = get_object_or_404(Watch, slug=slug)
    
    if request.method == 'POST':
        watch.delete()
        return redirect('watch_list')
    
    context = {
        'title': 'Удаление часов',
        'watch': watch,
        'statuses': WatchStatus,
    }
    return render(request, 'watch_confirm_delete.html', context)

# Категории
def category_list(request):
    """Список всех категорий"""
    categories = Category.objects.all()
    
    context = {
        'title': 'Категории часов',
        'categories': categories,
    }
    return render(request, 'category_list.html', context)

def category_create(request):
    """Создание новой категории"""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name:
            category = Category(name=name)
            category.save()
            return redirect('category_list')
    
    context = {
        'title': 'Добавление категории',
    }
    return render(request, 'category_form.html', context)

def category_update(request, slug):
    """Обновление категории"""
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        return redirect('category_list')
    
    context = {
        'title': 'Редактирование категории',
        'category': category,
    }
    return render(request, 'category_form.html', context)

def category_delete(request, slug):
    """Удаление категории"""
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    
    context = {
        'title': 'Удаление категории',
        'category': category,
    }
    return render(request, 'category_confirm_delete.html', context)
