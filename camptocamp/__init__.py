# -*- coding: utf-8 -*-

""" ------------------------------------------------------------------------------------------------------
Init du package et Initialisation des variables du projet
Déclaration des objets de persistance
Auteur : SDI
Date   : 21/08/2019
Objectif : educationnal purpose only. Merci de respecter les copyrights

# README: Installation Chrome Driver
# Driver chrome headless (prendre le driver ici http://chromedriver.chromium.org/downloads)
# Il faut prendre la même version que Chrome installée sur le PC
# https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug
"""

# ------------------------------------------------------
# Import des librairies
# ------------------------------------------------------
import os
import logging
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from selenium import webdriver

# ------------------------------------------------------
# Copyrights
# ------------------------------------------------------
__author__ = "Stéphane Di Cioccio"
__version__ = "2.2.0"
__copyright__ = "Copyright (c) 2004-2019 Stéphane Di Cioccio"
__license__ = "MIT"

# -----------------------------------------------------------------------------------
# Configuration des variables Utilisateur
# -----------------------------------------------------------------------------------
loglevel = logging.INFO         # Niveau de log
db_debug_mode = False           # mode debug pour database
nb_workers = 3                  # Nombre de threads à allouer
chrome_proxy = '127.0.0.1:3128'             # Proxy selenium None ou 'ip:port' exemple '127.0.0.1:3128'
chrome_headless = False          # Chrome headless (boolean, true or false)
chrome_no_image = True          # Pas de Chargement des images (boolean)
chromedriver = r"E:\\Logiciels\\Developpement\\chromedriver\\chromedriver_78.exe"
pickle_filename = 'c2c.pic'                         # fichier de persistence Pickle
mongodburl = 'mongodb://192.168.158.134:27017/'     # endpoint mongodb
# ------------------------------------------------------------------------------------

ROOT_DIR = (os.path.dirname(os.path.abspath(__file__)))   # Project Root Dir

# ------------------------------------------------------
# Configuration du logging pour les classes
# ------------------------------------------------------
# logging.basicConfig(level=loglevel,
#                    format='%(asctime)s %(levelname)-12s %(filename)-20s %(threadName)s: %(message)s',
#                    datefmt='%I:%M:%S %p')
# logging.getLogger(__name__).addHandler(logging.NullHandler())

# https://docs.python-guide.org/writing/logging/
fileConfig(ROOT_DIR + '\\' + 'logging_config.ini')

# -------------------------------------------------------
# Principales Variables
# -------------------------------------------------------
logger = logging.getLogger()
sqlitedb_filename = ROOT_DIR + '\\' + 'dbcamptocamp.db'
engine = create_engine('sqlite:///{}?check_same_thread=False'.format(sqlitedb_filename),
                       echo=db_debug_mode)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# ------------------------------------------------------
# Création des options pour le WEB DRIVER Chrome
# ------------------------------------------------------
options = webdriver.ChromeOptions()

if chrome_headless:
    options.add_argument('--headless')
if chrome_proxy is not None:
    options.add_argument('--proxy-server=%s' % chrome_proxy)
if chrome_no_image:
    options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})


def init_driver():
    """
    Initialisation du driver appelé par la classe de c2cparser
    :return: l'instance du webdriver
    """
    logger.info("Initialisation du Web driver.")
    chromewebdriver = webdriver.Chrome(options=options,
                                       executable_path=chromedriver)
    # Simulation de condition de réseaux
    chromewebdriver.set_network_conditions(
        offline=False,
        latency=5,                          # additional latency (ms)
        download_throughput=1000 * 1024,    # maximal throughput
        upload_throughput=500 * 1024)       # maximal throughput
    return chromewebdriver


# ------------------------------------------------------
# Initialisation de la Database SQLite
# ------------------------------------------------------
# l'import ici pour éviter les dépendances circulaires.
import camptocamp.DAO.sqlite_initdb

# ------------------------------------------------------
# Initialisation de la connection vers MongoDb
# ------------------------------------------------------
# l'import ici evite les dépendances circulaires.
from camptocamp.DAO.dao_mongodb import MongoDbDAO
mongodb = MongoDbDAO()


######################################################################################
# !! IMPORTANT: AVANT DE COMMENCER (initialisation manuelle) !!
# NB : le script sqlite_initdb automatise cette étape qui n'est plus obligatoire.
# https://stackoverflow.com/questions/30115010/using-flask-sqlalchemy-without-flask
######################################################################################
#
# Passer le modeDebug à True dans l'engine
# Ouvrir une Python Console
# ---------------
"""
from camptocamp import Base, Session, engine
from camptocamp.voie import Voie, C2CParser
from camptocamp.DAO.db_model import VoieDb
Base.metadata.create_all(engine)
"""
# A partir de ce moment la base est crée A LA RACINE DU PROJET
# Ne pas oublier de la déplacer dans la structure du répértoire

# Option: Par la suite nous pouvons ajouter un ou des enregistrements
"""
parser1 = C2CParser('https://www.camptocamp.org/routes/53914')
voie1 = Voie.from_c2cparser(parser1)
voiedb1 = VoieDb.from_voie(voie1)
session = Session()
session.add(voiedb1)
session.commit()
session.close()
"""