"""Views padrões para serem herdadas pelas apps que desejarem utilizar
as customizações implementadas.
"""
import logging
import secrets
import string
from datetime import date, datetime
from locale import normalize

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import User
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView)
from django.core.exceptions import (FieldDoesNotExist, FieldError,
                                    ValidationError)
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor, ManyToManyDescriptor
from django.core.mail import EmailMessage
from django.db.models import (AutoField, ForeignKey, ManyToManyField,
                              ManyToManyRel, ManyToOneRel, Q)
from django.db.models.fields import AutoField
from django.db.models.fields import BooleanField as BooleanFieldModel
from django.db.models.query_utils import DeferredAttribute
from django.forms.fields import BooleanField
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.base import resolve
from django.utils.text import camel_case_to_spaces, slugify
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, UpdateView)

from .forms import BaseForm
from .models import Base
from .settings import SYSTEM_NAME

# Configurando o logger
logger = logging.getLogger(__name__)


def has_fk_attr(classe=None, attr=None):
    try:
        classe.objects.values(attr)
    except Exception as e:
        return False
    return True


def get_breadcrumbs(url_str):
    """
    Método para criar o Breadcrumbs a ser utilizado nos templastes
    Arguments:
        url_str {String} -- [Nome da app e do Models]
    Returns:
        [Lista] -- [Lista com o breadcrumb]
    """

    breadcrumbs = []
    breadcrumbs.append({'slug': "Inicio", 'url': "/", })
    url = '/'
    array_url = url_str.strip('/').split('/')
    cont = 1
    for slug in array_url:
        breadcrumb = {}
        if slug != '':
            breadcrumb['slug'] = camel_case_to_spaces(slug).title()
            if cont < len(array_url):
                url = '%s%s/' % (url, slug.lower())
                breadcrumb['url'] = url
            breadcrumbs.append(breadcrumb)
        cont += 1
    return breadcrumbs


def get_apps(self):
    """Método para recuperar todas as apps

    Returns:
        List -- Lista com as apps que o usuário tem acesso
    """

    from django.apps import apps
    _apps = []
    for app in apps.get_app_configs():
        try:
            if (app.name.lower().__contains__('django') or
                    app.name.lower().__contains__('rest_framework') or
                    app.name.lower().__contains__('core') or
                    app.name.lower().__contains__('ckeditor') or
                    app.name.lower().__contains__('corsheaders')):
                continue
            _models = []
            for model in app.get_models():
                _models.append({'name_model': model._meta.verbose_name,
                                'url_list_model': '/{app}/{model}/'.format(
                                    app=model._meta.app_label,
                                    model=model._meta.model_name),
                                'path_url': '{app}:{model}-list'.format(
                                    app=model._meta.app_label.lower(),
                                    model=model._meta.model_name.lower()
                                ),
                                'real_name_model': model._meta.model_name
                                })
            _apps.append({'name_app': '%s' % app.verbose_name,
                          'models_app': _models,
                          'index_url_app': '{}:{}-index'.format(model._meta.app_label,
                                                                model._meta.app_label),
                          'real_name_app': app.name,
                          'real_name_model': model._meta.model_name})
        except Exception as error:
            print(error)
            continue
    return _apps


