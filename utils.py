# Copyright (C) 2018-2019 Amano Team <contact@amanoteam.ml>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import html
import aiohttp
import time
import zipfile
from aiohttp.client_exceptions import ContentTypeError

languages = {"ada": "39",
             "bash": "38",
             "brainfuck": "44",
             "c(clang)": "26",
             "c(gcc)": "6",
             "c(vc)": "29",
             "c#": "1",
             "c++ (clang)": "27",
             "c++ (gcc)": "7",
             "c++ (vc++)": "28",
             "d": "30",
             "elixir": "41",
             "erlang": "40",
             "f#": "3",
             "fortran": "45",
             "go": "20",
             "haskell": "11",
             "java": "4",
             "javascript": "17",
             "kotlin": "43",
             "lisp": "18",
             "lua": "14",
             "mysql": "33",
             "nasm": "15",
             "node.js": "23",
             "objective-c": "10",
             "ocaml": "42",
             "octave": "25",
             "oracle": "35",
             "pascal": "9",
             "perl": "13",
             "php": "8",
             "postgresql": "34",
             "prolog": "19",
             "python": "24",
             "python2": "5",
             "python3": "24",
             "py3": "24",
             "py2": "5",
             "r": "31",
             "ruby": "12",
             "scala": "21",
             "scheme": "22",
             "sql server": "16",
             "swift": "37",
             "tcl": "32",
             "vb.net": "2"}

compiler_args = {
    "c++ (gcc)": "-Wall -std=c++14 -O2 -o a.out source_file.cpp",
    "c++ (clang)": "-Wall -std=c++14 -stdlib=libc++ -O2 -o a.out source_file.cpp",
    "c++ (vc++)": "source_file.cpp -o a.exe /EHsc /MD /I C:\\boost_1_60_0 /link /LIBPATH:C:\\boost_1_60_0\\stage\\lib",
    "c (gcc)": "-Wall -std=gnu99 -O2 -o a.out source_file.c",
    "c (clang)": "-Wall -std=gnu99 -O2 -o a.out source_file.c",
    "c (vc)": "source_file.c -o a.exe",
    "d": "source_file.d -ofa.out",
    "go": "-o a.out source_file.go",
    "haskell": "-o a.out source_file.hs",
    "objective-c": "-MMD -MP -DGNUSTEP -DGNUSTEP_BASE_LIBRARY=1 -DGNU_GUI_LIBRARY=1 -DGNU_RUNTIME=1 -DGNUSTEP_BASE_LIBRARY=1 -fno-strict-aliasing -fexceptions -fobjc-exceptions -D_NATIVE_OBJC_EXCEPTIONS -pthread -fPIC -Wall -DGSWARN -DGSDIAGNOSE -Wno-import -g -O2 -fgnu-runtime -fconstant-string-class=NSConstantString -I. -I /usr/include/GNUstep -I/usr/include/GNUstep -o a.out source_file.m -lobjc -lgnustep-base"
}

# aio rextester forked from https://github.com/nitanmarcel/rextester_py/blob/master/rextester_py/rextester_aio.py
async def __fetch(session, url, data):
    async with session.get(url, data=data) as response:
        return await response.json()


async def rexec_aio(lang, code, stdin=None):
    data = {
        "LanguageChoice": languages.get(
            lang.lower()),
        "Program": code,
        "Input": stdin,
        "CompilerArgs": compiler_args.get(
            lang.lower())}

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        response = await __fetch(session, "https://rextester.com/rundotnet/api", data)
        return RextesterResult(response.get("Result"),
                               response.get("Warnings"),
                               response.get("Errors"),
                               response.get("Stats"),
                               response.get("Files"))
    
class RextesterResult(object):
    def __init__(self, results, warnings, errors, stats, files):
        self.results = results
        self.warnings = warnings
        self.errors = errors
        self.stats = stats
        self.files = files
        
async def send_to_dogbin(text):
    if not isinstance(text, bytes):
        text = text.encode()
    async with aiohttp.ClientSession() as session:
        post = await session.post("https://del.dog/documents", data=text)
        try:
            json = await post.json()
            return "https://del.dog/" + json["key"]
        except ContentTypeError:
            text = await post.text()
            return html.escape(text)
        
async def send_to_hastebin(text):
    if not isinstance(text, bytes):
        text = text.encode()
    async with aiohttp.ClientSession() as session:
        post = await session.post("https://haste.thevillage.chat/documents", data=text)
        try:
            json = await post.json()
            return "https://haste.thevillage.chat/" + json["key"]
        except ContentTypeError:
            text = await post.text()
            return html.escape(text)


def pretty_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    unit = 0
    while size >= 1024:
        size /= 1024
        unit += 1
    return '%0.2f %s' % (size, units[unit])


def get_flag(code):
    offset = 127462 - ord('A')
    return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)


def escape_markdown(text):
    text = text.replace('[', '\[')
    text = text.replace('_', '\_')
    text = text.replace('*', '\*')
    text = text.replace('`', '\`')

    return text

def backup_sources(output_file=None):
    ctime = int(time.time())

    if isinstance(output_file, str) and not output_file.lower().endswith('.zip'):
        output_file += '.zip'

    fname = output_file or 'backup-{}.zip'.format(ctime)

    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED) as backup:
        for folder, _, files in os.walk('.'):
            for file in files:
                if file != fname and not file.endswith('.pyc') and '.heroku' not in folder.split('/'):
                    backup.write(os.path.join(folder, file))

    return fname
