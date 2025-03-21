from django import template
from WebApp.views import categories_db

register = template.Library()

@register.inclusion_tag('list_categories.html')
def show_categories(cat_selected=0):
    cats = categories_db
    return {'cats': cats, 'cat_selected': cat_selected}