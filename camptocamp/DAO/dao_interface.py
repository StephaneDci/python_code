# -*- coding: utf-8 -*-

from camptocamp import logger
from camptocamp.DAO.db_model import VoieDb
from camptocamp.DAO.pickle_model import PickleDAO
from camptocamp import mongodb


class InterfaceDAO:
    """
    Classe présentant une interface avec des méthodes statiques afin de:
     - vérifier l'existence des enregistrements
     - inserer les enregistrements dans les backends
    """

    # TODO initialiser les connections vers les backends ?
    def __init__(self):
        pass

    # TODO refaire un check sur les conditions d'existence en multi backend
    @staticmethod
    def check_exists(urlvoie, backends):
        """
        Vérification si une voie existe dans le backend en question
        :param urlvoie: l'url de la voie (son identifiant unique)
        :param backends: liste des backends dans lesquels faire la vérification
        :return: true si la voie existe, false si elle n'existe pas
        """
        logger.debug("Verification existance de la voie dans les backends: {}".format(backends))
        if 'db' in backends:
            return VoieDb.exists(urlvoie)
        if 'pickle' in backends:
            pickle = PickleDAO()
            return pickle.exists(urlvoie)
        if 'mongodb' in backends:
            return mongodb.exists_voie(urlvoie)

    @staticmethod
    def persistance_voie(voie, backends):
        """
        Interface permettant d'insérer dans le backend la voie
        :param voie: Objet 'Voie' à insérer
        :param backends: liste des backends pour insertion
        :return:
        """
        logger.debug("Insertion de la voie dans les backends {}".format(backends))
        if 'db' in backends:
            voiedb = VoieDb.from_voie(voie)
            voiedb.insert()
        if 'pickle' in backends:
            pickle = PickleDAO()
            pickle.insert(voie)
        if 'mongodb' in backends:
            mongodb.insert(voie)
