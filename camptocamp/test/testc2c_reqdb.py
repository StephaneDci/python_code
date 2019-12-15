# -*- coding: utf-8 -*-

import unittest
from camptocamp.DAO.db_model import VoieDb
from camptocamp import Session

# ------------------------------------------------------------------------------------------------------
# Implémentation des Tests de requetes sur la base Sqlite
# Auteur : SDI
# Date   : 10/11/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# ------------------------------------------------------------------------------------------------------


class TestParserMethods(unittest.TestCase):

    # -----------------------------------------------------------------------------------------
    # Tests fonctionnels sur la database
    # -----------------------------------------------------------------------------------------

    def test_requete_base(self):
        session = Session()
        print(session.query(VoieDb).all())


# --------------------------------------------------------------------------
# Execution principale des tests
# --------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
