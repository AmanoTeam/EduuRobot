import gettext


def get_lang(msg, domain):
    #chat = msg.chat.id
    ## TODO: query db to get chat lang
    lang = gettext.translation(domain, localedir='locales', languages=['pt-BR'])
    return lang.gettext
