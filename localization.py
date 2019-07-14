import gettext
import subprocess
from glob import glob

enabled_locales = [
                    "en-US",    # English (United States)
                    "pt-BR"     # Portuguese (Brazil)
                  ]


def compile_localizations(files):
    print("Compiling languages... ", end="", flush=True)
    for file in files:
        subprocess.call(["msgfmt", file, "-o", file[:-3] + ".mo"])
    print("Done")

pofiles = glob("locales/*/LC_MESSAGES/*.po")
mofiles = glob("locales/*/LC_MESSAGES/*.mo")


if len(pofiles) != len(mofiles):
    compile_localizations(pofiles)


def get_lang(msg, domain):
    #chat = msg.chat.id
    ## TODO: query db to get chat lang
    lang = gettext.translation(domain, localedir='locales', languages=['pt-BR'])
    return lang.gettext
