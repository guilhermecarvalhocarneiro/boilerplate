import os
import platform
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand

from nuvols.core.management.commands.utils import Utils
from nuvols.core.management.commands.parser_content import ParserContent
from nuvols.core.models import Base
from nuvols.core.settings import FLUTTER_APPS, SYSTEM_NAME, API_PATH


class StateManager(Enum):
    Provider = 1
    MobX = 2
    Cubit = 3


class AppModel:
    """Auxiliary class for accessing template files as well as recurring methods

    Arguments:
        path_flutter {String} -- Flutter project path
        app_name {String} -- Name of the App to be mapped

    Keyword Arguments:
        model_name {String} -- Name of the model to be mapped (default: {None})
    """

    def __init__(self, path_flutter, app_name, model_name=None):
        try:
            self.path_flutter = path_flutter
            self.models = None
            self.model = None
            self.app_name = str(app_name).strip()
            self.app_name_lower = self.app_name.lower()
            self.app = apps.get_app_config(self.app_name_lower)
            self.model_name = str(model_name).strip()
            self.model_name_lower = self.model_name.lower()
            if model_name is not None:
                self.model = self.app.get_model(self.model_name)
            else:
                self.models = ((x, x.__name__.strip(), x.__name__.strip().lower())
                               for x in self.app.get_models())
            self.operation_system = platform.system().lower()

        except Exception as error:
            raise error

    def get_path_app_dir(self):
        """Method to return the app path in the Flutter project

        Returns:
            String -- Path of the app directory in the Flutter project
        """
        try:
            return Path("{}/lib/apps/{}".format(self.path_flutter, self.app_name_lower))
        except Exception as error:
            Utils.show_message(f"Error in get_path_app_dir: {error}", error=True)

    def get_path_app_model_dir(self):
        """ Method to return the model path in the Flutter project

        Returns:
            String -- Model directory path in the Flutter project
        """
        try:
            return Path("{}/lib/apps/{}/{}".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(f"Error in get_path_app_model_dir {error}", error=True)

    def get_path_views_dir(self):
        """Method to return the views directory path

        Returns:
            String -- Views directory path in the Flutter project
        """
        try:
            return Path("{}/lib/apps/{}/{}/pages/".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(f"Error in get_path_views_dir {error}", error=True)

    def get_path_files_views(self):
        """Method to return the files of the pages in the Flutter project

        Returns:
            List<String> -- Path of each page file in create, detail, index, list and update
        """
        try:
            __create = Path("{}/lib/apps/{}/{}/pages/create.dart".format(self.path_flutter,
                                                                         self.app_name_lower, self.model_name_lower))
            __detail = Path("{}/lib/apps/{}/{}/pages/detail.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __index = Path("{}/lib/apps/{}/{}/pages/index.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __list = Path("{}/lib/apps/{}/{}/pages/list.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __update = Path("{}/lib/apps/{}/{}/pages/update.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))

            return __create, __detail, __index, __list, __update
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_files_views: {error}", error=True)

    def get_path_data_file(self):
        """Method to retrieve data.dart file path

        Returns:
            String -- Path to file data.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/data.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(f"Error in get_path_data_file: {error}", error=True)

    def get_path_model_file(self):
        """Method to retrieve the model.dart file path

        Returns:
            String -- Path to file model.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/model.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(f"Error in get_path_model_file {error}", error=True)

    def get_path_controller_file(self):
        """Method to retrieve the path to the controller.dart file

        Returns:
            String -- Path to file controller.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/controller.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_controller_file {error}", error=True)

    def get_path_provider_file(self):
        """Method to retrieve the path to the provider.dart file

        Returns:
            String -- Path to file controller.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/provider.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_provider_file {error}", error=True)

    def get_path_cubit_file(self):
        """Method to retrieve the path to the cubit.dart file

        Returns:
            String -- Path to file cubit.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/cubit.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_provider_file {error}", error=True)

    def get_path_cubit_state_file(self):
        """Method to retrieve the path to the state of cubit file

        Returns:
            String -- Path to file controller.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/state.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_provider_file {error}", error=True)

    def get_path_service_file(self):
        """Method to retrieve the path to the service.dart file

        Returns:
            String -- Path to file service.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/service.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            Utils.show_message(
                f"Error in get_path_service_file {error}", error=True)

    def print_string(self):
        """Method for printing class attributes to assist in debugging the script
        """

        print("App: {} Name: {} - {}".format(self.app,
                                             self.app_name, self.app_name_lower))
        print("Model: {} Name: {} - {}".format(self.model, self.model_name, self.model_name_lower)
              )
        print("")
        print("Caminhos:")
        print(f"Diretório App {self.get_path_app_dir()}")
        print(f"Diretório Model {self.get_path_app_model_dir()}")
        print(f"Diretório views {self.get_path_views_dir()}")
        print(f"Data {self.get_path_data_file()}")
        print(f"Model {self.get_path_model_file()}")
        print(f"Controller {self.get_path_controller_file()}")
        print(f"Service {self.get_path_service_file()}")
        c, d, i, l, u = self.get_path_files_views()
        print("")
        print("views \nCreate: {}\nDetail: {}\nIndex: {}\nList: {}\nUpdate: {}".format(
            c, d, i, l, u))

        print("Models (Generator)")
        if self.models is not None:
            for __model in self.models:
                print(
                    "Model: {} Name: {} - {}".format(__model[0], __model[1], __model[2]))
        else:
            print("None")

    def check_inherited_base(self, model):
        """ Method to check if the model that was passed to be parsed inherits from the Base Model class of Nuvols Core

        Returns:
            Bool -- True when method inherits from class false when not inheriting
        """
        try:
            __instance = apps.get_app_config(self.app_name_lower)
            __model = __instance.get_model(model)
            return issubclass(__model, Base)
        except Exception as error:
            Utils.show_message(
                f"Error in check_inherited_base: {error}")
            return False

    def get_app_model_name(self, title_case=False):
        """ Method to return a String with the name of the App and Model in NomeAppNomeModel format.

        Arguments:
            title_case {bool} -- Determines whether the return should be AppNameModelName or AppNameModelName

        Returns:
            String -- String in the format NomeAppModel or nomeAppModel
        """
        try:
            if title_case is True:
                return f"{self.app_name.title()}{self.model_name}"
            return f"{self.app_name}{self.model_name}"
        except Exception as error:
            Utils.show_message(
                f"Error in get_app_model_name: {error}")
            return None


class Command(BaseCommand):
    help = """Manager responsible for generating the flutter project as well as performing other operations such as 
              configuring the pubspec.yaml file, changing the code of the main.dart class and also generating the 
              codes for each app based on the models of the Django project"""

    def __init__(self):
        super().__init__()
        self.path_root = os.getcwd()
        self.path_core = os.path.join(self.BASE_DIR, "core")
        self.operation_system = platform.system().lower()
        self.state_manager = StateManager.Provider
        self.state_manager_provider = True

        _path_project = os.getcwd()

        if self.operation_system == "windows":
            self.project = os.getcwd().split("\\")[-1:][0]
            self.flutter_dir = "{}\\Flutter\\{}".format(
                "\\".join(os.getcwd().split("\\")[:-2]), self.project.lower())
            self.project = self.project.replace("-", "").replace("_", "")
            self.flutter_project = "{}".format(self.project)
            self.utils_dir = "{}\\lib\\utils\\".format(self.flutter_dir)
            self.ui_dir = "{}\\lib\\user_interface\\".format(self.flutter_dir)
            self.config_file = "{}\\lib\\utils\\config.dart".format(
                self.flutter_dir)
            self.util_file = "{}\\lib\\utils\\util.dart".format(
                self.flutter_dir)
            self.process_controller_file = "{}\\lib\\utils\\process.controller.dart".format(
                self.flutter_dir)
            self.process_provider_file = "{}\\lib\\utils\\process.provider.dart".format(
                self.flutter_dir)
            self.snippet_dir = "{}\\{}".format(
                self.path_core, "management\\commands\\snippets\\flutter\\")

            self.app_configuration = "{}\\lib\\apps\\configuracao\\".format(
                self.flutter_dir)
            self.app_configuration_page_file = (
                f"{self.app_configuration}\\index.page.dart")
            self.app_configuration_controller_file = (
                f"{self.app_configuration}\\controller.dart")
            self.app_configuration_profile_file = (
                f"{self.app_configuration}\\model.dart")
            self.app_configuration_cubit_file = f"{self.app_configuration}\\cubit.dart"
            self.app_configuration_cubit_state_file = (
                f"{self.app_configuration}\\state.dart")
        else:
            self.project = _path_project.split("/")[-1:][0]
            self.project = self.project.replace("-", "").replace("_", "")
            self.flutter_dir = "{}/Flutter/{}".format(
                "/".join(_path_project.split("/")[:-2]), self.project.lower())
            self.flutter_project = "{}".format(self.project)
            self.utils_dir = "{}/lib/utils/".format(self.flutter_dir)
            self.ui_dir = "{}/lib/user_interface/".format(self.flutter_dir)
            self.config_file = "{}/lib/utils/config.dart".format(
                self.flutter_dir)
            self.util_file = "{}/lib/utils/util.dart".format(self.flutter_dir)
            self.process_controller_file = "{}/lib/utils/process.controller.dart".format(
                self.flutter_dir)
            self.snippet_dir = "{}/{}".format(
                self.path_core, "management/commands/snippets/flutter/")
            self.app_configuration = "{}/lib/apps/configuracao/".format(
                self.flutter_dir)
            self.app_configuration_page_file = (
                f"{self.app_configuration}/index.page.dart")
            self.app_configuration_controller_file = (
                f"{self.app_configuration}/controller.dart")

        self.current_app_model = None

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
    )

    _tipos_originais = [
        "SmallAutoField", "AutoField", "BLANK_CHOICE_DASH", "BigAutoField", "BigIntegerField",
        "BinaryField", "BooleanField", "CharField", "CommaSeparatedIntegerField",
        "DateField", "DateTimeField", "DecimalField", "DurationField",
        "EmailField", "Empty", "FileField", "Field", "FieldDoesNotExist",
        "FilePathField", "FloatField", "GenericIPAddressField", "IPAddressField",
        "IntegerField", "FieldFile", "NOT_PROVIDED", "NullBooleanField", "ImageField",
        "PositiveIntegerField", "PositiveSmallIntegerField", "SlugField", "SmallIntegerField",
        "TextField", "TimeField", "URLField", "UUIDField", "ForeignKey", "OneToOneField",
    ]

    _tipos_flutter = [
        "int", "int", "BLANK_CHOICE_DASH",
        "int", "int", "String", "bool", "String",
        "String", "DateTime", "DateTime", "double", "int",
        "String", "String", "String", "String", "String", "String",
        "double", "String", "String", "int", "String", "String",
        "bool", "String", "int", "int", "String", "int",
        "String", "DateTime", "String", "String", "String", "int",
    ]

    _tipos_sqlite = [
        "INT", "INT", "BLANK_CHOICE_DASH",
        "BIGINT", "BIGINT", "TEXT",
        "BOOLEAN", "TEXT", "TEXT",
        "DATE", "DATETIME", "DOUBLE", "INT",
        "TEXT", "TEXT", "TEXT", "TEXT",
        "TEXT", "TEXT", "FLOAT",
        "TEXT", "TEXT", "INT", "TEXT", "TEXT",
        "BOOLEAN", "TEXT", "INT", "INT", "TEXT",
        "SMALLINT", "TEXT", "DATETIME", "TEXT", "TEXT", "TEXT", "INT",
    ]

    def add_arguments(self, parser):
        """Method for adding positional arguments (required) and optional arguments
        """

        parser.add_argument("App", type=str, nargs="?")
        parser.add_argument("Model", type=str, nargs="?")

        parser.add_argument(
            "--app", action="store_true", dest="app", help="Criar a App e seus models"
        )
        parser.add_argument(
            "--app_model", action="store_true", dest="app_model",
            help="Criar a App e o Model informado")

        parser.add_argument(
            "--main", action="store_true", dest="main", help="Renderizar a main.dart")
        parser.add_argument(
            "--yaml", action="store_true", dest="yaml", help="Refatorando o YAML")

        parser.add_argument(
            "--build_mobx", action="store_true", dest="build_mobx",
            help="Gerar os arquivos do MobX")

        parser.add_argument(
            "--init_provider", action="store_true", dest="init_provider",
            help="Gerar o projeto Flutter utilizando o Provider como gerencia de estado.",
        )
        parser.add_argument(
            "--init_mobx", action="store_true", dest="init_mobx",
            help="Gerar o projeto Flutter utilizando o MobX como gerencia de estado.",
        )
        parser.add_argument(
            "--init_cubit", action="store_true", dest="init_cubit",
            help="Gerar o projeto Flutter utilizando o Cubit como gerencia de estado.",
        )
        parser.add_argument(
            "--clear", action="store_true", dest="clear", help="Limpar projeto flutter.")

    def __ignore_base_fields(self, field) -> bool:
        """Method to check if the model attribute should be ignored in the parser process according to
           tuple __ignore_fields

        Arguments:
            field {String} -- Field name

        Returns:
            bool -- True if it is to be ignored.
        """
        try:
            __ignore_fields = ["id", "enabled", "deleted", "createdOn",
                               "created_on", "updatedOn", "updatedOn", ]
            return field in __ignore_fields
        except Exception as error:
            Utils.show_message(f"Error in __ignore_base_fields: {error}", error=True)

    def __to_camel_case(self, text, flutter=False):
        """Method to convert the text passed in the text parameter from the snake_case format to the camelCase format

        Arguments:
            str {str} -- Text to be converted
            flutter {bool} -- Determines whether the CamelCase return should be camelCase or CamelCase
                              (default: {False})
        """
        try:
            components = text.split("_")
            if flutter is True:
                if len(components) == 1:
                    __string = components[0]
                    return "{}{}".format(__string[:1].lower(), __string[1:])
                return components[0] + "".join(x.title() for x in components[1:])
            return components[0] + "".join(x.title() for x in components[1:])
        except Exception as error:
            Utils.show_message(f"Error in Camel Case: {error}")
            return None

    def __get_snippet(self, path=None, file_name=None, state_manager=False):
        """Method to retrieve the value of the snippet file to be converted by merging with the values based on models
           from the Django project

        Arguments:
            path {str} - Absolute path to the optional file,
                         must be passed when the snippet path is in the same flutter directory
            file_name {str} - Name of the snippet file in xpto.txt format, must be passed together
                              with state_manager = True to retrieve the correct state manage snippet
            state_manager {bool} - Value to determine whether the snippet will be retrieved taking into account
                                   the chosen state_manager

        Returns:
            str -- Text to be used to interpolate model data
        """

        try:
            if file_name and state_manager is True:
                if self.state_manager == StateManager.Provider:
                    path = f"{self.snippet_dir}provider/"
                if self.state_manager == StateManager.MobX:
                    path = f"{self.snippet_dir}mobx/"
                if self.state_manager == StateManager.Cubit:
                    path = f"{self.snippet_dir}cubit/"
                path += file_name

            if os.path.isfile(path):
                with open(path, encoding="utf-8") as arquivo:
                    return arquivo.read()
        except Exception as e:
            Utils.show_message(f"Error in get_snippet {e}", error=True)
            sys.exit()

    def __init_flutter(self):
        """Method responsible for creating the basic structure of the flutter project
        """
        try:
            if not Utils.check_dir(self.flutter_dir):
                Utils.show_message("Criando o projeto flutter.")
                __cmd_flutter_create = "flutter create --androidx {}".format(
                    self.flutter_dir)
                subprocess.call(__cmd_flutter_create, shell=True)
                Utils.show_message("Projeto criado com sucesso.")
        except Exception as error:
            Utils.show_message(
                f"Error in __init_flutter: {error}", error=True)

    def __build_flutter(self):
        """
        Method to update the project dependency package, run the pub get command to download the dependency packages
        and also update the main.dart file based on the corresponding state manager snippet
        """
        try:
            if Utils.check_dir(self.flutter_dir):
                Utils.show_message("Atualizando o arquivo de dependências.")
                self.__add_packages()
                time.sleep(3)

                current_path = os.getcwd()
                os.chdir(self.flutter_dir)
                subprocess.run("flutter pub get", shell=True)
                os.chdir(current_path)
                time.sleep(3)

                Utils.show_message("Atualizando o arquivo main.dart.")
                self.__replace_main()
                time.sleep(3)

                if self.state_manager == StateManager.MobX:
                    self.__build_mobx()

        except Exception as error:
            Utils.show_message(f"Error in __build_flutter: {error}", error=True)

    def __build_menu_home_page_itens(self):
        """Method responsible for generating the flutter code that creates the navigation component using cards
           from the APP's home screen."""
        try:
            __itens_menu = ""
            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __model = model[1]
                    __itens_menu += f"list.add(Itens(title: '{__model.title()}'"
                    __itens_menu += f",icon: FontAwesomeIcons.folderOpen,uri: {__app.title()}{__model.title()}"
                    __itens_menu += f"Views.{__model.title()}ListPage(),),);"
            return __itens_menu
        except Exception as error:
            Utils.show_message(f"Error in __build_menu_home_page_itens: {error}", error=True)

    def __register_provider(self):
        """Method responsible for registering the Provider's of the classes in the main.dart file when choosing the
           Provider state manager"""
        __register_provider = ""
        __import_provider = ""
        try:
            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __import_provider += f"import 'apps/{__app.lower()}/{model[1].lower()}/provider.dart';\n"
                    __register_provider += f"ChangeNotifierProvider<{model[1].title()}Provider> "
                    __register_provider += f"(create: (_) => {model[1].title()}Provider(),),\n"

            __import_provider += f"import 'apps/auth/provider.dart';\n"
            __register_provider += f"ChangeNotifierProvider<SettingsProvider>(create: (_) => SettingsProvider(),),\n"
            __register_provider += f"ChangeNotifierProvider<AuthProvider>(create: (_) => AuthProvider(),),\n"
        except Exception as error:
            Utils.show_message(f"Error in __register_provider: {error}", error=True)
        return __import_provider, __register_provider

    def __register_cubit(self) -> tuple:
        """Method for registering Cubit components in the main.dart file when the Cubit state manager has been chosen"""
        _register = ""
        __import = ""
        try:
            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name

                for model in __current_app.models:
                    __import += f"import 'apps/{__app.lower()}/{model[1].lower()}/cubit.dart';\n"
                    _register += f"BlocProvider<{model[1].title()}Cubit>(create: (_) => {model[1].title()}Cubit(),),\n"

            __import += f"import 'apps/auth/cubit.dart';\n"
            _register += f"BlocProvider<SettingsCubit>(create: (_) => SettingsCubit(),),\n"
            _register += f"BlocProvider<AuthCubit>(create: (_) => AuthCubit(),),\n"
        except Exception as error:
            Utils.show_message(f"Error in __register_cubit: {error}", error=True)
        return __import, _register

    def __mapping_all_application(self):
        """Method responsible for browsing all Django apps configured in the FLUTTER_APPS tuple in the Django
           project's settings.py file, which should be used as the basis for generating the Flutter project"""
        try:
            __imports_views = ""
            __imports_controllers = ""
            __controllers_models = ""
            __list_views = ""
            __current_app = None

            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __model = model[1]
                    __imports_views += "import 'apps/{}/{}/pages/list.dart' as {}Views;\n".format(
                        __app, __model.lower(), f"{__app.title()}{__model}")
                    __list_views += f"Itens(title: '{model[0]._meta.verbose_name}', "
                    __list_views += f"icon: FontAwesomeIcons.folderOpen, uri: {__app.title()}{__model}."
                    __list_views += f"{__model}ListPage()),\n"
                    __imports_controllers += f"import 'apps/{__app.lower()}/{__model.lower()}/controller.dart' "
                    __imports_controllers += f"as {__app.title()}{__model.title()}Controller;\n"
                    __controller_model = f"{__app.title()}{__model.title()}Controller.{__model}"
                    __controllers_models += f"getIt.registerSingleton<{__controller_model}Controller>"
                    __controllers_models += f"({__controller_model}Controller(), instanceName: "
                    __controllers_models += f"'{__app.title()}{__model.title()}Controller');\n    "

            return __imports_views, __imports_controllers, __controllers_models, __list_views

        except Exception as error:
            Utils.show_message(
                f"Error in __mapping_all_application: {error}", error=True)

    def __indexpage_parser(self, app):
        """Method for creating the Model index page

        Arguments:
            app {AppModel} -- AppModel class instance
        """
        try:
            __indexpage_file = Path(f"{app.get_path_views_dir()}/index.dart")
            if Utils.check_file_is_locked(__indexpage_file):
                return

            content = ParserContent(
                ["$ModelClass$", "$ModelClassCamelCase$", "$project$"],
                [app.model_name, self.__to_camel_case(app.model_name, True),
                 self.flutter_project.lower(), ], self.__get_snippet(file_name="index_page.txt", state_manager=True),
            ).replace()

            with open(__indexpage_file, "w", encoding="utf-8") as page:
                page.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __indexpage_parser {error}", error=True)

    def __listpage_parser(self, app):
        """Method for creating the Model listing page

         Arguments:
             app {AppModel} - AppModel class instance
        """
        try:
            __listpage_file = Path(f"{app.get_path_views_dir()}/list.dart")
            if Utils.check_file_is_locked(__listpage_file):
                return

            content = ParserContent(
                ["$App$", "$Model$", "$ModelClass$", "$ModelClassCamelCase$", "$project$"],
                [app.app_name, app.model_name_lower, app.model_name, self.__to_camel_case(app.model_name, True),
                 self.flutter_project], self.__get_snippet(file_name="list_page.txt", state_manager=True)
            ).replace()

            with open(__listpage_file, "w", encoding="utf-8") as page:
                page.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __listpage_parser: {error}", error=True)

    def __get_attributes_data(self, attribute, model_name, name, name_title) -> str:
        """Method for recovering the structure of field attributes to the create and update pages

         Arguments:
             attribute {String} - String with the type of attribute to be render

         Returns:
             String - Data attribute structure
        """

        __attribute = ""
        try:
            if attribute == "int":
                if f"id{model_name.lower()}" == name.lower():
                    __attribute = "{0}_{1}.id = int.tryParse(_{1}Form{2}.text ?? 0);\n".format(
                        " " * 16, self.__to_camel_case(model_name, True), name_title)
                else:
                    __attribute = "{0}_{1}.{2} = int.tryParse(_{1}Form{3}.text ?? 0);\n".format(
                        " " * 16, self.__to_camel_case(model_name, True), name,
                        name_title)

            elif attribute == "double":
                __attribute = "{0}_{1}.{2} = double.tryParse(_{1}Form{3}.text ?? 0.0);\n".format(
                    " " * 16, self.__to_camel_case(model_name, True), name, name_title)

            elif attribute == "bool":
                __attribute = "{0}_{1}.{2} = _{1}Form{3}.text ?? true;\n".format(
                    " " * 16, self.__to_camel_case(model_name, True), name, name_title)

            elif attribute == "DateTime":
                __attribute = '{0}_{1}.{2} = '.format(" " * 16, self.__to_camel_case(model_name, True), name)
                __attribute += '_{0}Form{1}.text != "" ?Util.convertDate(_{0}Form{1}.text): null;\n'.format(
                    self.__to_camel_case(model_name, True), name_title)

            else:
                __attribute = '{0}_{1}.{2} = _{1}Form{3}.text ?? "";\n'.format(
                    " " * 16, self.__to_camel_case(model_name, True), name, name_title)
        except Exception as error:
            Utils.show_message(f"Error in __get_attributes: {error}", error=True)
        finally:
            return __attribute

    def __get_controllers_data(self, attribute, model_name, name, name_title) -> str:
        """Method to build the command line responsible for retrieving values
         controller

         Arguments:
             attribute {String} - String containing the type of the attribute being parsed

         Returns:
             String - Line containing the dart command to retrieve the controller value
        """
        __controllers_data = ""
        try:
            if attribute == "int":
                if f"id{model_name.lower()}" == name.lower():
                    __controllers_data = "{0}_{1}.id = int.tryParse(_{1}Form{2}.text ?? 0);\n".format(
                        " " * 6, self.__to_camel_case(model_name, True), name_title)
                else:
                    __controllers_data = "{0}_{1}.{2} = int.tryParse(_{1}Form{3}.text ?? 0);\n".format(
                        " " * 6, self.__to_camel_case(model_name, True), name, name_title)
            elif attribute == "double":
                __controllers_data = "{0}_{1}.{2} = double.tryParse(_{1}Form{3}.text ?? 0.0);\n".format(
                    " " * 6, self.__to_camel_case(model_name, True), name, name_title)
            elif attribute == "bool":
                __controllers_data = "{0}_{1}.{2} = _{1}Form{3}.text ?? true;\n".format(
                    " " * 6, self.__to_camel_case(model_name, True), name, name_title)
            elif attribute == "DateTime":
                __controllers_data = '{0}_{1}.{2} = _{1}Form{3}.text != ""?'.format(
                    " " * 6, self.__to_camel_case(model_name, True), name, name_title)
                __controllers_data += ' Util.convertDate(_{}Form{}.text) : null;\n'.format(
                    self.__to_camel_case(model_name, True), name_title)
            else:
                __controllers_data = "{0}_{1}.{2} = _{1}Form{3}.text;\n".format(
                    " " * 6, self.__to_camel_case(model_name, True), name, name_title)
        except Exception as error:
            Utils.show_message(f"Error in __get_controllers_data: {error}", error=True)
        finally:
            return __controllers_data

    def __create_update_page_parser(self, app, create_page=True):
        """Method responsible for creating the app's data persistence page

        Arguments:
            app {String} -- Django app to be used as a basis for creating registration creation and editing page
            create_page {bool} -- Boolean used to determine if the insert or update page is to be created
                                  (default{True})
        """
        try:
            if create_page is True:
                __create_page_file = Path(f"{app.get_path_views_dir()}/create.dart")
                content = self.__get_snippet(file_name="create_page.txt", state_manager=True)
                if Utils.check_file_is_locked(__create_page_file):
                    return
            else:
                __create_page_file = Path(f"{app.get_path_views_dir()}/update.dart")
                content = self.__get_snippet(file_name="update_page.txt", state_manager=True)
                if Utils.check_file_is_locked(__create_page_file):
                    return

            content_form = self.__get_snippet(f"{self.snippet_dir}text_field.txt")

            content_attributes = ""
            text_fields = ""
            attributes_data = ""
            clear_data = ""
            edited_attributes = ""
            get_controllers_data = ""

            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split(".")
                __nameTitle = self.__to_camel_case(__name.title())
                __name = self.__to_camel_case(__name.lower())

                if self.__ignore_base_fields(__name):
                    continue

                field_type = (
                    str(str(type(field)).split(".")[-1:])
                    .replace('["', "")
                    .replace("'>\"]", ""))

                attribute = self._tipos_flutter[self._tipos_originais.index(field_type)]
                content_attributes += "  final _{0}Form{1} = TextEditingController();\n".format(
                    self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = content_form
                controller = "_{}Form{}".format(self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = text_field.replace("$controller$", controller)
                text_field = text_field.replace("$Field$", str(field.verbose_name).replace("R$", "R\$"))
                text_fields += text_field

                attributes_data += self.__get_attributes_data(
                    attribute, app.model_name, __name, __nameTitle)

                get_controllers_data += self.__get_controllers_data(
                    attribute, app.model_name, __name, __nameTitle)

                clear_data += "    {}.clear();\n".format(controller)

                if __name.startswith(f"id{app.model_name_lower}"):
                    __name = "id"

                edited_attributes += "      {}.text = _{}.{}.toString();\n".format(
                    controller, self.__to_camel_case(app.model_name, True), __name)

            content = ParserContent(
                ["$app$", "$App$", "$Model$", "$model$",
                 "$ModelClass$", "$ModelClassCamelCase$",
                 "$project$", "$Attributes$", "$Form$", "$AttributesData$", "$ClearData$",
                 "$EditedAttributes$", "$GetValuesControllers$", ],
                [app.app_name_lower, app.app_name_lower,
                 self.__to_camel_case(app.model_name, True), app.model_name_lower,
                 app.model_name, self.__to_camel_case(app.model_name, True),
                 self.flutter_project, content_attributes, text_fields, attributes_data,
                 clear_data, edited_attributes, get_controllers_data],
                content,
            ).replace()

            with open(__create_page_file, "w", encoding="utf-8") as page:
                page.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __create_update_page_parser: {error}", error=True)

    def __detailpage_parser(self, app):
        """Method for creating the Model detail page

         Arguments:
             app {AppModel} - AppModel class instance
        """
        try:
            __detail_page_file = Path(f"{app.get_path_views_dir()}/detail.dart")

            if Utils.check_file_is_locked(__detail_page_file):
                return

            content = ParserContent(
                ["$App$", "$app$", "$Model$", "$ModelClassCamelCase$",
                 "$model$", "$ModelClass$", "$project$"],
                [app.app_name, app.app_name_lower, self.__to_camel_case(
                    app.model_name, True), self.__to_camel_case(app.model_name, True),
                 app.model_name_lower, app.model_name, self.flutter_project],
                self.__get_snippet(file_name="detail_page.txt", state_manager=True),
            ).replace()

            with open(__detail_page_file, "w", encoding="utf-8") as page:
                page.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __detailpage_parser {error}", error=True)

    def __widget_parser(self, app):
        """Method responsible for creating the widget.dart file of the app where all the widgets needed to compose
           the pages of the flutter app must be saved

         Arguments:
             app {AppModel} - AppModel class instance
        """
        try:
            __widget_file = Path(f"{app.get_path_views_dir()}/widget.dart")

            if Utils.check_file_is_locked(__widget_file):
                return

            content = ParserContent(["$ModelClass$"], [app.model_name],
                                    self.__get_snippet(f"{self.snippet_dir}widget.txt"),).replace()

            with open(__widget_file, "w", encoding="utf-8") as page:
                page.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __widget_parser {error}", error=True)

    def __build_auth_app(self):
        """Method responsible for creating the authentication app on the flutter, bringing by default authentication
           using Firebase.
        """
        try:
            __file = ""
            __data_snippet = self.__get_snippet(
                file_name="auth_data.txt", state_manager=True)
            __model_snippet = self.__get_snippet(
                file_name="auth_model.txt", state_manager=True)

            __auth_file = Path(f"{self.flutter_dir}/lib/apps/auth")
            if Utils.check_dir(__auth_file):
                return None

            os.makedirs(__auth_file)

            __data_file = Path(
                "{}/lib/apps/auth/data.dart".format(self.flutter_dir))
            __model_file = Path(
                "{}/lib/apps/auth/model.dart".format(self.flutter_dir))
            __service_file = Path(
                "{}/lib/apps/auth/service.dart".format(self.flutter_dir))

            with open(__data_file, "w", encoding="utf-8") as data_file:
                data_file.write(__data_snippet)

            with open(__model_file, "w", encoding="utf-8") as model_file:
                model_file.write(__model_snippet)

            __snippet = self.__get_snippet(
                file_name="auth_app.txt", state_manager=True)

            if self.state_manager == StateManager.Provider:
                __file = Path("{}/lib/apps/auth/provider.dart".format(self.flutter_dir))

            if self.state_manager == StateManager.MobX:
                __file = Path("{}/lib/apps/auth/controller.dart".format(self.flutter_dir))

            if self.state_manager == StateManager.Cubit:
                __snippet_cubit_state = self.__get_snippet(file_name="auth_state.txt", state_manager=True)

                __cubit_state_file = Path("{}/lib/apps/auth/state.dart".format(self.flutter_dir))

                with open(__cubit_state_file, "w", encoding="utf-8") as cubit_state_file:
                    cubit_state_file.write(__snippet_cubit_state)
                __file = Path("{}/lib/apps/auth/cubit.dart".format(self.flutter_dir))

            with open(__file, "w", encoding="utf-8") as provider_file:
                provider_file.write(__snippet)

            __service_snippet = self.__get_snippet(
                file_name="auth_service.txt", state_manager=True)

            with open(__service_file, "w", encoding="utf-8") as service_file:
                service_file.write(__service_snippet)

        except Exception as error:
            Utils.show_message(f"Error in __build_auth_app {error}", error=True)

    def __data_parser(self, app):
        """Method responsible for creating the local data persistence file on the smartphone.

        Arguments:
            app {AppModel} -- AppModel class instance
        """
        try:
            __data_file = app.get_path_data_file()
            if Utils.check_file_is_locked(__data_file):
                return

            content = ParserContent(
                ["$ModelClass$", "$modelClass$", "$project$"],
                [app.model_name, app.model_name_lower, self.flutter_project],
                self.__get_snippet(f"{self.snippet_dir}data.txt"), ).replace()

            with open(__data_file, "w", encoding="utf-8") as data_helper:
                data_helper.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __data_parser {error}", error=True)

    def __build_custom_dio(self):
        """Method responsible for creating the class that manages all access to the API's rest using the
           Dio flutter package as a base.
        """
        try:
            __dio_file = Path(f"{self.flutter_dir}/lib/utils/custom_dio.dart")

            content = ParserContent(["$project$", ], [self.flutter_project, ],
                                    self.__get_snippet(f"{self.snippet_dir}/custom_dio.txt")).replace()

            with open(__dio_file, "w", encoding="utf-8") as http_request:
                http_request.write(content)
        except Exception as error:
            Utils.show_message(f"Error in __build_custom_dio {error}", error=True)

    def __controller_parser(self, app):
        """Method responsible for creating the Model controller file

         Arguments:
             app {AppModel} - AppModel class instance
        """
        try:
            if app.model is None:
                return

            __controller_file = app.get_path_controller_file()
            if Utils.check_file_is_locked(__controller_file):
                return

            content = ParserContent(
                ["$ModelClass$", "$ModelClassCamelCase$", ],
                [app.model_name, self.__to_camel_case(app.model_name, True)],
                self.__get_snippet(file_name="controller.txt", state_manager=True)).replace()

            if not Utils.check_file(__controller_file):
                os.makedirs(__controller_file)

            with open(__controller_file, "w", encoding="utf-8") as controller_file:
                controller_file.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __controller_parser: {error}", error=True)

    def __provider_parser(self, app):
        """Method responsible for creating the Model provider file

         Args:
             app {AppModel} - AppModel class instance
        """
        try:
            if app.model is None:
                print("Informe o App")
                return
            __file = app.get_path_provider_file()

            if Utils.check_file_is_locked(__file):
                print("Arquivo travado")
                return

            content = ParserContent(
                ["$ModelClass$", "$ModelClassCamelCase$", ],
                [app.model_name, self.__to_camel_case(app.model_name, True)],
                self.__get_snippet(file_name="provider.txt", state_manager=True)).replace()

            with open(__file, "w", encoding="utf-8") as fileProvider:
                fileProvider.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __provider_parser: {error}", error=True)

    def __cubit_parser(self, app):
        """Method responsible for creating the Cubit file based on the Django App passed as a parameter

         Args:
             app {AppModel} - AppModel class instance
        """
        try:
            if app.model is None:
                print("Informe o App")
                return

            __file_cubit = app.get_path_cubit_file()
            __file_cubit_state = app.get_path_cubit_state_file()

            if Utils.check_file_is_locked(__file_cubit):
                print("Arquivo travado")
                return

            content = ParserContent(
                ["$ModelClass$", "$ModelClassCamelCase$", ],
                [app.model_name, self.__to_camel_case(app.model_name, True)],
                self.__get_snippet(file_name="cubit.txt", state_manager=True)).replace()

            with open(__file_cubit, "w", encoding="utf-8") as file_cubit:
                file_cubit.write(content)

            if Utils.check_file_is_locked(__file_cubit_state):
                print("Arquivo travado")
                return

            content = ParserContent(
                ["$ModelClass$", "$ModelClassCamelCase$", ],
                [app.model_name, self.__to_camel_case(app.model_name, True)],
                self.__get_snippet(file_name="state.txt", state_manager=True)).replace()

            with open(__file_cubit_state, "w", encoding="utf-8") as file_sate_cubit:
                file_sate_cubit.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __cubit_parser: {error}", error=True)

    def __service_parser(self, app):
        """Method responsible for creating the Django App class of service passed by parameter

        Arguments:
            app {AppModel} -- AppModel class instance
        """
        try:
            if app.model is None:
                return

            __service_file = app.get_path_service_file()
            if Utils.check_file_is_locked(__service_file):
                return

            content = ParserContent(
                ["$ModelClass$", "$App$", "$Model$",
                 "$ModelClassCamelCase$", "$project$", ],
                [app.model_name, app.app_name_lower, app.model_name_lower,
                 self.__to_camel_case(app.model_name, True), self.flutter_project],
                self.__get_snippet(file_name="service.txt", state_manager=True)).replace()

            if not Utils.check_file(__service_file):
                os.makedirs(__service_file)

            with open(__service_file, "w", encoding="utf-8") as service_file:
                service_file.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __service_parser: {error}", error=True)

    def __model_parser(self, app):
        """Method responsible for creating the model class based on the Django App passed by parameter.
        """
        try:
            if app.model is None:
                return

            content = self.__get_snippet(f"{self.snippet_dir}model.txt")
            content_attributes = ""
            content_string_return = ""
            content_from_json = ""
            content_to_map = ""
            content_constructor = ""

            __model_file = app.get_path_model_file()

            if Utils.check_file_is_locked(__model_file):
                return

            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split(".")
                __name_dart = self.__to_camel_case(__name)

                if __name_dart in [f"id{app.model_name_lower}", "id"]:
                    continue

                field_type = (
                    str(str(type(field)).split(".")[-1:])
                    .replace('["', "")
                    .replace("'>\"]", ""))
                attribute = self._tipos_flutter[self._tipos_originais.index(
                    field_type)]

                content_attributes += "{} {};\n  ".format(attribute, __name_dart)
                content_string_return += "{}: ${}\\n".format(__name_dart.upper(), __name_dart)

                content_constructor += "this.{},\n".format(__name_dart)

                if str(attribute) == "DateTime":
                    content_from_json += "{} = Util.convertDate(json['{}']) == null".format(__name_dart, __name)
                    content_from_json += "? null:  Util.convertDate(json['{}']);\n".format(__name, " " * 8)
                elif str(attribute) == "double":
                    content_from_json += "{} = json['{}'] == null".format(__name_dart, __name)
                    content_from_json += "? null : double.parse(json['{}']) ;\n{}".format(__name, " " * 8)
                elif str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_from_json += "{1} = json['{2}'] == null ? true : json['{2}'] ;\n{0}".format(
                            " " * 8, __name_dart, __name)
                    elif __name_dart.lower() == "deleted":
                        content_from_json += "{1} = json['{2}'] == null ? false : json['{2}'];\n{0}".format(
                            " " * 8, __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] == null ? true : json['{2}'];\n{0}".format(
                            " " * 8, __name_dart, __name)
                else:
                    if __name_dart.startswith("fk"):
                        content_from_json += "{1} = json['{2}'] == null ? \"\" : json['{2}'];\n{0}".format(
                            " " * 8, __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] == null ? \"\" : json['{2}'];\n{0}".format(
                            " " * 8, __name_dart, __name)

                if str(field_type) == "DateTimeField":
                    if __name_dart in ("createdOn", "updatedOn"):
                        content_to_map += "'{0}': this.{1}.toString(),\n{2}".format(__name, __name_dart, " " * 8)
                    else:
                        content_to_map += "'{}': this.{} != null? Util.stringDateTimeSplit".format(__name, __name_dart)
                        content_to_map += "(this.{}, returnType: \"dt\"): null, \n".format(__name_dart)
                    continue
                if str(field_type) == "DateField":
                    content_to_map += "'{}': this.{} != null ?Util.stringDateTimeSplit".format(__name, __name_dart)
                    content_to_map += "(this.{}, returnType: \"d\"): null, \n".format(__name_dart)
                    continue
                if str(field_type) == "TimeField":
                    content_to_map += "'{}': this.{} != null ?Util.stringDateTimeSplit".format(__name, __name_dart)
                    content_to_map += "(this.{}, returnType: \"t\"): null, \n".format(__name_dart)
                    continue
                if str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_to_map += "'{0}': this.{1} != null? this.{1}: true,\n{2}".format(
                            __name, __name_dart, " " * 8)
                    elif __name_dart.lower() == "deleted":
                        content_to_map += "'{0}': this.{1} != null? this.{1}: false,\n{2}".format(
                            __name, __name_dart, " " * 8)
                    else:
                        content_to_map += "'{0}': this.{1} != null? this.{1}: true,\n{2}".format(
                            __name, __name_dart, " " * 8)
                    continue
                content_to_map += "'{0}': this.{1} != null? this.{1}: \"\",\n{2}".format(__name, __name_dart, " " * 8)

            content = ParserContent(
                ["$ModelClass$", "$AttributeClass$", "$StringReturn$", "$Model$", "$ParserfromMap$", "$ParserToMap$",
                 "$project$", "$ConstructorModelClass$", ],
                [app.model_name, content_attributes, content_string_return, app.model_name_lower, content_from_json,
                 content_to_map, self.flutter_project, content_constructor],
                content).replace()

            if not Utils.check_file(__model_file):
                os.makedirs(__model_file)

            with open(__model_file, "w", encoding="utf-8") as model_file:
                model_file.write(content)

        except Exception as error:
            Utils.show_message(f"Error in __parser_model: {error}", error=True)

    def __build_mobx(self):
        """Method to be executed when the project was created using MobX as state management,
           which executes the build_runner command to generate the xpto.g.dart files
        """
        try:
            if self.state_manager_provider:
                return
            if Utils.check_dir(self.flutter_dir):
                current_path = os.getcwd()
                os.chdir(self.flutter_dir)
                subprocess.run("flutter pub run build_runner build", shell=True)
                os.chdir(current_path)
                time.sleep(3)
        except Exception as error:
            Utils.show_message(f"Error in __build_mobx: {error}", error=True)

    def __build_settings_controller(self):
        """Method responsible for creating the flutter application configuration app, bringing standard
           methods to control the theme of the App.
        """
        try:
            if not Utils.check_dir(self.app_configuration):
                os.makedirs(self.app_configuration)

                _content_page = self.__get_snippet(
                    file_name="settings_page.txt", state_manager=True)
                _content_controller = self.__get_snippet(
                    file_name="settings.txt", state_manager=True)
                if self.state_manager == StateManager.Provider:
                    with open(
                            self.app_configuration_profile_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(_content_controller)
                elif self.state_manager == StateManager.MobX:
                    with open(self.app_configuration_controller_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(_content_controller)
                elif self.state_manager == StateManager.Cubit:
                    with open(
                            self.app_configuration_cubit_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(_content_controller)
                    with open(self.app_configuration_cubit_state_file, 'w', encoding='utf-8') as arquivo:
                        __content = self.__get_snippet(
                            file_name="settings_state.txt", state_manager=True)
                        arquivo.write(__content)

                with open(
                        self.app_configuration_page_file, "w", encoding="utf-8") as arquivo:
                    arquivo.write(_content_page)

        except Exception as error:
            Utils.show_message(f"Error in __build_settings_controller: {error}", error=True)

    def __get_yaml_file(self):
        """Method responsible for retrieving the snippet from the pubspec.yaml file"""
        try:
            return Path(f"{self.flutter_dir}/pubspec.yaml")
        except Exception as error:
            Utils.show_message(f"Error in __get_yaml_file:{error}", error=True)

    def __add_packages(self):
        """Method responsible for adding the packages (dependencies) of the flutter project according to the chosen
           state management.
        """
        try:
            __path = self.__get_yaml_file()

            snippet = ParserContent(
                ["$AppPackage$", "$AppDescription$"],
                [self.project.lower(),
                 f"Projeto Flutter do sistema Django {self.project}"],
                self.__get_snippet(file_name="yaml.txt", state_manager=True)).replace()

            with open(__path, "w", encoding="utf-8") as yaml_file:
                yaml_file.write(snippet)

        except Exception as error:
            Utils.show_message(f"Error in __add_packages: {error}", error=True)

    def __build_utils(self):
        """Method responsible for creating the utils package containing constants, and general methods used by
           the project's apps
        """
        try:
            if not Utils.check_dir(self.utils_dir):
                os.makedirs(self.utils_dir)

            __config_snippet = self.__get_snippet(f"{self.snippet_dir}config.txt")

            __util_snippet = self.__get_snippet(f"{self.snippet_dir}util.txt")

            __controller_snippet = self.__get_snippet(file_name="process.txt", state_manager=True)

            if Utils.check_file(self.config_file) is False:
                __config_snippet = ParserContent(["$AppName$", "$DjangoAPIPath$"],
                                                 [SYSTEM_NAME, API_PATH], __config_snippet).replace()
                with open(self.config_file, "w", encoding="utf-8") as config:
                    config.write(__config_snippet)
            else:
                if Utils.check_file_is_locked(self.config_file) is False:
                    __config_snippet = ParserContent(["$AppName$", "$DjangoAPIPath$"],
                                                     [SYSTEM_NAME, API_PATH], __config_snippet).replace()
                    with open(self.config_file, "w", encoding="utf-8") as config:
                        config.write(__config_snippet)

            if Utils.check_file(self.util_file) is False:
                with open(self.util_file, "w", encoding="utf-8") as config:
                    config.write(__util_snippet)
            else:
                if Utils.check_file_is_locked(self.util_file) is False:
                    with open(self.util_file, "w", encoding="utf-8") as config:
                        config.write(__util_snippet)

            if self.state_manager == StateManager.Provider:
                if Utils.check_file(self.process_provider_file) is False:
                    with open(
                            self.process_provider_file, "w", encoding="utf-8") as process_provider:
                        process_provider.write(__controller_snippet)
                else:
                    if Utils.check_file_is_locked(self.process_provider_file) is False:
                        with open(
                                self.process_provider_file, "w", encoding="utf-8") as process_provider:
                            process_provider.write(__controller_snippet)
            elif self.state_manager == StateManager.MobX:
                if Utils.check_file(self.process_controller_file) is False:
                    with open(
                            self.process_controller_file, "w", encoding="utf-8") as process_controller:
                        process_controller.write(__controller_snippet)
                else:
                    if Utils.check_file_is_locked(self.process_controller_file) is False:
                        with open(self.process_controller_file, "w", encoding="utf-8") as process_controller:
                            process_controller.write(__controller_snippet)
            elif self.state_manager == StateManager.Cubit:
                pass

        except Exception as error:
            Utils.show_message(f"Error in __build_utils {error}", error=True)

    def __build_user_interface(self):
        """Method responsible for creating the package containing the project's font settings and also the
           general app widgets
        """
        try:
            if not Utils.check_dir(self.ui_dir):
                os.makedirs(self.ui_dir)

            for arquivo in ["widget", "font"]:
                __path = Path(f"{self.ui_dir}{arquivo}.dart")
                if arquivo == "font":
                    __snippet = self.__get_snippet(Path(f"{self.snippet_dir}ui_{arquivo}.txt"))
                else:
                    __snippet = self.__get_snippet(file_name="ui_widget.txt", state_manager=True)
                if Utils.check_file(__path) is False:
                    with open(__path, "w", encoding="utf-8") as arq:
                        arq.write(__snippet)
                else:
                    if Utils.check_file_is_locked(__path) is False:
                        with open(__path, "w", encoding="utf-8") as arq:
                            arq.write(__snippet)

        except Exception as error:
            Utils.show_message(f"Error in __build_user_interface: {error}", error=True)

    def __create_source_from_model(self):
        """Method for creating apps when App and Model are informed
        """
        Utils.show_message("Criando as apps baseado na App e no Model")
        try:
            self.__create_source(self.current_app_model.app_name, self.current_app_model.model_name)
        except Exception as error:
            Utils.show_message(f"Error in __create_source_from_model: {error}", error=True)

    def __create_source_from_generators(self):
        """Method for creating apps when only the App is informed
        """
        Utils.show_message("Criando as apps baseado na App e nos Generators")
        try:
            for model in self.current_app_model.models:
                self.__create_source(self.current_app_model.app_name, model[1])
        except Exception as error:
            Utils.show_message(
                f"Error in __create_source_from_generators: {error}", error=True)

    def __create_source(self, app_name, model_name):
        """Method responsible for creating the directory structure based on Django's App / Models
        """
        try:
            if app_name is None:
                Utils.show_message("É necessário passar a App")
                return

            if model_name is None:
                Utils.show_message(f"É necessário passar o Model")
                return

            __source_class = AppModel(self.flutter_dir, app_name, model_name)
            __app_name = __source_class.app_name
            __model_name = __source_class.model_name
            __model = __source_class.model
            __model_dir = __source_class.get_path_app_model_dir()
            __views_dir = __source_class.get_path_views_dir()
            __data_file = __source_class.get_path_data_file()
            __model_file = __source_class.get_path_model_file()
            __service_file = __source_class.get_path_service_file()
            __controller_file = __source_class.get_path_controller_file()
            __provider_file = __source_class.get_path_provider_file()
            __cubit_file = __source_class.get_path_cubit_file()
            __cubit_state_file = __source_class.get_path_cubit_state_file()
            __views = __source_class.get_path_files_views()

            if not Utils.check_dir(__model_dir):
                Utils.show_message(f"Criando diretório source do {__app_name}.{__model_name}")
                os.makedirs(__model_dir)

            if not Utils.check_dir(__views_dir):
                os.makedirs(__views_dir)

                if __views is not None:
                    with open(__views[0], "w", encoding="utf-8") as pagina:
                        pagina.write(f"// Create Page {__app_name} {__model_name}")

                    with open(__views[1], "w", encoding="utf-8") as pagina:
                        pagina.write(f"// Detail Page {__app_name} {__model_name}")

                    with open(__views[2], "w", encoding="utf-8") as pagina:
                        pagina.write(f"// Index Page {__app_name} {__model_name}")

                    with open(__views[3], "w", encoding="utf-8") as pagina:
                        pagina.write(f"// List Page {__app_name} {__model_name}")

                    with open(__views[4], "w", encoding="utf-8") as pagina:
                        pagina.write(f"// Update Page {__app_name} {__model_name}")

            if not Utils.check_file(__model_file):
                with open(__model_file, "w", encoding="utf-8") as arquivo:
                    arquivo.write(f"// Modelo do {__model_name}")

            if not Utils.check_file(__data_file):
                with open(__data_file, "w", encoding="utf-8") as arquivo:
                    arquivo.write(f"// Persistência do {__model_name}")

            if not Utils.check_file(__service_file):
                with open(__service_file, "w", encoding="utf-8") as arquivo:
                    arquivo.write(f"// Service do {__model_name}")

            if self.state_manager == StateManager.Provider:
                if not Utils.check_file(__provider_file):
                    with open(__provider_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(f"// Provider do {__model_name}")

            if self.state_manager == StateManager.MobX:
                if not Utils.check_file(__controller_file):
                    with open(__controller_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(f"// Controller do {__model_name}")

            if self.state_manager == StateManager.Cubit:
                if not Utils.check_file(__cubit_file):
                    with open(__cubit_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(f"// Cubit do {__model_name}")
                if not Utils.check_file(__cubit_state_file):
                    with open(__cubit_state_file, "w", encoding="utf-8") as arquivo:
                        arquivo.write(f"// State Cubit do {__model_name}")

            self.__create_update_page_parser(__source_class)
            self.__detailpage_parser(__source_class)
            self.__indexpage_parser(__source_class)
            self.__listpage_parser(__source_class)
            self.__widget_parser(__source_class)
            self.__create_update_page_parser(__source_class, False)
            self.__model_parser(__source_class)
            self.__data_parser(__source_class)
            self.__service_parser(__source_class)

            if self.state_manager == StateManager.Provider:
                self.__provider_parser(__source_class)
            if self.state_manager == StateManager.MobX:
                self.__controller_parser(__source_class)
            if self.state_manager == StateManager.Cubit:
                self.__cubit_parser(__source_class)

        except Exception as error:
            Utils.show_message(f"Error in __create_source: {error}", error=True)

    def _build_internationalization(self):
        """Method responsible for configuring the internationalization package in the project
        """
        try:
            snippet = self.__get_snippet(f"{self.snippet_dir}localization.txt")

            path_localization = os.path.join(
                self.utils_dir, "localization.dart")

            if Utils.check_file_is_locked(path_localization):
                return

            with open(path_localization, "w", encoding="utf-8") as localizations:
                localizations.write(snippet)

            __lang_dir = Path(f"{self.flutter_dir}/lang")
            __pt_br = Path(f"{self.flutter_dir}/lang/pt.json")
            __en_us = Path(f"{self.flutter_dir}/lang/en.json")

            if not Utils.check_dir(__lang_dir):
                os.makedirs(__lang_dir)

            if not Utils.check_file(__pt_br):
                snippet = self.__get_snippet(f"{self.snippet_dir}pt_language.txt")
                with open(__pt_br, "w", encoding="utf-8") as pt_json:
                    pt_json.write(snippet)

            if not Utils.check_file(__en_us):
                snippet = self.__get_snippet(f"{self.snippet_dir}en_language.txt")
                with open(__en_us, "w", encoding="utf-8") as en_json:
                    en_json.write(snippet)

        except Exception as error:
            Utils.show_message(f"Error in _build_internationalization: {error}", error=True)

    def __replace_main(self):
        """Method responsible for updating the main.dart file according to the chosen state management
        """
        __imports = ""
        __list_itens = []
        try:
            snippet = self.__get_snippet(file_name="main.txt", state_manager=True)

            path_main_dart = Path(f"{self.flutter_dir}/lib/main.dart")
            if Utils.check_file_is_locked(path_main_dart):
                return

            (__import_views, __import_controllers, __register_controller,
             __views,) = self.__mapping_all_application()

            __import_controllers += f"import 'apps/configuracao/model.dart';"
            __import_views += f"import 'apps/configuracao/index.page.dart';\n"
            __register_controller += (
                "getIt.registerSingleton<SettingsController>(SettingsController());")

            if __import_views is None or __import_controllers is None:
                return

            snippet = snippet.replace("$project$", self.flutter_project)
            if self.state_manager == StateManager.Provider:
                __import, __register = self.__register_provider()
                snippet = snippet.replace("$ImportProvider$", __import)
                snippet = snippet.replace("$RegisterProviders$", __register)
            if self.state_manager == StateManager.MobX:
                snippet = snippet.replace("$ImportViews$", __import_views)
                snippet = snippet.replace("$RegisterControllers$", __register_controller)
                snippet = snippet.replace("$ImportController$", __import_controllers)
            if self.state_manager == StateManager.Cubit:
                __import_controllers += f"import 'apps/configuracao/cubit.dart';"
                __import, __register = self.__register_cubit()
                snippet = snippet.replace("$ImportController$", __import_controllers)
                snippet = snippet.replace("$ImportCubit$", __import)
                snippet = snippet.replace("$RegisterProviders$", __register)

            snippet = snippet.replace("$Listviews$", __views)

            with open(path_main_dart, "w", encoding="utf-8") as main_dart:
                main_dart.write(snippet)

            path_homepage = Path(f"{self.flutter_dir}/lib/home.page.dart")
            if Utils.check_file_is_locked(path_homepage):
                return
            __snippet_page = self.__get_snippet(
                file_name="home.page.txt", state_manager=True)
            __menu_home_page_itens = self.__build_menu_home_page_itens()

            if self.state_manager == StateManager.Provider or self.state_manager == StateManager.Cubit:
                __snippet_page = __snippet_page.replace("$ImportViews$", __import_views)
                __snippet_page = __snippet_page.replace("$ItenMenu$", __menu_home_page_itens)

                with open(path_homepage, "w", encoding="utf-8") as home_page_dart:
                    home_page_dart.write(__snippet_page)

        except Exception as error:
            Utils.show_message(f"Error in __replace_main: {error}", error=True)

    def call_methods(self, options):
        """Method that identifies which command was requested by the user to be executed, before calling the method,
           the inputs informed by the user are validated, thus avoiding program execution errors due to the absence of
           mandatory parameters
        """
        if options["init_provider"] is False and options["init_mobx"] is False and options["init_cubit"] is False:
            Utils.show_message("É obrigatório informar o state manager que será utilizado no projeto Flutter",
                               error=True)
        if options["init_provider"]:
            self.state_manager = StateManager.Provider
        elif options["init_mobx"]:
            self.state_manager = StateManager.MobX
        elif options["init_cubit"]:
            self.state_manager = StateManager.Cubit
        else:
            sys.exit()

        if options["main"]:
            self.__replace_main()
            return
        elif options["yaml"]:
            self.__add_packages()
            return
        elif options["build_mobx"] and self.state_manager == StateManager.MobX:
            self.__build_mobx()
            return
        elif options["clear"]:
            self.__clear_project()
            sys.exit()

        elif options["init_provider"] or options["init_mobx"] or options["init_cubit"]:
            self.__init_flutter()
            self.__build_settings_controller()
            self.__build_utils()
            self.__build_user_interface()
            self.__build_custom_dio()
            self._build_internationalization()
            self.__build_auth_app()
            # self.__build_flutter()
        else:
            Utils.show_message(
                "É necessário passar pelo menos um dos parâmetros a seguir: --init_provider, --init_mobx, --init_cubit,"
                " --main, --yaml, --build_mobx",
                error=True, )

    def handle(self, *args, **options):

        app = options["App"] or None
        model = options["Model"] or None

        if app is None and model is None and FLUTTER_APPS == []:
            Utils.show_message(
                f"Você não configurou o FLUTTER_APPS no settings e também não informou uma APP para ser gerada.",
                error=True)
            return

        if app and model:
            if Utils.contain_number(app) or Utils.contain_number(model):
                Utils.show_message(f"Nome da app ou do model contendo números")
                return

            self.current_app_model = AppModel(self.flutter_project, app, model)
            self.call_methods(options)

        if app and model is None:
            if Utils.contain_number(app):
                Utils.show_message(f"Nome da app contendo números", error=True)
                return

            self.current_app_model = AppModel(self.flutter_project, app)
            self.call_methods(options)

        if not FLUTTER_APPS:
            Utils.show_message("Não foram informadas as APPS a serem mapeadas", error=True)
            return
        else:
            self.call_methods(options)
            for __app in FLUTTER_APPS:
                self.current_app_model = AppModel(self.flutter_project, __app)
                self.__create_source_from_generators()
            self.__build_mobx()

    def __clear_project(self, path=None):
        try:
            __path = path or f"{self.flutter_dir}"
            import shutil

            shutil.rmtree(__path)
        except Exception as error:
            Utils.show_message(f"Error in __clear_project: {error}")
