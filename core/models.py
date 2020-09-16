import uuid

from django.contrib.auth import get_permission_codename
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRel
from django.db import models
from django.db import transaction
from django.db.models import (AutoField, ManyToManyField,
                              ManyToOneRel, ManyToManyRel,
                              OneToOneRel, BooleanField,
                              FileField, ImageField)
from rest_framework.pagination import PageNumberPagination

from .settings import use_default_manager

models.options.DEFAULT_NAMES += ('fk_fields_modal', 'fields_display', 'fk_inlines')


class PaginacaoCustomizada(PageNumberPagination):
    """Classe para configurar a paginação da API
        O padrão da paginação são 10 itens, caso queira
        alterar o valor basta passar na URL o parametro
        page_size = X
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100000


class BaseManager(models.Manager):
    """Sobrescrevendo o Manager padrão. Nesse Manager 
    os registros não são apagados do banco de dados
    apenas desativados, atribuindo ao campo deleted = True e
    enabled = True
    """

    def get_queryset(self):
        """Sobrescrevendo a queryset para filtrar os 
        registros que foram marcados como deleted
        """
        queryset = super(BaseManager, self).get_queryset()

        if ((hasattr(self.model, '_meta') and hasattr(self.model._meta, 'ordering') and self.model._meta.ordering) or
                ((hasattr(self.model, 'Meta') and hasattr(self.model.Meta, 'ordering') and self.model.Meta.ordering))):
            queryset = queryset.order_by(*(self.model._meta.ordering or self.model.Meta.ordering))

        return queryset.filter(deleted=False)


class Base(models.Model):
    """Classe Base para ser herdada pelas demais
    para herdar os métodos e atributos
    objects_all [Manager auxiliar para retornar todos os registro
                 mesmo que o use_default_manager esteja como True]
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enabled = models.BooleanField('Ativo', default=True)
    deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # Verificação se deve ser usado o manager padrão ou o customizado
    if use_default_manager is False:
        objects = BaseManager()
    else:
        objects = models.Manager()

    # Manager auxiliar para retornar todos os registro indepentende
    # da configuraçao do use_default_manager
    objects_all = models.Manager()

    def get_all_related_fields(self):
        """Método para retornar todos os campos que fazem referência ao 
        registro que está sendo manipulado
        
        Returns:
            [Listas] -- [São retornadas duas listas a primeira com
                         os campos 'comuns' e a segunda lista os campos que 
                         possuem relacionamento ManyToMany ou ForeignKey]
        """

        try:
            # Lista para retornar os campos que não são de relacionamento
            object_list = []

            # Lista para retornar os campos com relacionamento
            many_fields = []

            for field in self._meta.get_fields(include_parents=True):
                # Verificando se existe o atributo exclude no atributo que está sendo analisado
                if hasattr(self, 'exclude'):
                    if field.name in Base().get_exclude_hidden_fields() or field.name in self.exclude:
                        continue
                # Desconsiderando o campo do tipo AutoField da análise
                if isinstance(field, AutoField):
                    continue
                # Desconsiderando os campos com atributos auto_now_add ou now_add da análise
                if hasattr(field, "auto_now_add") or hasattr(field, "now_add"):
                    continue

                # Verificando o tipo do relacionamento entre os campos
                if type(field) is ManyToManyField:
                    many_fields.append((
                        field.verbose_name or field.name,
                        self.__getattribute__(field.name).all() or None
                    ))
                elif type(field) is ManyToOneRel or type(field) is ManyToManyRel:
                    many_fields.append((field.related_model._meta.verbose_name_plural or field.name,
                                        self.__getattribute__(
                                            (field.related_name or '{}_set'.format(field.name))
                                        )))
                elif type(field) is GenericRel or type(field) is GenericForeignKey:
                    many_fields.append(((field.verbose_name if hasattr(field, 'verbose_name') else None) or field.name,
                                        self.object.__getattribute__(field.name)))
                elif type(field) is OneToOneRel:
                    try:
                        object_list.append((field.related_model._meta.verbose_name or field.name,
                                            self.object.__getattribute__(field.name)))
                    except Exception:
                        pass
                elif type(field) is BooleanField:
                    object_list.append(((field.verbose_name if hasattr(field, 'verbose_name') else None) or field.name,
                                        "Sim" if self.__getattribute__(field.name) else "Nâo"))
                elif type(field) is ImageField or type(field) is FileField:
                    tag = ''
                    if self.__getattribute__(field.name).name:
                        if type(field) is ImageField:
                            tag = '<img width="100px" src="{url}" alt="{nome}" />'
                        elif type(field) is FileField:
                            tag = '<a  href="{url}" > <i class="fas fa-file"></i> {nome}</a>'
                        if tag:
                            tag = tag.format(url=self.__getattribute__(field.name).url,
                                             nome=self.__getattribute__(field.name).name.split('.')[0])

                    object_list.append(((field.verbose_name if hasattr(field, 'verbose_name') else None) or field.name,
                                        tag))
                else:
                    object_list.append(((field.verbose_name if hasattr(field, 'verbose_name') else None) or field.name,
                                        self.__getattribute__(field.name)))

        finally:
            # Retornando as listas
            return object_list, many_fields

    def delete(self, using='default', keep_parents=False):
        """Sobrescrevendo o método para marcar os campos
        deleted como True e enabled como False. Assim o
        item não é excluído do banco de dados.
        """
        # Verificando se deve ser utilizado o manager costumizado
        if use_default_manager is False:

            # Iniciando uma transação para garantir a integridade dos dados
            with transaction.atomic():

                # Recuperando as listas com os campos do objeto
                object_list, many_fields = self.get_all_related_fields()

                # Percorrendo todos os campos que possuem relacionamento com o objeto
                for obj, values in many_fields:
                    if values is not None and values.all():
                        values.all().update(deleted=True, enabled=False)
                # Atualizando o registro 
                self.deleted = True
                self.enabled = False
                self.save(update_fields=['deleted', 'enabled'])
        else:
            super(Base, self).delete()

    class Meta:
        """ Configure abstract class """
        abstract = True
        ordering = ['id']

    def get_exclude_hidden_fields(self):
        return ['enabled', 'deleted']

    def get_meta(self):
        return self._meta

    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        opts = self._meta
        codename = get_permission_codename('add', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self._meta
        codename = get_permission_codename('change', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        opts = self._meta
        codename = get_permission_codename('delete', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def __str__(self):
        return self.updated_on.strftime('%d/%m/%Y %H:%M:%S')
