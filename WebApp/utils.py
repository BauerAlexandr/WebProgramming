from .models import Category

menu = [
    {'title': 'О сайте', 'url_name': 'stats'}, 
    {'title': 'Добавить часы', 'url_name': 'add_watch'},
    {'title': 'Категории', 'url_name': 'category_list'},
    {'title': 'Главная', 'url_name': 'home'},
]

class DataMixin:
    title_page = None
    paginate_by = 3  # Пагинация по умолчанию

    def get_mixin_context(self, context, **kwargs):
        context['menu'] = menu
        context['categories'] = Category.objects.all()
        if self.title_page:
            context['title'] = self.title_page
        context.update(kwargs)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)