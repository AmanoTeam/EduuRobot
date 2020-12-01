.. raw:: html

  <img src="https://i.imgur.com/RtXS5Yo.png" width="150" align="right">

EduuRobot
=========

|License| |Codacy| |Crowdin| |Telegram Channel| |Telegram Chat|

A multipurpose Telegram Bot made with Pyrogram and asynchronous programming.


Requirements
------------
- Python 3.6+
- An Unix-like operating system (Running on Windows isn't 100% supported. In case you find any issues inside Windows, please file an issue)


Setup
-----
- Install the required modules from the requirements.txt with ``pip3 install -Ur requirements.txt``.
- Go to https://my.telegram.org/apps and create a new app.
- Create a new ``config.py`` file from the ``config.py.example`` file (``cp config.py.example config.py``).
- Place your token, IDs and api keys to your config.py file.


Running
-------
- To run the bot you just need to run ``python3 bot.py``.
- Running it on `screen <https://en.wikipedia.org/wiki/GNU_Screen>`__ or `tmux <https://en.wikipedia.org/wiki/Tmux>`__ is highly recommended if you want to keep the bot running on a server.


Note
----
If you find any bugs/issues with the bot you have three options:

- Create a new issue in our `GitHub <https://github.com/AmanoTeam/EduuRobot>`__ describing the issue.
- Send the /bug command to `bot's <https://t.me/EduuRobot>`__ chat describing the issue.
- If you know how to fix the issue, fork our repo and open up a pull request.


Translations
------------
All translations must be done in our `Crowdin project <https://crowdin.com/project/eduurobot>`__.
Direct pull requests will be closed.

We only accept pull requests for source language changes (currently en-GB).


Special thanks
--------------
* @iiiiii1wepfj: Hebrew translation
* @HafitzSetya: Indonesian translation
* @Pato05: Italian translation
* @Quiec: Russian and Turkish translations
* And many other people I couldn't list here.


©2020 - `AmanoTeam™ <https://amanoteam.com>`__

.. Badges
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/7e9bffc2c3a140cf9f1e5d3c4aea0c2f
   :target: https://www.codacy.com/gh/AmanoTeam/EduuRobot/dashboard?utm_source=github.com&utm_medium=referral&utm_content=AmanoTeam/EduuRobot&utm_campaign=Badge_Grade
.. |Crowdin| image:: https://badges.crowdin.net/eduurobot/localized.svg
   :target: https://crowdin.com/project/eduurobot
.. |License| image:: https://img.shields.io/github/license/AmanoTeam/EduuRobot
.. |Telegram Channel| image:: https://img.shields.io/badge/Telegram-Channel-33A8E3
   :target: https://t.me/AmanoTeam
.. |Telegram Chat| image:: https://img.shields.io/badge/Telegram-Chat-33A8E3
   :target: https://t.me/AmanoChat
