from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        # Возвращаем значение по умолчанию, если словарь отсутствует
        return None
    return dictionary.get(key, None)
