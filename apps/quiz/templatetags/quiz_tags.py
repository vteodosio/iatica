from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary by key and returns its text."""
    item = dictionary.get(key)
    if item:
        return item.texto
    return '—'
