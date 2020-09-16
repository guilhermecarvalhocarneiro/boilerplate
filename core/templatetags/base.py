
from django import template
import pprint

register = template.Library()

@register.simple_tag(takes_context=True)
def get_ip(context):
    """Template tag to get user IP"""
    request = context['request']
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# pegar um atributo de um dicionario
# motivo: No template não acessa var que começa com _
@register.filter(name='get')
def get(d, k):
    return d.get(k, None)

# Retorna os fields manytomany
@register.filter(name='get_many_to_many')
def get_many_to_many(obj, object_list):
    manytomany_name = []
    manytomany = []
    for field in obj._meta.many_to_many:
        manytomany_name.append(field._m2m_reverse_name_cache)

    for item in object_list:
        try:
            if item[1].target_field_name in manytomany_name:
                manytomany.append(item[1])
        except Exception:
            pass

    return manytomany

@register.filter()
def has_add_permission(model=None, request=None):
    """
    Verifica se o usuario tem a permissão de adicionar, no model passado
    ex: {if model|has_add_permission:request %}
    """
    if model and hasattr(model, 'has_add_permission') and request:
        return model.has_add_permission(request=request)
    else:
        return False


@register.filter()
def has_change_permission(model=None, request=None):
    """
    Verifica se o usuario tem a permissão de alterar, no model passado
    ex: {if model|has_change_permission:request %}
    """
    if model and hasattr(model, 'has_change_permission') and request:
        return model.has_change_permission(request=request)
    else:
        return False


@register.filter()
def has_delete_permission(model=None, request=None):
    """
    Verifica se o usuario tem a permissão de deletar, no model passado
    ex: {if model|has_delete_permission:request %}
    """
    if model and hasattr(model, 'has_delete_permission') and request:
        return model.has_delete_permission(request=request)
    else:
        return False
