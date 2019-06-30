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
import time
import schedule
from datetime import datetime
from utils import backup_sources
from multiprocessing import Process
from config import backups_chat, backup_hours, na_bot


def backup_func():
    cstrftime = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    file = backup_sources()

    na_bot.sendDocument(backups_chat, open(file, 'rb'), caption="📅 " + cstrftime + "\n_Auto generated._", parse_mode='Markdown')

    os.remove(file)


def backup_scheduler(target):
    for hour in backup_hours:
        schedule.every().day.at(hour).do(target)

    while True:
        schedule.run_pending()
        time.sleep(5)


def backup_service():
    p = Process(target=backup_scheduler, args=(backup_func,))
    p.start()
