from django import forms
from django.forms.fields import BooleanField, DateField, DateTimeField

from .models import Base


class BaseForm(forms.ModelForm):
    """Form para ser usado no classe based views"""

    # Sobrescrevendo o Init para aplicar as regras CSS
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            class_attrs = ""
            class_attrs = 'form-control'
            # Verificando se o campo está configurado como obrigatório
            if self.fields[field].required:
                class_attrs = "{} {}".format(class_attrs, 'obrigatorio')
            # Verificando se o campo é Booleano
            if isinstance(self.fields[field], BooleanField) is True:
                class_attrs = "{} {}".format(class_attrs, 'checked-left')
            # Verificando se o campo é do tipo DateTime
            if isinstance(self.fields[field], DateTimeField) is True:
                class_attrs = "{} {}".format(class_attrs, 'datetimefield')
            # Verificando se o campo é do tipo Date
            if isinstance(self.fields[field], DateField) is True:
                class_attrs = "{} {}".format(class_attrs, 'datefield')
            # # Verificando se o campo é do tipo FileField
            # if isinstance(self.fields[field], FileField) is True:
            #     class_attrs = "{} {}".format(class_attrs, 'custom-file-input')
            # # Verificando se o campo é do tipo ImageField
            # if isinstance(self.fields[field], ImageField) is True:
            #     class_attrs = "{} {}".format(class_attrs, 'custom-file-input')
            # Verificando se o campo é do tipo BooleanField
            if isinstance(self.fields[field], BooleanField) is True:
                class_attrs = "{} {}".format(class_attrs, 'form-check-input')
            # Atualizando os atributos do campo para adicionar as classes
            # conforme as regras anteriores
            self.fields[field].widget.attrs.update({
                'class': class_attrs
            })

    class Meta:
        model = Base
        exclude = ['enabled', 'deleted']
