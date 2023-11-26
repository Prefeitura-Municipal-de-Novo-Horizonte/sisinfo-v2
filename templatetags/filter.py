from django import template

register = template.Library()

@register.filter(name='is_par')
def is_par(valor):
    return valor % 2 == 0