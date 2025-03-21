from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import redirect, render
from datetime import datetime

# Список часов
watches_db = [
    {
        'id': 1,
        'title': 'Urban Jürgensen Reference 2',
        'description': 'Эти часы из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году...',
        'category_id': 1,
        'is_available': True
    },
    {
        'id': 2,
        'title': 'Patek Philippe Calatrava',
        'description': 'Классические часы с минималистичным дизайном, идеально подходящие для делового стиля...',
        'category_id': 2,
        'is_available': False
    },
    {
        'id': 3,
        'title': 'Rolex Submariner',
        'description': 'Легендарные дайверские часы, известные своей надежностью и стилем...',
        'category_id': 3,
        'is_available': True
    },
]

# Список категорий
categories_db = [
    {'id': 1, 'name': 'Классические'},
    {'id': 2, 'name': 'Спортивные'},
    {'id': 3, 'name': 'Дайверские'},
]

def index(request):
    context = {
        'headline': 'АРХЕТИП',
        'description': 'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году, они появились в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...',
        'cta': 'Доступно сейчас',
        'image_url': 'images/Urban.webp',
        'title': 'Главная страница',
        'watches': watches_db,  # Передаем список часов
        'categories': categories_db,  # Передаем список категорий
        'cat_selected': 0,
    }
    return render(request, 'index.html', context)

def show_category(request, cat_id):
    watches = [watch for watch in watches_db if watch['category_id'] == cat_id or cat_id == 0]
    context = {
        'headline': 'АРХЕТИП',
        'description': 'Эти часы Urban Jürgensen Reference 2 из желтого золота оснащены немецкими колесами дня и месяца. Созданные в 1989 году, они появились в первые годы после возрождения бренда Питером Баумбергером и Дереком Праттом...',
        'cta': 'Доступно сейчас',
        'image_url': 'images/123.jpg',
        'title': 'Категория часов',
        'watches': watches,
        'categories': categories_db,
        'cat_selected': cat_id,
    }
    return render(request, 'index.html', context)

def show_watch(request, watch_id):
    watch = next((w for w in watches_db if w['id'] == watch_id), None)
    context = {
        'title': watch['title'] if watch else 'Часы не найдены',
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
