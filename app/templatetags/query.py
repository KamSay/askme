from django import template
from urllib.parse import urlencode
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def make_addr_add(context, name, value):
    params = context['request'].GET.copy()
    params['page'] = 1
    values = params.getlist(name)
    if value not in values:
        values.append(value)

    if values:
        params.setlist(name, values)
        return f'{reverse('app:tag')}?{urlencode(dict(params), doseq=True)}'
    else:
        return reverse('app:index')


@register.simple_tag(takes_context=True)
def make_addr_close(context, name, value):
    params = context['request'].GET.copy()
    params['page'] = 1
    values = params.getlist(name)
    if value in values:
        values.remove(value)

    if values:
        params.setlist(name, values)
        return f'{reverse('app:tag')}?{urlencode(dict(params), doseq=True)}'
    else:
        return reverse('app:index')