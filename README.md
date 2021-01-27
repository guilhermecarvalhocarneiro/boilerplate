Projeto Django Manager Boilerplate
==================================

Esse projeto tem como objetivo facilitar o desenvolvimento dos sistemas utilizando manager do Django para automatizar a geração de código Boilerplate.  

As funcionalidades desse projeto são:

1) Renderização automática dos templates HTML do CRUD.  
2) Geração dos templates HTML estáticos de cada App/Model.  
3) Geração das URL's.
4) Geração das views  
5) Geração da APIRest.  
6) Geração de um projeto mobile utilizando o Flutter.  
7) Geração de documentação de desenvolvimento baseado em DocStrings.  

Para que o projeto funcione corretamente devem ser seguidas as etapas a seguir.


1. Adicionar o core no INSTALLED_APPS do settings
    ```
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',  
        
            'core',  
        
            '...',
        ]
    ```

2. Criar o virtualenv. `virtualenv env -p Python(Version: 2.7 ou 3)`  
3. Adicionar no diretório env/pythonx.x/lib/site-packages o arquivo .path apontando para o diretório desse projeto  
4. Ativar o virtualenv  
    3.1 Usuários Linux/Mac `. env/bin/activate`  
    3.2 Usuários Windows `env/Scripts/activate`  
5. Executar o comando `pip install -r requirements_dev.txt`
 
### Protegendo arquivos de serem sobrescritos ao rodar os comandos
> Para impedir que ao executar o comando build o arquivo seja novamente
> gerado pelo CLI basta adicionar no começo do arquivo o palavra #FileLocked

### Configurações para funcionamento do manager doc  
> Manage responsável por gerar a documentação baseado nas DocStrings. Utiliza a biblioteca Sphinx

Adicionar no settings a lista abaixo, com as apps que deseja gerar a documentação  

```DOC_APPS = ['nome_da_app_1', 'nome_da_app_2']```

### Configurações para funcionamento do manager flutter  
> Manage responsável por gerar o projeto Flutter.

Adicionar no settings a lista abaixo, com as apps que deseja trabalhar no projeto Flutter

```FLUTTER_APPS = ['nome_da_app_1', 'nome_da_app_2']```

__________

## Executando os manager's  

### Doc  
> Manage responsável por gerar a documentação de desenvolvimento do sistema.

```python manage.py doc NOME_DO_PROJETO_DJANGO "NOME DO DESENVOLVEDOR"```

### Build
> Manage responsável por gerar os templates HTML, as views, configurar  as url's do projeto e gerar a APIRest.

```python manage.py build NOME_DA_APP NOME_DO_MODEL```

### Build (Templates HTML)
> Manage responsável por gerar os templates html, para que o parser funcione corretamente
> é necessário configurar no Class Meta do model o parâmetro fields_display = []
> contendo os campos que deseja que sejam mostrados na listview.
>
> Para que o build gere os formulários modais dos campos ForeignKey deve ser informado também no
> Class Meta do model o parâmetro fk_fields_modal com os campos que deseja que sejam criados os modais.

```python manage.py build --parser_html NOME_DA_APP NOME_DO_MODEL```

### Configuração do urlpatterns do projeto no settings
> O formato da url de inclusão da APP no projeto deve serguir o padrão abaixo

``` path('core'/, include(('model.urls', 'models'), namespace='namespace_model')) ```


### Flutter
> Manage responsável por gerar o projeto Flutter, é obrigatório determinar qual o gerenciador de estado será utilizado no gerenciamento de estado da aplicação, as possibilidades são MobX (--init_mobx), Provider (--init_provider), Cubit (--init_cubit)

Para gerar o projeto com todas as apps configuradas no FLUTTER_APPS
```python manage.py flutter```

Para atualizar o arquivo pubspec.yaml
```python manage.py flutter --yaml```

Para gerar os arquivos do Flutter de uma determinada App e seus models  

```python manage.py flutter --app NomeDaApp```

Para gerar os arquivos do Flutter de um determinado Model de uma App
```python manage.py flutter --model NomeDaApp nome_do_model```

Para renderizar o arquivo main.dart

```python manage.py flutter --main```
