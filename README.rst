.. raw:: html

  <img src="https://i.imgur.com/RtXS5Yo.png" width="150" align="right">

EduuRobot
=========

|License| |Codacy| |Crowdin| |Black| |Telegram Channel| |Telegram Chat|

A multipurpose Telegram Bot made with Pyrogram and asynchronous programming.


Requirements
------------
- Python 3.7+
- An Unix-like operating system (Running on Windows isn't 100% supported. In case you find any issues inside Windows, please file an issue)


Setup
-----
1. Create a virtualenv (This step is optional, but **highly** recommended to avoid dependency conflicts)

   - ``python3 -m venv .venv`` (You don't need to run it again)
   - ``. .venv/bin/activate`` (You must run this every time you open the project in a new shell)

2. Install the required modules from the requirements.txt with ``pip3 install -Ur requirements.txt``.
3. Go to https://my.telegram.org/apps and create a new app.
4. Create a new ``config.py`` file from the ``config.py.example`` file (``cp eduu/config.py.example eduu/config.py``).
5. Place your token, IDs and api keys to your config.py file.


Running
-------
- To run the bot you just need to run ``python3 -m eduu``. In case you installed from a virtualenv, run ``. .venv/bin/activate`` before this.
- Running it on `screen <https://en.wikipedia.org/wiki/GNU_Screen>`__ or `tmux <https://en.wikipedia.org/wiki/Tmux>`__ is highly recommended if you want to keep the bot running on a server.


Note
----
If you find any bugs/issues with the bot you have three options:

- Create a new issue in our `GitHub <https://github.com/AmanoTeam/EduuRobot>`__ describing the issue.
- Send the /bug command to `bot's <https://t.me/EduuRobot>`__ chat describing the issue.
- If you know how to fix the issue, fork our repo and open up a pull request.


Translations
------------
Translations should be done in our `Crowdin project <https://crowdin.com/project/eduurobot>`__,
as Crowdin checks for grammar issues, provides improved context about the string being translated and so on,
thus possibly providing better quality translations. But you can also submit a pull request if you prefer translating that way.


Special thanks
--------------
* @Halokv: Arabic translation
* @SGANoud: Dutch translation
* @iiiiii1wepfj: Hebrew translation
* @HafitzSetya: Indonesian translation
* @Pato05: Italian translation
* @Quiec: Russian and Turkish translations
* And many other people I couldn't list here.


© 2023 - `AmanoTeam™ <https://amanoteam.com>`__

.. Badges
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/7e9bffc2c3a140cf9f1e5d3c4aea0c2f
   :target: https://www.codacy.com/gh/AmanoTeam/EduuRobot/dashboard
.. |Crowdin| image:: https://badges.crowdin.net/eduurobot/localized.svg
   :target: https://crowdin.com/project/eduurobot
.. |License| image:: https://img.shields.io/github/license/AmanoTeam/EduuRobot
.. |Telegram Channel| image:: https://img.shields.io/badge/Telegram-Channel-33A8E3
   :target: https://t.me/AmanoTeam
.. |Telegram Chat| image:: https://img.shields.io/badge/Telegram-Chat-33A8E3
   :target: https://t.me/AmanoChat
