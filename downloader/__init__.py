# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------------------
# Init Downloader.
# Auteur : SDI
# Date   : 15/02/2020
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# Python >= 3.8 + modules dans les requirements
# Lectures Recommandées :
#  https://stackoverflow.com/questions/3490173/how-can-i-speed-up-fetching-pages-with-urllib2-in-python/3491455#3490368
#  https://stackoverflow.com/questions/52676647/how-to-define-circularly-dependent-data-classes-in-python-3-7
#  https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
#  https://realpython.com/python-concurrency/
#  https://www.reddit.com/r/learnpython/comments/5qwm5h/asyncio_for_dummies/dd432ke/
#  https://medium.com/@nhumrich/asynchronous-python-45df84b82434
#  https://stackoverflow.com/questions/60320220/python-tqdm-race-condition-with-threading
# ------------------------------------------------------------------------------------------------------

import os
import logging
from logging.config import fileConfig

ROOT_DIR = (os.path.dirname(os.path.abspath(__file__)))   # Project Root Dir
fileConfig(ROOT_DIR + '\\' + 'logging_config.ini')
logger = logging.getLogger('app_logger')