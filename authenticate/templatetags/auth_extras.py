from django import template

register = template.Library()

@register.inclusion_tag('templatetags/render_field.html')
def render_field(field, style='default'):
    return {'field': field, 'style': style}

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})
