# -*- coding: utf-8 -*-

import pickle
from camptocamp import pickle_filename, logger

# --------------------------------------------------------------------------
# Classe Voie pour la persistence dans des fichiers serialisées
# --------------------------------------------------------------------------


class Pickle_DAO:
    def __init__(self):
        pass

    @staticmethod
    def insert(voie):
        logger.info("{} : Serialisation de la voie en cours...".format(voie.titre))
        pickle.dump(voie, open(pickle_filename, 'wb'))
        logger.info("Fin de la Serialisation !")

    # Retourne id si voie existe, False sinon
    @staticmethod
    def exists(urldevoie):
        voies = Pickle_DAO.restore()
        for v in voies:
            if v.url == urldevoie:
                return v.url
        return False

    @staticmethod
    def restore():
        voies_loaded_p = pickle.load(open(pickle_filename, 'rb'))
        logger.info("Il y a {} voie(s)".format(len(voies_loaded_p)))
        return voies_loaded_p
