# -*- coding: utf-8 -*-

import pickle
from camptocamp import pickle_filename, logger

# --------------------------------------------------------------------------
# Classe pour la persistence dans des fichiers serialisées
# TODO a voir comment optimiser l'algorithme qui est couteux
# --------------------------------------------------------------------------


class PickleDAO:
    """
    Classe permettant la persistance via la serialisation des objets
    """
    def __init__(self):
        pass

    @staticmethod
    def insert(voie):
        """
        Insertion d'une voie dans une liste et dans un fichier
        :param voie: l'objet Voie
        :return:
        """
        voies = PickleDAO.restore()
        if voies is None:
            voies = list()

        logger.debug("Il y a {} voies dans {}".format(len(voies), pickle_filename))
        logger.info("{} : Serialisation.".format(voie.titre))
        voies.append(voie)
        pickle.dump(voies, open(pickle_filename, 'wb'))

    @staticmethod
    def exists(urldevoie):
        """
        Verification de l'existance d'une voie via son url
        :param urldevoie: url de la voie
        :return: id si voie existe, False sinon
        """
        # Chargement de la liste serialisée
        voies = PickleDAO.restore()

        # Recherche de la voie via son url
        if voies is not None:
            if isinstance(voies, list):
                for v in voies:
                    if v.url == urldevoie:
                        return True
        return False

    @staticmethod
    def restore():
        """
        Chargement de l'ensemble des voies serialisées
        :return: liste d'objet 'Voie'
        """
        try:
            with open(pickle_filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            logger.error("Pickle restore filename {} non existant".format(pickle_filename))
