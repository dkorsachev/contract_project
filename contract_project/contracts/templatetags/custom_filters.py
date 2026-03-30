from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Возвращает значение из словаря по ключу"""
    if dictionary is None:
        return ''
    return dictionary.get(key, '')