# -*- coding: utf-8 -*-

import unittest
from camptocamp.DAO.dao_mongodb import MongoDbDAO

# ------------------------------------------------------------------------------------------------------
# Implémentation des Tests unitaires de la classe Dao Mongodb
# Uses case simple de connection, insertion, recherche ...
# Auteur : SDI
# Date   : 01/11/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# ------------------------------------------------------------------------------------------------------


class TestDaoMongoDb(unittest.TestCase):

    # -----------------------------------------------------------------------------------------
    # Initialisation des inputs et des fonctions de tests
    # -----------------------------------------------------------------------------------------

    # Chargement une seule fois pour la classe
    @classmethod
    def setUpClass(cls):
        cls.mongo = MongoDbDAO()
        # Suppression de la collection 'voies_test' avant les tests
        coll = cls.mongo.db.voies_test
        coll.drop()

    # -----------------------------------------------------------------------------------------
    # Tests des méthodes statiques
    # -----------------------------------------------------------------------------------------

    def test_init(self):
        mongo = MongoDbDAO()
        self.assertIsNotNone(mongo)

    # Le nommage est important dans l'ordre d'execution
    def test_1_insert_voie(self):
        voietest = {'nom': 'voie de test unitaire',
                    'diff': '6a',
                    'commentaires': 'un commentaire',
                    'rating': 5}
        res = self.mongo.db.voies_test.insert_one(voietest)
        print("Objet insere: ID = {}".format(res.inserted_id))
        self.assertIsNotNone(res)

    def test_find_one(self):
        fivestar = self.mongo.db.voies_test.find_one({'rating': 5})
        self.assertIsNotNone(fivestar)

    def test_find_nonexistant(self):
        res = self.mongo.exists_voie('jenexistepas')
        self.assertIsNotNone(res)

    # la deletion du dernier document delete egalement la collection
    def test_z_delete_record(self):
        coll = self.mongo.db.voies_test
        q = {'rating': 5}
        res = coll.delete_one(q)
        print("Nombre enregistrement supprimé: {}".format(res.deleted_count))
        self.assertIs(res.deleted_count, 1)


# --------------------------------------------------------------------------
# Execution principale des tests
# --------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
