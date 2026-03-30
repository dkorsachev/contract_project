from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Возвращает значение из словаря по ключу"""
    if dictionary is None:
        return ''
    return dictionary.get(key, '')

@register.filter
def mul(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Делит значение на аргумент"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0