class BaseTemplateView(TemplateView):
    """
    Classe base que deve ser herdada caso o desenvolvedor queira reaproveitar
    as funcionalidades já desenvolvidas TemplateView

    Na classe que herdar dessa deve ser atribuido o valor template_name com o caminho até o template HTML a ser renderizado

    Raises:
        ValidationError -- Caso não seja atribuido o valor da variavel template_name ocorrerá uma excessão
    """

    def __init__(self):
        if self.template_name is None:
            raise ValidationError(
                message='Deve ser definido o caminho do template \
                         na variavel "template_name" em sua Views!')
        super(BaseTemplateView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(BaseTemplateView, self).get_context_data(**kwargs)
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        context['system_name'] = SYSTEM_NAME
        context['apps'] = get_apps(self)
        return context


class IndexTemplate(LoginRequiredMixin, PermissionRequiredMixin, BaseTemplateView):
    """[summary]

    Arguments:
        BaseTemplateView {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    template_name = "core/index.html"
    context_object_name = 'core'

    def has_permission(self):
        """
        Verifica se tem alguma das permissões retornadas pelo
        get_permission_required, caso tenha pelo menos uma ele
        retorna True
        """
        return not self.request.user is None and self.request.user.is_authenticated and self.request.user.is_active


class BaseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Classe base que deve ser herdada caso o desenvolvedor queira reaproveitar
    as funcionalidades já desenvolvidas ListView

    Na classe que herdar dessa deve ser atribuido o valor template_name com o caminho até o template HTML a ser renderizado

    Raises:
        ValidationError -- Caso não seja atribuido o valor da variavel template_name ocorrerá uma excessão
    """

    model = Base
    list_filter = []
    search_fields = []
    list_display = list_filter + search_fields
    query_params_q = ""
    url_pagination = ""
    query_params_filters = []
    paginate_by = 1000
    template_name_suffix = '_list'

    def __init__(self):
        if self.template_name is None:
            raise ValidationError(
                message='Deve ser definido o caminho do \
                         template na variavel "template_name" em sua Views!')
        super(BaseListView, self).__init__()

    def get_permission_required(self):
        """
            cria a lista de permissões que a view pode ter de acordo com cada model.
        """
        return ('{app}.add_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name),
                '{app}.delete_{model}'.format(
                    app=self.model._meta.app_label, model=self.model._meta.model_name),
                '{app}.change_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name))

    def has_permission(self):
        """
        Verifica se tem alguma das permissões retornadas pelo
        get_permission_required, caso tenha pelo menos uma ele
        retorna True
        """
        perms = self.get_permission_required()
        # o retorno usa a função any para retornar True caso tenha pelo menos uma das permissões na lista perms
        return any(self.request.user.has_perm(perm) for perm in perms)

    def get_queryset(self):
        queryset = super(BaseListView, self).get_queryset()

        if ((hasattr(self.model, '_meta') and hasattr(self.model._meta, 'ordering') and self.model._meta.ordering) or
                ((hasattr(self.model, 'Meta') and hasattr(self.model.Meta, 'ordering') and self.model.Meta.ordering))):
            queryset = queryset.order_by(
                *(self.model._meta.ordering or self.model.Meta.ordering))

        try:
            param_filter = self.request.GET.get('q')
            query_dict = self.request.GET
            query_params = Q()
            for field in self.search_fields:
                try:
                    queryset.filter(**{"%s__icontains" % field: param_filter})
                    query_params |= Q(**{"%s__icontains" %
                                         field: param_filter})
                    continue
                except Exception as e:
                    pass

                if hasattr(self.model, field) and field != '' and (field in ['pk', 'id'] or (field.split('__')[-1] in ['pk', 'id'])):
                    # se for um atributo de relacionamento então olha se é numero pois pk só aceita numero.
                    if not param_filter or (param_filter and param_filter.isnumeric()):
                        query_params |= Q(**{field: param_filter})
                # olha se é um atributo normal ou se é de relacionamento
                elif (hasattr(self.model, field) and type(getattr(self.model, field)) == DeferredAttribute):
                    query_params |= Q(**{'%s__icontains' %
                                         field: param_filter})
                # resolve a opção de buscar pelo name do model quando usa GenericForeignKey com o atributo content_type no modelo
                elif ('content_type' == field.split('__')[0] and hasattr(self.model, 'content_type') and
                      type(getattr(self.model, 'content_type')) == ForwardManyToOneDescriptor and
                      hasattr(ContentType, field.replace('content_type__', ''))):
                    param_filter_content_type = param_filter
                    try:
                        param_filter_content_type = param_filter_content_type.replace(
                            " ", '').lower()
                        param_filter_content_type = normalize('NFKD', param_filter_content_type).encode('ASCII',
                                                                                                        'ignore').decode(
                            'ASCII')
                    except Exception as erro_tipo:
                        logger.error('Erro: %s; No Metodo: %s' %
                                     (erro_tipo, 'BaseListView.get_queryset()'))
                        pass
                    query_params |= Q(**{'%s__icontains' %
                                         field: param_filter_content_type})

                elif ('content_object' == field.split('__')[0] and hasattr(self.model, 'content_object') and
                      type(getattr(self.model, 'content_object')) == GenericForeignKey):
                    try:
                        # lista de objetos genericos usados pelo model
                        list_object = queryset.values(
                            'content_type_id').distinct()
                        for obj in ContentType.objects.filter(id__in=list_object).all():
                            try:
                                # pega o campo do modelo a ser buscado
                                field_name = field.replace(
                                    'content_object__', '')
                                # pega os ids dos objetos filtrados
                                list_id_object = obj.model_class().objects.filter(
                                    **{field_name: param_filter}).values_list('id', flat=True)
                                if len(list_id_object) > 0:
                                    query_params |= Q(
                                        content_type_id=obj.id, object_id__in=list_id_object)
                            except Exception as erro_content:
                                logger.error('Erro: %s; No Metodo: %s' % (
                                    erro_content, 'BaseListView.get_queryset()'))
                                pass
                    except Exception as e:
                        logger.error('Erro: %s; No Metodo: %s' %
                                     (e, 'BaseListView.get_queryset()'))
                        pass
                else:
                    if hasattr(self.model, field) and type(getattr(self.model, field)) != ManyToManyDescriptor:
                        query_params |= Q(**{field: param_filter})

            if param_filter:
                queryset = queryset.filter(query_params)

            for chave, valor in query_dict.items():
                if valor is not None and valor != 'None' and valor != '':
                    if chave not in ['q', 'csrfmiddlewaretoken', 'page']:
                        not_exact = False
                        if "__not_exact" in chave:
                            not_exact = True
                            chave = "%s%s" % (chave.split("__")[0], "__exact")
                        try:
                            campo_date = DateTimeField().clean(valor)
                            if not_exact:
                                queryset = queryset.exclude(
                                    **{chave: campo_date})
                            else:
                                queryset = queryset.filter(
                                    **{chave: campo_date})
                            continue
                        except Exception as e_date:
                            logger.error('Erro: %s; No Metodo: %s' %
                                         (e_date, 'BaseListView.get_queryset()'))
                            pass
                        queryset = queryset.filter(**{chave: valor})
            return queryset
        except FieldError as fe:
            if field:
                # COLOQUE O extra_tags='danger' PARA CASO DE ERROS, POIS O DJANGO MANDA O NOME erro E NÃO danger QUE É PADRÃO DO BOOTSTRAP
                messages.error(self.request, "Erro com o campo '%s'!" %
                               field, extra_tags='danger')
                logger.error('Erro: %s; No Metodo: %s' %
                             (fe, 'BaseListView.get_queryset()'))
            return queryset.none()
        except Exception as e:
            print(e)
            messages.error(
                self.request, "Erro ao tentar filtrar!", extra_tags='danger')
            logger.error('Erro: %s; No Metodo: %s' %
                         (e, 'BaseListView.get_queryset()'))
            return queryset.none()

    def list_display_verbose_name(self):
        list_display_verbose_name = []
        for name in self.get_list_display():
            try:
                if name == '__str__':
                    if hasattr(self.model, name) and hasattr(self.model._meta, 'verbose_name'):
                        list_display_verbose_name.append(
                            getattr(self.model._meta, 'verbose_name'))
                elif '__' in name and name != '__str__' and has_fk_attr(self.model, name):
                    list_name = name.split('__')
                    list_name.reverse()
                    list_display_verbose_name.append(
                        ' '.join(list_name).title())
                elif name != 'pk' and name != 'id':
                    # verifica se existe auguma função feita na view e usada no display
                    # verifica se é do tipo allow_tags
                    # e verifica se tem o short_description para usa-lo no cabeçario da tabela do list
                    if hasattr(self, name) and hasattr(getattr(self, name), 'allow_tags') \
                            and getattr(self, name).allow_tags and \
                            hasattr(getattr(self, name), 'short_description'):
                        list_display_verbose_name.append(
                            getattr(self, name).short_description)
                    elif hasattr(self.model, name):
                        field = self.model._meta.get_field(name)
                        if hasattr(field, 'verbose_name'):
                            verbose_name = field.verbose_name.title()
                            list_display_verbose_name.append(verbose_name)
                        else:
                            list_display_verbose_name.append(name)
                    else:
                        list_display_verbose_name.append(name)
                else:
                    list_display_verbose_name.append(name)
            except FieldDoesNotExist as e:
                raise FieldDoesNotExist("%s não tem nenhum campo chamado '%s'" % (
                    self.model._meta.model_name, name))
        return list_display_verbose_name

    def list_display_plural_verbose_name(self):
        list_display_plural_verbose_name = []
        for name in self.get_list_display():
            try:
                field = self.model._meta.get_field(name)
                if name == '__str__':
                    if hasattr(self.model, name) and hasattr(self.model._meta, 'verbose_name_plural'):
                        list_display_plural_verbose_name.append(
                            getattr(self.model._meta, 'verbose_name_plural'))
                elif '__' in name and name != '__str__' and has_fk_attr(self.model, name):
                    list_name = name.split('__')
                    list_name.reverse()
                    list_display_plural_verbose_name.append(
                        ' '.join(list_name).title())
                elif name != 'pk' and name != 'id':
                    # verifica se existe auguma função feita na view e usada no display
                    # verifica se é do tipo allow_tags
                    # e verifica se tem o short_description para usa-lo no cabeçario da tabela do list
                    if hasattr(self, name) and hasattr(getattr(self, name), 'allow_tags') \
                            and getattr(self, name).allow_tags and \
                            hasattr(getattr(self, name), 'short_description'):
                        list_display_plural_verbose_name.append(
                            getattr(self, name).short_description)
                    elif hasattr(self.model, name):
                        field = self.model._meta.get_field(name)
                        if hasattr(field, 'verbose_name_plural'):
                            verbose_name = self.model._meta.get_field(
                                name).verbose_name_plural.title()
                            list_display_plural_verbose_name.append(
                                verbose_name)
                        else:
                            list_display_plural_verbose_name.append(name)
                else:
                    list_display_plural_verbose_name.append(name)
            except FieldDoesNotExist as e:
                raise FieldDoesNotExist("%s não tem nenhum campo chamado '%s'" % (
                    self.model._meta.model_name, name))
        return list_display_plural_verbose_name

    def get_list_display(self):
        list_display = []
        # define os campos padrões
        if not self.list_display:
            self.list_display = ['pk', '__str__']
        # define os campos padrões
        if self.list_display and 'pk' in self.list_display and len(self.list_display) <= 1 and hasattr(self.model,
                                                                                                       '__str__'):
            self.list_display += ['__str__']

        # ordena para que o id sempre venha primeiro ou em segundo caso tenha o pk
        if 'id' in self.list_display:
            self.list_display.remove('id')
            self.list_display = ['id'] + self.list_display
        # ordena para que o pk sempre venha primeiro
        if 'pk' in self.list_display:
            self.list_display.remove('pk')
            self.list_display = ['pk'] + self.list_display
        else:
            self.list_display = ['pk'] + self.list_display

        # faz a checagem dos campos
        for name in self.list_display:
            # verifica casos onde pega campos dos filhos ex: pai__name
            if '__' in name and name != '__str__' and not has_fk_attr(self.model, name):
                messages.error(self.request, "%s ou a View não tem nenhum campo chamado '%s'" % (
                    self.model._meta.model_name, name),
                               extra_tags='danger')
            elif not '__' in name and not hasattr(self.model, name) and not hasattr(self, name):
                messages.error(self.request,
                               "%s ou a View não tem nenhum campo chamado '%s'" % (
                                   self.model._meta.model_name, name),
                               extra_tags='danger')
                continue
            elif not '__' in name and not hasattr(self.model, name) and hasattr(self, name) and (
                    not hasattr(getattr(self, name), 'allow_tags') or
                    (hasattr(getattr(self, name), 'allow_tags') and not getattr(self, name).allow_tags)):
                messages.error(self.request,
                               "%s não tem nenhum campo chamado '%s'" % (
                                   self.model._meta.model_name, name),
                               extra_tags='danger')
                continue

            if not name in list_display:
                list_display.append(name)
        return list_display

    def get_context_data(self, **kwargs):
        try:
            # se colocar o do super da erro de paginação
            # context = super().get_context_data(**kwargs)
            context = super(BaseListView, self).get_context_data(**kwargs)
            context['user_ip'] = self.request.META.get(
                'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
            context['display'] = self.list_display_verbose_name()

            # processa os parametros para retorna-los ao template
            query_params = dict(self.request.GET)
            if query_params:
                # retira o parametro page e add ele em outra variavel, apensas dele
                if query_params.get('page'):
                    query_params.pop('page')
                # retira o csrf token caso exista
                if query_params.get('csrfmiddlewaretoken'):
                    query_params.pop('csrfmiddlewaretoken')
                # cria a url para add ao link de paginação para não perder os filtros
                url_pagination = ''
                for key, value in query_params.items():
                    url_pagination += "{}={}&".format(key,
                                                      value[0].replace(" ", "+"))
                # add a url dos filtros e da pesquisa no context
                context['url_pagination'] = url_pagination
                # retira o parametro do campo de pesquisa e add ele em outra variavel no context apensas dele
                if query_params.get('q'):
                    context['query_params_q'] = query_params.pop('q')[0]
                # O apos todas as verificações sobram os filtros que são add em outra variavel no context apenas dele.
                context['query_params_filters'] = query_params

            # manipulo a lista para tratar de forma diferente
            list_item = []
            for obj in context['object_list']:

                field_dict = {}

                obj._meta.get_fields(include_parents=True)

                # percorre os atributos setados no list_display
                for field_display in self.get_list_display():
                    try:
                        if '__' in field_display and field_display != '__str__' and has_fk_attr(obj.__class__,
                                                                                                field_display):
                            lista_fk = context['object_list'].values(
                                'id', field_display)
                            for item_fk in lista_fk:
                                if item_fk['id'] == obj.id:
                                    field_dict[field_display] = "{}".format(
                                        item_fk[field_display])
                        elif hasattr(obj, field_display) and field_display != '__str__':
                            # verifica se o campo não é None se sim entra no if
                            if obj.__getattribute__(field_display) is not None:
                                # Verificando se o campo possui o metodo do CHOICE
                                str_metodo_choice = 'get_{nome}_display'.format(
                                    nome=field_display)
                                if hasattr(obj, str_metodo_choice):
                                    field_dict[field_display] = "{}".format(
                                        getattr(obj, str_metodo_choice)().__str__())
                                else:
                                    if type(getattr(obj, field_display)) == datetime:
                                        campo_date_time = getattr(
                                            obj, field_display)
                                        tz = pytz.timezone(settings.TIME_ZONE)
                                        date_tz = tz.normalize(campo_date_time)
                                        field_dict[field_display] = "{}".format(
                                            date_tz.strftime(settings.DATETIME_INPUT_FORMATS[0] or
                                                             "%d/%m/%Y %H:%M"))
                                    elif type(getattr(obj, field_display)) == date:
                                        field_dict[field_display] = "{}".format(
                                            getattr(obj, field_display).strftime(settings.DATE_INPUT_FORMATS[0] or
                                                                                 "%d/%m/%Y"))
                                    #     verifica se é um ManyToMany
                                    elif hasattr(getattr(obj, field_display), 'all'):
                                        list_many = []
                                        # pega uma string feita com o str de cada objeto da lista
                                        for sub_obj in getattr(obj, field_display).all():
                                            list_many.append(
                                                '{}'.format(sub_obj))
                                        field_dict[field_display] = ', '.join(
                                            list_many)
                                    else:
                                        field_dict[field_display] = "{}".format(
                                            getattr(obj, field_display).__str__())
                            else:
                                # no caso de campos None ele coloca para aparecer vasio
                                field_dict[field_display] = ""
                        elif field_display == '__str__':
                            field_dict[field_display] = "{}".format(
                                getattr(obj, field_display)())

                        elif hasattr(self, field_display) and self.__getattribute__(
                                field_display) and field_display != '__str__':
                            # elif verifica se existe auguma função feita na view e usada no display
                            # elif verifica se é do tipo allow_tags
                            # elif então usa o retorno da função para aparecer na lista
                            field_dict[field_display] = getattr(
                                self, field_display)(obj)
                    except Exception as e:
                        logger.error(e)
                        messages.error(self.request, "Erro com o campo '%s' no model '%s'!" % (field_display, str(obj)),
                                       extra_tags='danger')
                        continue
                list_item.append(field_dict)

            # reinciro a lista modificada para aproveitar a variavel page_list e retornar apenas um objeto, no template eu separo de novo
            context['object_list'] = list_item
            context['system_name'] = SYSTEM_NAME

            object_filters = []
            # Refatorar para não precisar pecorrer os itens duas vezes
            for field in self.model._meta.fields:
                if field.name in self.list_filter:
                    # o label do choices.
                    filter = {}
                    # variavel para ficar no label do campo
                    label_name = ' '.join(str(field.name).split('_')).title()
                    if hasattr(field, 'verbose_name') and field.verbose_name:
                        label_name = field.verbose_name
                    # Verificando se o campo e relacionamento
                    if isinstance(field, ForeignKey):
                        filter[field.name] = {'label': label_name, 'list': field.related_model.objects.distinct(),
                                              'type_filter': 'ForeignKey'}
                    # Verificando se o campo eh booleano
                    elif isinstance(field, BooleanFieldModel):
                        filter[field.name] = {'label': label_name, 'list': ['True', 'False'],
                                              'type_filter': 'BooleanFieldModel'}
                    elif isinstance(field, DateField) or isinstance(field, DateTimeField):
                        # cria um choice list com  os operadores que poderá usar
                        choice_date_list = []
                        choice_date_list.append(
                            {'choice_id': '__exact', 'choice_label': 'Igual'})
                        choice_date_list.append(
                            {'choice_id': '__not_exact', 'choice_label': 'Diferente'})
                        choice_date_list.append(
                            {'choice_id': '__lt', 'choice_label': 'Menor que'})
                        choice_date_list.append(
                            {'choice_id': '__gt', 'choice_label': 'Maior que'})
                        choice_date_list.append(
                            {'choice_id': '__lte', 'choice_label': 'Menor Igual a'})
                        choice_date_list.append(
                            {'choice_id': '__gte', 'choice_label': 'Maior Igual a'})

                        filter[field.name] = {'label': label_name, 'list': choice_date_list,
                                              'type_filter': str(type(field))[:-2].split('.')[-1]}
                    else:
                        # Verificando se o campo possui o atributo CHOICE
                        if hasattr(field, 'choices') and len(getattr(field, 'choices')) > 0 \
                                and hasattr(field, 'flatchoices') and len(getattr(field, 'flatchoices')) > 0:
                            choice_list = []
                            for choice in getattr(field, 'flatchoices'):
                                item = {
                                    'choice_id': choice[0], 'choice_label': choice[1]}
                                choice_list.append(item)
                            filter[field.name] = {'label': label_name, 'list': choice_list,
                                                  'type_filter': 'ChoiceField'}
                        else:
                            # ele ja faz o distinct e ordena de acordo com o nome do campo
                            # add um dicionario com o nome do label, lista do filtro e o tipo de campo
                            filter[field.name] = {'label': label_name, 'list': self.get_queryset().
                                values_list(field.name, flat=True).order_by(
                                field.attname).distinct(field.attname),
                                                  'type_filter': str(type(field))[:-2].split('.')[-1]}
                    object_filters.append(filter)

            context['filters'] = object_filters

            context['url_create'] = '{app}:{model}-create'.format(app=self.model._meta.app_label,
                                                                  model=self.model._meta.model_name)
            context['url_update'] = '{app}:{model}-update'.format(app=self.model._meta.app_label,
                                                                  model=self.model._meta.model_name)
            context['url_detail'] = '{app}:{model}-detail'.format(app=self.model._meta.app_label,
                                                                  model=self.model._meta.model_name)
            context['url_delete'] = '{app}:{model}-delete'.format(app=self.model._meta.app_label,
                                                                  model=self.model._meta.model_name)
            context['url_list'] = '{app}:{model}-list'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)

            url_str = reverse(context['url_list']) + ' Listar'

            context['breadcrumbs'] = get_breadcrumbs(url_str)

            context['model_name'] = '%s' % (
                    self.model._meta.verbose_name_plural or self.model._meta.object_name).title()
            context['apps'] = get_apps(self)

            context['has_add_permission'] = self.model(
            ).has_add_permission(self.request)
            context['has_change_permission'] = self.model(
            ).has_change_permission(self.request)
            context['has_delete_permission'] = self.model(
            ).has_delete_permission(self.request)

            return context

        except Exception as error:
            pass
        except Exception as e:
            pass


class BaseDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Classe base que deve ser herdada caso o desenvolvedor queira reaproveitar
    as funcionalidades já desenvolvidas para DetailView
    Na classe que herdar dessa deve ser atribuido o valor template_name com o caminho até o template HTML a ser renderizado

    Raises:
        ValidationError -- Caso não seja atribuido o valor da variavel template_name ocorrerá uma excessão
    """

    model = Base
    exclude = []
    template_name_suffix = '_detail'

    def get_template_names(self):
        if self.template_name:
            return [self.template_name, ]
        return ['outside_template/base_detail.html', ]

    def get_permission_required(self):
        """
            cria a lista de permissões que a view pode ter de acordo com cada model.
        """
        return ('{app}.add_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name),
                '{app}.delete_{model}'.format(
                    app=self.model._meta.app_label, model=self.model._meta.model_name),
                '{app}.change_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name))

    def has_permission(self):
        """
        Verifica se tem alguma das permissões retornadas pelo
        get_permission_required, caso tenha pelo menos uma ele
        retorna True
        """
        perms = self.get_permission_required()
        # o retorno usa a função any para retornar True caso tenha pelo menos uma das permissões na lista perms
        return any(self.request.user.has_perm(perm) for perm in perms)

    def get_context_data(self, **kwargs):
        context = super(BaseDetailView, self).get_context_data(**kwargs)
        object_list, many_fields = self.object.get_all_related_fields()
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        context['object_list'] = object_list
        context['many_fields'] = many_fields
        context['system_name'] = SYSTEM_NAME
        context['url_create'] = '{app}:{model}-create'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_update'] = '{app}:{model}-update'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_detail'] = '{app}:{model}-detail'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_delete'] = '{app}:{model}-delete'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_list'] = '{app}:{model}-list'.format(app=self.model._meta.app_label,
                                                          model=self.model._meta.model_name)

        url_str = reverse(context['url_list']) + \
                  ' Detalhe {}'.format(context['object'].pk)

        context['breadcrumbs'] = get_breadcrumbs(url_str)

        context['model_name'] = '%s' % (
                self.model._meta.verbose_name or self.model._meta.object_name or '').title()
        context['apps'] = get_apps(self)

        context['has_add_permission'] = self.model(
        ).has_add_permission(self.request)
        context['has_change_permission'] = self.model(
        ).has_change_permission(self.request)
        context['has_delete_permission'] = self.model(
        ).has_delete_permission(self.request)

        return context


class BaseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Classe base que deve ser herdada caso o desenvolvedor queira reaproveitar
    as funcionalidades já desenvolvidas para UpdateView
    Na classe que herdar dessa deve ser atribuido o valor template_name com o caminho até o template HTML a ser renderizado

    Raises:
        ValidationError -- Caso não seja atribuido o valor da variavel template_name ocorrerá uma excessão
    """

    model = Base
    form_class = BaseForm
    template_name_suffix = '_update'
    inlines = []

    def __init__(self):
        super(BaseUpdateView, self).__init__()

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        return ['outside_template/base_update.html']

    def get_success_url(self):
        if self.success_url and self.success_url != '':
            return self.success_url
        else:
            url = reverse('{app}:{model}-detail'.format(
                app=self.model._meta.app_label,
                model=self.model._meta.model_name), kwargs={"pk": self.object.pk}
            )
            return url

    def get_permission_required(self):
        """
            cria a lista de permissões que a view pode ter de acordo com cada model.
        """
        return ('{app}.change_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name),)

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateView, self).get_context_data(**kwargs)
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        context['list_inlines'] = self.get_formset_inlines()
        context['system_name'] = SYSTEM_NAME

        context['url_create'] = '{app}:{model}-create'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_update'] = '{app}:{model}-update'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_detail'] = '{app}:{model}-detail'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_delete'] = '{app}:{model}-delete'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_list'] = '{app}:{model}-list'.format(app=self.model._meta.app_label,
                                                          model=self.model._meta.model_name)

        url_str = reverse(context['url_list']) + \
                  ' Atualizar {}'.format(context['object'].pk)

        context['breadcrumbs'] = get_breadcrumbs(url_str)

        context['model_name'] = '%s' % (
                self.model._meta.verbose_name_plural or self.model._meta.object_name or '').title()
        context['apps'] = get_apps(self)

        context['has_add_permission'] = self.model(
        ).has_add_permission(self.request)
        context['has_change_permission'] = self.model(
        ).has_change_permission(self.request)
        context['has_delete_permission'] = self.model(
        ).has_delete_permission(self.request)

        return context

    def get_formset_inlines(self):
        """Metodo utilizado para instanciar os inlines.
        Returns:
            List -- Lista com os formulários inline do form principal
        """
        formset_inlines = []
        if hasattr(self, 'inlines') and self.inlines:
            for item in self.inlines:
                if item.model().has_change_permission(self.request):
                    if self.request.POST:
                        formset = item(self.request.POST, self.request.FILES, instance=self.object,
                                       prefix=item.model._meta.model_name)
                    else:
                        formset = item(instance=self.object,
                                       prefix=item.model._meta.model_name)
                    lista_instance_inline = formset.queryset.all() or []
                    # só seta True caso os valores definidos na permissão do usuario e o can_delete do inlineformset_factory seja True
                    formset.can_delete = item.model().has_delete_permission(
                        self.request) and item.can_delete
                    if not formset.can_delete:
                        # se não tem permisão de excluir, então seta o valor minimo para 0
                        formset.min_num = 0
                    if not item.model().has_add_permission(self.request):
                        # se não tem permisão de adcionar, então seta o valor minimo para 0
                        formset.max_num = 0
                    if hasattr(formset, 'prefix') and formset.prefix:
                        # pode ser colocado o user aqui para utilizar na validação do forms
                        formset.form.user = self.request.user
                        formset_inlines.append(formset)
        return formset_inlines

    def get_form_kwargs(self):
        """Método utilizado para adicionar o request

        Returns:
            Kwargs
        """
        kwargs = super(BaseUpdateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Método para verificar se o formulário submetido está válido

        Arguments:
            form {Form} -- Formulário com os valores enviado para processamento

        Returns:
            Url -- O retorno é o redirecionamento para a URL de sucesso configurada na Views da app
        """

        formset_inlines = self.get_formset_inlines()
        if form.is_valid():
            for form_formset in formset_inlines:
                if not form_formset.is_valid():
                    return self.render_to_response(
                        context=self.get_context_data(form=form, named_formsets=formset_inlines))

            self.object = form.save()

            # for every formset, attempt to find a specific formset save function
            # otherwise, just save.
            for formset in formset_inlines:
                formset.instance = self.object
                formset.save()
            messages.success(request=self.request, message="'{}', Alterado com Sucesso!".format(self.object),
                             extra_tags='success')
        else:
            messages.error(
                request=self.request, message="Ocorreu um erro, verifique os campos!", extra_tags='danger')
            return form.errors
        # salva e add outro novo_continue
        if '_addanother' in form.data:
            return redirect(reverse(self.get_context_data()['url_create']))
        # salva e continua editando
        elif '_continue' in form.data:
            return redirect(reverse(self.get_context_data()['url_update'], kwargs={'pk': self.object.pk}))
        # salva e redireciona pra lista
        else:
            return redirect(self.get_success_url())


class BaseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Classe base que deve ser herdada caso o desenvolvedor queira reaproveitar
    as funcionalidades já desenvolvidas para CreateView
    Na classe que herdar dessa deve ser atribuido o valor template_name com o
    caminho até o template HTML a ser renderizado

    Raises:
        ValidationError -- Caso não seja atribuido o valor da variavel template_name ocorrerá uma excessão
    """

    model = Base
    template_name_suffix = '_create'
    form_class = BaseForm
    inlines = []

    def __init__(self):
        super(BaseCreateView, self).__init__()

    def get_template_names(self):
        if self.template_name:
            return [self.template_name, ]
        return ['outside_template/base_create.html', ]

    def get_success_url(self):
        if self.success_url and self.success_url != '':
            return reverse(self.success_url)
        else:
            url = reverse('{app}:{model}-detail'.format(
                app=self.model._meta.app_label,
                model=self.model._meta.model_name), kwargs={"pk": self.object.pk}
            )
            return url

    def get_permission_required(self):
        """
            cria a lista de permissões que a view pode ter de acordo com cada model.
        """
        return ('{app}.add_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name),)

    def get_context_data(self, **kwargs):
        context = super(BaseCreateView, self).get_context_data(**kwargs)
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        context['list_inlines'] = self.get_formset_inlines()
        context['system_name'] = SYSTEM_NAME

        context['url_create'] = '{app}:{model}-create'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_update'] = '{app}:{model}-update'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_detail'] = '{app}:{model}-detail'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_delete'] = '{app}:{model}-delete'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_list'] = '{app}:{model}-list'.format(app=self.model._meta.app_label,
                                                          model=self.model._meta.model_name)

        url_str = reverse(context['url_list']) + ' Criar'

        context['breadcrumbs'] = get_breadcrumbs(url_str)

        context['model_name'] = '%s' % (
                self.model._meta.verbose_name_plural or self.model._meta.object_name or '').title()
        context['apps'] = get_apps(self)

        context['has_add_permission'] = self.model(
        ).has_add_permission(self.request)
        context['has_change_permission'] = self.model(
        ).has_change_permission(self.request)
        context['has_delete_permission'] = self.model(
        ).has_delete_permission(self.request)

        return context

    def get_form_kwargs(self):
        """Método utilizado para adicionar o request

        Returns:
            Kwargs
        """

        kwargs = super(BaseCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_formset_inlines(self):
        """Metodo utilizado para instanciar os inlines.
        Returns:
            List -- Lista com os formulários inline do form principal
        """
        formset_inlines = []
        if hasattr(self, 'inlines') and self.inlines:
            for item in self.inlines:
                if item.model().has_change_permission(self.request):
                    if self.request.POST:
                        formset = item(self.request.POST, self.request.FILES, instance=self.object,
                                       prefix=item.model._meta.model_name)
                    else:
                        formset = item(instance=self.object,
                                       prefix=item.model._meta.model_name)
                    lista_instance_inline = formset.queryset.all() or []
                    formset.can_delete = item.model().has_delete_permission(self.request)
                    if not formset.can_delete:
                        formset.min_num = len(lista_instance_inline)
                    if not item.model().has_add_permission(self.request):
                        formset.max_num = len(lista_instance_inline)
                    if hasattr(formset, 'prefix') and formset.prefix:
                        # pode ser colocado o user aqui para utilizar na validação do forms
                        formset.form.user = self.request.user
                        formset_inlines.append(formset)
        return formset_inlines

    def form_valid(self, form):
        """Método para verificar se o formulário submetido está válido

        Arguments:
            form {Form} -- Formulário com os valores enviado para processamento

        Returns:
            Url -- O retorno é o redirecionamento para a URL de sucesso configurada na Views da app
        """
        formset_inlines = self.get_formset_inlines()
        if form.is_valid():
            for form_formset in formset_inlines:
                if not form_formset.is_valid():
                    return self.render_to_response(self.get_context_data(form=form))
            try:
                self.object = form.save()  
                for formset in formset_inlines:
                    formset.instance = self.object
                    formset.save()
            except:
                pass
            messages.success(request=self.request, message="'{}', Criado com Sucesso!".format(self.object),
                             extra_tags='success')
        else:
            messages.error(
                request=self.request, message="Ocorreu um erro, verifique os campos!", extra_tags='danger')
            return form.errors

        # salva e add outro novo_continue
        if '_addanother' in form.data:
            return redirect(reverse(self.get_context_data()['url_create']))
        # salva e continua editando
        elif '_continue' in form.data:
            return redirect(reverse(self.get_context_data()['url_update'], kwargs={'pk': self.object.pk}))
        # salva e redireciona pra lista
        else:
            return redirect(self.get_success_url())


class BaseDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Classe para gerenciar a deleção dos itens do sistema
    Raises:
        ValidationError -- [Deve ser definido o caminho para o template]
    """

    model = Base
    template_name_suffix = '_confirm_delete'

    def __init__(self):
        super(BaseDeleteView, self).__init__()

    def get_template_names(self):
        if self.template_name:
            return [self.template_name, ]
        return ['outside_template/base_delete.html', ]

    def get_success_url(self):
        try:
            if self.success_url and self.success_url != '':
                return reverse(self.success_url)
            else:
                url = reverse('{app}:{model}-list'.format(
                    app=self.model._meta.app_label,
                    model=self.model._meta.model_name)
                )
                return url
        except:
            url = reverse('{app}:{model}-list'.format(
                app=self.model._meta.app_label,
                model=self.model._meta.model_name)
            )
            return url

    def get_permission_required(self):
        """
            cria a lista de permissões que a view pode ter de acordo com cada model.
        """
        return ('{app}.delete_{model}'.format(app=self.model._meta.app_label, model=self.model._meta.model_name),)

    def get_context_data(self, **kwargs):
        context = super(BaseDeleteView, self).get_context_data(**kwargs)
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        object_list, many_fields = self.object.get_all_related_fields()
        context['object_list'] = object_list
        context['many_fields'] = many_fields
        context['system_name'] = SYSTEM_NAME

        context['url_create'] = '{app}:{model}-create'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_update'] = '{app}:{model}-update'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_detail'] = '{app}:{model}-detail'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_delete'] = '{app}:{model}-delete'.format(app=self.model._meta.app_label,
                                                              model=self.model._meta.model_name)
        context['url_list'] = '{app}:{model}-list'.format(app=self.model._meta.app_label,
                                                          model=self.model._meta.model_name)

        url_str = reverse(context['url_list']) + \
                  ' Apagar {}'.format(context['object'].pk)

        context['breadcrumbs'] = get_breadcrumbs(url_str)

        context['model_name'] = '%s' % (
                self.model._meta.verbose_name_plural or self.model._meta.object_name or '').title()
        context['apps'] = get_apps(self)

        context['has_add_permission'] = self.model(
        ).has_add_permission(self.request)
        context['has_change_permission'] = self.model(
        ).has_change_permission(self.request)
        context['has_delete_permission'] = self.model(
        ).has_delete_permission(self.request)

        return context


class LoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'core/registration/login.html'


class ProfileView(BaseTemplateView):
    template_name = 'core/registration/profile.html'


class SettingsView(BaseTemplateView):
    template_name = 'core/settings.html'


class ProfileUpdateView(View):
    """Views para atualizar os dados do perfil do usuario
    """

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            request.user.first_name = data.get('first_name')
            request.user.last_name = data.get('last_name')
            request.user.email = data.get('email')
            request.user.save()
        except Exception as error:
            print(error)

        return redirect('core:profile')  # Redirect using name url parameter


class UpdatePassword(View):
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST
            new_password = data.get('new-password')
            check_password = data.get('confirm-password')
            if (new_password == check_password):
                request.user.set_password(new_password)
                request.user.save()
                return redirect('core:login')
        except Exception as error:
            messages.error(request, 'Your password was successfully updated!')
            print('Error: {}'.format(error))
            return redirect('core:profile')


class ResetPassword(View):
    def get(self, request, *args, **kwargs):
        try:
            data = request.GET
            username = data.get('username')
            user = User.objects.get(username=username)
            email = data.get('email')
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            user.set_password(password)
            user.save()
            print(password)
            # Send new password to email
            email = EmailMessage(
                'Rercuperação de Senha',
                'Aqui está sua nova senha\n{}'.format(password),
                'guilherme.carvalho.carneiro@gmail.com',
                [user.email, ],
            )
            email.send()
        except Exception as error:
            print(error)
        finally:
            return HttpResponse('Finalizado')


class IndexAdminTemplateView(LoginRequiredMixin, PermissionRequiredMixin, BaseTemplateView):
    """Template View index"""
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_ip'] = self.request.META.get(
            'HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        url_str = '/'
        try:
            url_str = reverse('core:index')
        except:
            url_str = '/core/'
        if 'app_name' in context:
            url_str += context['app_name']
        context['breadcrumbs'] = get_breadcrumbs(url_str)
        context['system_name'] = SYSTEM_NAME
        return context

    def has_permission(self):
        """
        Verifica se tem alguma das permissões retornadas pelo
        get_permission_required, caso tenha pelo menos uma ele
        retorna True
        """
        return not self.request.user is None and self.request.user.is_authenticated and self.request.user.is_active
