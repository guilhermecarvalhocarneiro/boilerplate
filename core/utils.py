import re

from django.apps import apps
from django.db.models import Q

from nuvols.core.excecoes import CpfCnpjValidationError

# Validators
EMPTY_VALUES = (None, '', [], (), {})


def obter_modelo(nome_modelo):
    if not nome_modelo:
        return None
    try:
        return next(
            (m for m in apps.get_models() if m._meta.model_name.lower() == nome_modelo.lower()),
            None)
    except LookupError:
        return None


def registro_existente(objeto, campo):
    campo_str = '{0}__iexact'.format(campo)
    filtro = Q(**{campo_str: getattr(objeto, campo)})
    if objeto.id:
        return objeto._meta.model.objects.exclude(id=objeto.id).filter(filtro).exists()
    else:
        return objeto._meta.model.objects.filter(filtro).exists()


def is_valid_email(value):
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013'
        r"""\014\016-\177])*"$)""", re.IGNORECASE)
    domain_regex = re.compile(
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|'
        r'[A-Z0-9-]{2,})$|^\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|'
        r'2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)
    domain_whitelist = ['localhost']

    if not value or '@' not in value:
        raise CpfCnpjValidationError(u'Email inválido')

    user_part, domain_part = value.rsplit('@', 1)

    if not user_regex.match(user_part):
        raise CpfCnpjValidationError(u'Email inválido')

    if (domain_part not in domain_whitelist and
            not domain_regex.match(domain_part)):
        # Try for possible IDN domain-part
        try:
            domain_part = domain_part.encode('idna').decode('ascii')
            if not domain_regex.match(domain_part):
                raise CpfCnpjValidationError(u'Email inválido')
            else:
                return value
        except UnicodeError:
            pass
        raise CpfCnpjValidationError(u'Email inválido')
    return value


def DV_maker(v):
    if v >= 2:
        return 11 - v
    return 0


def is_valid_cpf(value):
    error_messages = {
        'invalid': u"CPF Inválido",
        'max_digits': (u"CPF possui 11 dígitos (somente números) ou 14"
                       u" (com pontos e hífen)"),
        'digits_only': (u"Digite um CPF com apenas números ou com ponto e "
                        u"hífen"),
    }

    if value in EMPTY_VALUES:
        return u''
    orig_value = value[:]
    if not value.isdigit():
        value = re.sub("[-\.]", "", value)
    try:
        int(value)
    except ValueError:
        raise CpfCnpjValidationError(error_messages['digits_only'])
    if len(value) != 11:
        raise CpfCnpjValidationError(error_messages['max_digits'])
    orig_dv = value[-2:]

    new_1dv = sum([i * int(value[idx]) for idx, i in enumerate(range(10, 1, -
    1))])
    new_1dv = DV_maker(new_1dv % 11)
    value = value[:-2] + str(new_1dv) + value[-1]
    new_2dv = sum([i * int(value[idx]) for idx, i in enumerate(range(11, 1, -
    1))])
    new_2dv = DV_maker(new_2dv % 11)
    value = value[:-1] + str(new_2dv)
    if value[-2:] != orig_dv:
        raise CpfCnpjValidationError(error_messages['invalid'])

    return orig_value
