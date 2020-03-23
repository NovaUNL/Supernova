from django import template

register = template.Library()


@register.filter('class_name')
def class_name(value):
    return value.__class__.__name__
