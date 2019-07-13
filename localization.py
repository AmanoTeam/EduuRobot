import gettext
import sys


def get_lang(msg, domain):
    lang = gettext.translation(domain, localedir='locales', languages=['pt-BR'])
    return lang.gettext
