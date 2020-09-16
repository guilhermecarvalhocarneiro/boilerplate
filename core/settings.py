
try:
    from django.conf import settings
    SYSTEM_NAME = settings.PROJECT_NAME
except:
    SYSTEM_NAME = 'EASY CMS'

try:
    """Variável responsável por configurar qual Manager utilizar
    Se for True usa o manager padrão que retorna todos os elementos
    mesmo os que foram marcados com deleted = True e enabled = False
    Se for False usa o manager configurado para não mostrar 
    os elementos marcados com deleted = True e enabled
    """
    use_default_manager = settings.USE_DEFAULT_MANAGER
except:
    use_default_manager = False


try:
    from django.conf import settings
    # Caminho para criação do Projeto Flutter
    FLUTTER_PROJECT_PATH = settings.FLUTTER_PROJECT_PATH
except:
    pass

try:
    from django.conf import settings
    # Apps a serem mapeadas
    FLUTTER_APPS = settings.FLUTTER_APPS
except:
    pass

try:
    from django.conf import settings
    # Caminho da API
    API_PATH = settings.API_PATH
except:
    pass

try:
    from django.conf import settings
    # Apps a serem geradas a documentação
    DOC_APPS = settings.DOC_APPS
except:
    pass

try:
    from django.conf import settings
    LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
except expression as identifier:
    pass

try:
    from django.conf import settings
    LOGOUT_REDIRECT_URL = settings.LOGOUT_REDIRECT_URL
except expression as identifier:
    pass
