import sys

from colorama import Fore, Style
from colorama import init as colorama_init

class LogMeta(type):
    def __init__(cls, name, bases, dct):
        super(LogMeta, cls).__init__(name, bases, dct)
        colorama_init()

class Log(object):
    __metaclass__ = LogMeta

    colors = Fore

    @staticmethod
    def println(namespace, string, color=Fore.MAGENTA):
        """
        Prints string tagged with a namespace with some colors
        Args:
            namespace: A string stating what part of the app is logging this
            string: The string to print
        Kwargs:
            color: The color to make the namespace tag (Log.colors)
        """
        print("[{}{}{}] {}".format(color, namespace, Fore.RESET, string))

    @staticmethod
    def error(namespace, string, color=Fore.MAGENTA):
        """
        Prints string to stderr tagged with a namespace with some colors
        Args:
            namespace: A string stating what part of the app is logging this
            string: The string to print
        Kwargs:
            color: The color to make the namespace tag (Log.colors)
        """
        sys.stderr.write("[{}{}{}:{}ERROR{}] {}\n".format(color, namespace, Fore.RESET, Fore.RED, Fore.RESET, string))

    @staticmethod
    def write(namespace, string, color=Fore.MAGENTA):
        """
        Prints string with no newline tagged with a namespace with some colors
        Args:
            namespace: A string stating what part of the app is logging this
            string: The string to print
        Kwargs:
            color: The color to make the namespace tag (Log.colors)
        """
        sys.stdout.write("[{}{}{}] {}".format(color, namespace, Fore.RESET, string))
