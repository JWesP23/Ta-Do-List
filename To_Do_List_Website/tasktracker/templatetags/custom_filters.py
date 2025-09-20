from django import template

register = template.Library()

#Return the value for a given key from a dictionary
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])