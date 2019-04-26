from django.template.defaulttags import register
from django.utils.safestring import mark_safe


@register.simple_tag(takes_context=True)
def url_query_replace(context, **kwargs):
    query = context['request'].GET.copy()

    for kwarg in kwargs:
        try:
            query.pop(kwarg)
        except KeyError:
            pass

    query.update(kwargs)

    return mark_safe(query.urlencode())
