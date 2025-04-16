from django import template
from django.db.models import Count
from WebApp.models import Category, Tag

register = template.Library()

@register.inclusion_tag('list_categories.html')
def show_categories(cat_selected=0):
    cats = Category.objects.all()
    return {'cats': cats, 'cat_selected': cat_selected}

@register.inclusion_tag('list_tags.html')
def show_tags():
    tags = Tag.objects.annotate(total=Count('watches')).filter(total__gt=0)
    return {'tags': tags}
