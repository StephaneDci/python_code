# -*- coding: utf-8 -*-

""" ------------------------------------------------------------------------------------------------------
Initialisation des variable du projet
Déclaration des objets de persistance
Auteur : SDI
Date   : 21/08/2019
Objectif : educationnal purpose only. Merci de respecter les copyrights

# README Installation Chrome Driver
# Driver chrome headless (prendre le driver ici http://chromedriver.chromium.org/downloads)
# Il faut prendre la même version que Chrome installée sur le PC
# https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug

------------------------------------------------------------------------------------------------------ """

# Import des librairies
import logging
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from selenium import webdriver

# -----------------------------------------------------------------------------------
# Configuration Utilisateur
# -----------------------------------------------------------------------------------
loglevel = logging.INFO     # Niveau de log
db_debug_mode = False       # mode debug database
headless = False            # Chrome headless
proxy = None                # Proxy selenium None ou 'ip:port' exemple '127.0.0.1:3128'
no_image = True             # Pas de Chargement des images
pickle_filename = ''        # fichier de persistence Pickle
chromedriver = r"E:\\Logiciels\\Developpement\\chromedriver\\chromedriver_76.exe"
# ------------------------------------------------------------------------------------

# Configuration du logging pour les classes
logging.basicConfig(level=loglevel,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%I:%M:%S %p')
# https://docs.python-guide.org/writing/logging/
# fileConfig('logging_config.ini')
logging.getLogger(__name__).addHandler(logging.NullHandler())

# ------------------------------------------------------
# Création des options pour le driver Chrome
options = webdriver.ChromeOptions()

if headless:
    options.add_argument('--headless')
if proxy is not None:
    options.add_argument('--proxy-server=%s' % proxy)
if no_image:
    options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})


# Initialisation du driver
def init_driver():
    logger.info("Initialisation of Web driver...")
    chromewebdriver = webdriver.Chrome(options=options, executable_path=chromedriver)
    # Simulation de condition de réseaux
    chromewebdriver.set_network_conditions(
        offline=False,
        latency=15,                         # additional latency (ms)
        download_throughput=500 * 1024,     # maximal throughput
        upload_throughput=500 * 1024)       # maximal throughput
    return chromewebdriver


# -------------------------------------------------------
# Variables importées dans le code:
# -------------------------------------------------------
logger = logging.getLogger()
engine = create_engine('sqlite:///dbcamptocamp.db?check_same_thread=False', echo=db_debug_mode)
Session = sessionmaker(bind=engine)
Base = declarative_base()
# -------------------------------------------------------

######################################################################################
# !! IMPORTANT AVANT DE COMMENCER !!
# A faire pour initialiser la Base sqlite !
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

# Par la suite nous pouvons ajouter un ou des enregistrements
"""
parser1 = C2CParser('https://www.camptocamp.org/routes/53914')
voie1 = Voie.from_c2cparser(parser1)
voiedb1 = VoieDb.from_voie(voie1)
session = Session()
session.add(voiedb1)
session.commit()
session.close()
"""
