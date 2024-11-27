from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        # Возвращаем значение по умолчанию, если словарь отсутствует
        return None
    return dictionary.get(key, None)


@register.filter
def toggle_sort(current_order, column_name):
    """
    Определяет направление сортировки для конкретного столбца.
    Если текущий столбец уже сортируется, переключает порядок.
    """
    if not current_order:  # Если сортировка не задана, начинаем с "asc"
        return 'asc'
    current_order_by, current_order_direction = current_order.split(':')
    if current_order_by == column_name:
        # Переключаем направление сортировки
        return 'desc' if current_order_direction == 'asc' else 'asc'
    return 'asc'  # Если это новый столбец, начинаем с "asc"
