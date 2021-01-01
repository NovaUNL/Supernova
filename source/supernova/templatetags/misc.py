from django import template

register = template.Library()


@register.filter('class_name')
def class_name(value):
    return value.__class__.__name__


@register.filter('dict_key')
def dict_key(d, k):
    """ Returns the given key from a dictionary. """
    return d[k]
