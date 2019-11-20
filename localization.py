import json
from glob import glob

enabled_locales = [
    "en-US",  # English (United States)
    "pt-BR",  # Portuguese (Brazil)
    "pt-BR2",  # Portuguese (Brazil, informal version)
]


def cache_localizations(files):
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        pname = file.split("/")[-1][:-5]
        lname = file.split("/")[1]
        dic = json.load(open(file))
        ldict[lname].update({pname: dic})
    return ldict


jsons = []

for locale in enabled_locales:
    jsons += glob("locales/%s/*.json" % locale)

langdict = cache_localizations(jsons)


class GetLang:
    def __init__(self, msg, pname):
        # try to get user lang from language_code, if it does not exist, use en-US
        self.lang = msg.from_user.language_code or "en-US"
        # User has a language_code without hyphen
        if len(self.lang.split("-")) == 1:
            # Try to find a language that starts with the provided language_code
            for locale_ in enabled_locales:
                if locale_.startswith(self.lang):
                    self.lang = locale_
        if self.lang.split("-")[1].islower():
            self.lang = self.lang.split("-")
            self.lang[1] = self.lang[1].upper()
            self.lang = "-".join(self.lang)
        self.lang = self.lang if self.lang in enabled_locales else "en-US"

        self.dic = langdict.get(self.lang) or langdict["en-US"]
        self.dic = self.dic.get(pname) or langdict["en-US"][pname]

    def strs(self, string):
        return self.dic.get(string, string)
