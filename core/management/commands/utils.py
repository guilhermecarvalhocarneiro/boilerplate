import logging
import os
import sys

from django.contrib.contenttypes.models import ContentType


class Utils(object):
    @staticmethod
    def show_message(text: str, error: bool = False):
        __log = logging.getLogger('logger')
        __log.setLevel(logging.INFO)
        """Method do show message in console"""
        """Method for displaying friendly messages on the flow of script execution on the terminal.

        Arguments:
            message {str} -- Message to be displayed on the terminal
            error {bool} -- Attribute that determines whether the message is an error,
                            being an error message the execution of the program is ended
        """
        try:
            if error:
                __log.error(f"\n{'!=' * len(text)}\nERROR: {text.upper()}\n")
                sys.exit()
            else:
                __log.warning(text)
        except Exception as error:
            logging.error(error)

    @staticmethod
    def contain_number(text: str) -> bool:
        """Method to check the text passed as a parameter has numeric characters

        Arguments:
            text {String} -- Text to be validated

        Returns:
            bool -- True if there is any number in the text parameter
        """
        try:
            return any(character.isdigit() for character in text)
        except Exception as error:
            Utils.show_message(f"Error in __contain_number: {error}", error=True)
            return False

    @staticmethod
    def get_verbose_name(apps, app_name: str = None, model_name: str = None) -> str:
        """Method get verbose name class

        Arguments:
            app_name String -- App Name lower()
            model_name String -- Model Name lower()

        Returns:
            String -- Verbose name model
        """
        try:
            if app_name is not None and model_name is not None:
                _model = ContentType.objects.get(
                    app_label=app_name.lower(), model=model_name.lower())
                return _model.model_class()._meta.verbose_name.title()
            if app_name is not None and model_name is None:
                __app_config = apps.get_app_config(app_name.lower())
                return __app_config.verbose_name.title() or app_name
        except Exception as error:
            if str(error).find("ContentType matching query does not exist") == -1:
                Utils.show_message(f"Error in Utils.get_verbose_name: {error}")
            return model_name.title() or app_name.title()

    @staticmethod
    def check_dir(path: str) -> bool:
        """Method to check if the directory exists

        Arguments:
            path {str} -- Directory path

        Returns:
            bool -- True if the directory exists and False if not.
        """
        __process_result = False
        try:
            __process_result = os.path.isdir(path)
        except Exception as error:
            Utils.show_message(f"Error in Utils.check_dir: {error}", error=True)
        finally:
            return __process_result

    @staticmethod
    def check_file(path: str) -> bool:
        """Method to check if the file passed as a parameter exists

         Arguments:
             path {str} - Path to the file

         Returns:
             bool - True if the file exists and False if not.
        """
        __process_result = False
        try:
            __process_result = os.path.isfile(path)
        except Exception as error:
            Utils.show_message(f"Error in Utils.check_file: {error}", error=True)
        finally:
            return __process_result

    @staticmethod
    def check_content(path: str, text: str) -> bool:
        """Method to check if the text exists within the file

         Arguments:
             path {str} - Absolute path to the file to be analyzed
             text {str} - Text to be searched within the given file

         Returns:
             bool - True if the content is found and False if not.
        """
        __process_result = False
        try:
            if Utils.check_file(path):
                with open(path) as content_file:
                    content = content_file.read()
                    __process_result = text in content
        except Exception as error:
            Utils.show_message(f"Error in Utils.check_content: {error}", error=True)
        finally:
            return __process_result

    @staticmethod
    def check_file_is_locked(path: str) -> bool:
        """ Method to check if the file is locked
         thus preventing it from being parsed again

         Arguments:
             path {str} - Absolute path to the file to be analyzed

         Returns:
             bool - True if it contains the word #FileLocked
        """
        __process_result = False
        try:
            if Utils.check_file(path):
                with open(path, encoding='utf-8') as file:
                    content = file.read()
                    __process_result = "#FileLocked" in content
        except Exception as error:
            Utils.show_message(f"Error in Utils.check_file: {error}", error=True)
        finally:
            return __process_result

    @staticmethod
    def get_snippet(path: str) -> str:
        """Method to retrieve the value of the snippet file to be converted by merging with the values based on models
           from the Django project

        Arguments:
            path {str} - Absolute path to the optional file,
                         must be passed when the snippet path is in the same flutter directory

        Returns:
            str -- Text to be used to interpolate model data
        """
        __content = ""
        try:
            if Utils.check_file(path):
                with open(path, 'r', encoding='utf-8') as file:
                    __content = file.read()
        except Exception as error:
            Utils.show_message(f"Error in Utils.check_file: {error}", error=True)
        finally:
            return __content

    # @staticmethod
    # def XPTO(path):
    #     __process_result = False
    #     try:
    #         if Utils.check_file(path):
    #             pass
    #         Utils.show_message("Arquivo não encontrado para análise")
    #     except Exception as error:
    #         Utils.show_message(f"Error in Utils.check_file: {error}", error=True)
    #     finally:
    #         return __process_result
