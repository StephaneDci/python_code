# -*- coding: utf-8 -*-

""" ------------------------------------------------------------------------------------------------------
Création et Initialisation de la Database Sqlite
Auteur : SDI
Date   : 29/09/2019
Objectif : educationnal purpose only. Merci de respecter les copyrights.

Le script est executé par le __init__ du package Si et Seulement Si le chemin d'execution est le même
que le chemin racine du package (pour éviter la création dans les dossiers test/ , DAO/ ...)
------------------------------------------------------------------------------------------------------ """

import os
from camptocamp import Base, engine, sqlitedb_filename, logger
from camptocamp import ROOT_DIR

# Import nécessaire pour la création du modèle en database
from camptocamp.DAO.db_model import VoieDb

logger.info("Projet ROOT DIR: {}".format(ROOT_DIR))
logger.info("Execution DIR  : {}".format(os.getcwd()))

# Creation de la database SQLite uniquement dans le ROOT_DIR du projet
if ROOT_DIR == os.getcwd():
    logger.info("Check de l'existence de la database sqlite.")
    if os.path.isfile(sqlitedb_filename):
        logger.info('la database sqlite existe. Rien à faire')
    else:
        logger.warning("database sqlite n'existe pas: création...")
        Base.metadata.create_all(engine)
        logger.info("Fin de Creation de la db.")
