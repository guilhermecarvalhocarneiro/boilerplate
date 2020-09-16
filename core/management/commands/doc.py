"""Manager to generate project documentation for the development team using the Sphinx package
"""

import os
from django.core.management.base import BaseCommand
from core.management.commands.utils import Utils
from nuvols.core.settings import DOC_APPS


class Command(BaseCommand):
    help = """Manager responsible for generating documentation for the development team"""

    def __init__(self):
        super().__init__()
        self.projeto = None
        self.desenvolvedor = None
        self.path_root = os.getcwd()
        self.__docs_path = f"{self.path_root}/doc"

    def add_arguments(self, parser):
        parser.add_argument('projeto', type=str)
        parser.add_argument('desenvolvedor', type=str)

    @staticmethod
    def __title(string) -> str:
        try:
            string = string.replace('_', ' ').title()
        finally:
            return string

    def __parser_documentation(self):
        try:
            self.path_core = os.path.join(self.path_root, "nuvols/core")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/config.txt"))

            content = content.replace("$project$", self.projeto.lower())
            content = content.replace("$Project$", self.__title(self.projeto))
            content = content.replace("$Desenvolvedor$", self.desenvolvedor)

            with open(f"{self.__docs_path}/source/conf.py", 'w') as arquivo:
                arquivo.write(content)

            __make_content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make.txt"))

            with open(f"{self.__docs_path}/Makefile", 'w') as arquivo:
                arquivo.write(__make_content)

            __make_bat_content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make_bat.txt"))

            with open(f"{self.__docs_path}/make.bat", 'w') as arquivo:
                arquivo.write(__make_bat_content)

            __modules_content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/modules.txt"))

            __module_apps = ''
            for __app in DOC_APPS:
                __module_apps += f"   {__app}\n"

            __modules_content = __modules_content.replace("$App$", self.__title(self.projeto))
            __modules_content = __modules_content.replace("$Modules$", __module_apps)

            with open(f"{self.__docs_path}/source/modules.rst", 'w') as arquivo:
                arquivo.write(__modules_content)

            __rst_content = Utils.get_snippet(
                os.path.join(self.path_core,
                             "management/commands/snippets/sphinx_doc/index_rst.txt")
            )

            with open(f"{self.__docs_path}/source/index.rst", "w") as arquivo:
                arquivo.write(__rst_content)

            for app in DOC_APPS:
                __content = Utils.get_snippet(
                    os.path.join(self.path_core, "management/commands/snippets/sphinx_doc/rst.txt")
                )
                __content = __content.replace("$App$", app.title())
                __content = __content.replace("$app$", app)

                with open(f"{self.__docs_path}/source/{app.lower()}.rst", "w") as arquivo:
                    arquivo.write(__content)

            os.system("make --directory=doc html")

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                               "docker-compose.yml sofreu alguma alteração: "
                               "{}".format(e))

    def handle(self, *args, **options):
        if not DOC_APPS:
            Utils.show_message("É obrigatório a configuração no settings do projeto das DOC_APPS")
            return

        self.projeto = options['projeto'] or None
        self.desenvolvedor = options['desenvolvedor'] or None
        __path = self.path_root

        if self.projeto is not None and self.desenvolvedor is not None:
            try:
                os.makedirs(self.__docs_path)
                os.makedirs(f"{self.__docs_path}/build")
                os.makedirs(f"{self.__docs_path}/source")
                os.makedirs(f"{self.__docs_path}/source/_templates")
                os.makedirs(f"{self.__docs_path}/source/_static")
            except Exception as error:
                Utils.show_message(f"Error in handle: {error}")
                pass
            
            self.__parser_documentation()
