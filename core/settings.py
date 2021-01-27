"""
Settings do projeto Core
"""

try:
    from django.conf import settings

    SYSTEM_NAME = settings.PROJECT_NAME
except:
    SYSTEM_NAME = 'Nuvols Core'

"""Variável responsável por configurar qual Manager utilizar
Se for True usa o manager padrão que retorna todos os elementos
mesmo os que foram marcados com deleted = True e enabled = False
Se for False usa o manager configurado para não mostrar 
os elementos marcados com deleted = True e enabled
"""
try:
    use_default_manager = settings.USE_DEFAULT_MANAGER
except:
    use_default_manager = False

# Carregando o caminho para o projeto Flutter
try:
    from django.conf import settings

    FLUTTER_PROJECT_PATH = settings.FLUTTER_PROJECT_PATH
except:
    pass

# Carregando as apps que devem ser mapeadas para gerar o projeto Flutter
try:
    from django.conf import settings

    FLUTTER_APPS = settings.FLUTTER_APPS
except:
    pass

# Carregando o URI da API
try:
    from django.conf import settings

    API_PATH = settings.API_PATH
except:
    pass

# Carregando as apps que será gerada a documentação utilizando o Sphinx
try:
    from django.conf import settings

    DOC_APPS = settings.DOC_APPS
except:
    pass

# Carregando a URL do login redirect
try:
    from django.conf import settings

    LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
except expression as identifier:
    pass

# Carregando a URL do logout redirect
try:
    from django.conf import settings

    LOGOUT_REDIRECT_URL = settings.LOGOUT_REDIRECT_URL
except expression as identifier:
    pass
