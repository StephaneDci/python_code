# -*- coding: utf-8 -*-

import unittest
from camptocamp.c2cparser import C2CParser
from camptocamp import logger

# ------------------------------------------------------------------------------------------------------
# Implémentation des Tests unitaires de la classe de Parser
# Auteur : SDI
# Date   : 21/08/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# ------------------------------------------------------------------------------------------------------


class TestParserMethods(unittest.TestCase):

    # Chargement une seule fois pour la classe
    @classmethod
    def setUpClass(cls):
        cls.expected_liste = ['https://www.camptocamp.org/routes/53914']
        cls.expected_baseurl = C2CParser.baseurl
        cls.c2c = C2CParser('https://www.camptocamp.org/routes/171402')

    # A la fin de tous les tests fermeture du driver
    @classmethod
    def tearDownClass(cls):
        cls.c2c.driver.close()

    # -----------------------------------------------------------------------------------------
    # Tests des méthodes statiques
    # -----------------------------------------------------------------------------------------

    def test_filtre_doublon(self):
        logger.info("\nTest Filtrage des doublons...")
        liste_non_filtree = ['https://www.camptocamp.org/routes/53914',
                             'https://www.camptocamp.org/routes/53914']
        liste_filtree = C2CParser.filter_url(liste_non_filtree)
        self.assertCountEqual(liste_filtree, self.expected_liste)

    def test_filtre_mauvais_baseurl(self):
        logger.info("\nTest Filtrage mauvais baseurl...")
        liste_non_filtree = ['https://www.camp.org/routes/53914',
                             'https://www.tocamp.org/routes/53914',
                             'https://www.camptocamp.org/routes/53914']
        liste_filtree = C2CParser.filter_url(liste_non_filtree)
        self.assertCountEqual(liste_filtree, self.expected_liste)

    def test_get_baseurl(self):
        logger.info("\nTest fonction get_baseurl()...")
        baseurl = C2CParser.get_baseurl('https://www.camptocamp.org/routes/53914')
        self.assertEqual(baseurl, self.expected_baseurl)

    def test_get_urlvoie(self):
        inputurl = 'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum'
        expected = 'https://www.camptocamp.org/routes/171402'
        output = C2CParser.get_urlvoie(inputurl)
        self.assertEqual(output, expected)

    def test_get_list_from_waypoint(self):
        output = self.c2c.get_list_from_waypoint('https://www.camptocamp.org/waypoints/40766/fr/presles-eliane',
                                                 typecourse='Escalade')
        self.assertIsInstance(output, list)
        self.assertGreater(len(output), 10)

    # -----------------------------------------------------------------------------------------
    # Tests fonctionnels
    # -----------------------------------------------------------------------------------------

    def test_get_titre(self):
        output_titre = self.c2c.get_titre()
        self.assertEqual(output_titre, 'Presles - Eliane : Bim Bam Boum')

    def test_get_approche(self):
        output_approche = self.c2c.get_approche()
        approche = output_approche.get('approche')
        self.assertIsInstance(output_approche, dict)
        self.assertIsInstance(approche, str)
        self.assertGreater(len(output_approche), 1)
        self.assertIn("Bim Bam Boum", approche)

    def test_get_details_longueurs(self):
        output = self.c2c.get_details_longueurs()
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 4)
        self.assertIn('L1', output[0])

    def test_get_commentaires(self):
        output = self.c2c.get_commentaires()
        self.assertIsInstance(output, str)
        self.assertIn('11 avril 1994', output)
        self.assertIn('Bim Bam Boum', output)

    def test_get_cotations(self):
        output = self.c2c.get_cotations()
        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), 5)
        self.assertEqual(output.get('Cotation globale'), 'AD+')

    def test_get_alt_difficultes(self):
        output = self.c2c.get_alt_difficultes()
        self.assertIsInstance(output, dict)
        self.assertEqual(len(output), 3)
        self.assertEqual(output.get('Altitude maximale'), '874 m')

    def test__get_url_outings(self):
        output = self.c2c._get_url_outings()
        self.assertEqual(output, '/outings?r=171402')

    def test__get_urls_outings(self):
        output = self.c2c._get_urls_outings()
        self.assertIsInstance(output, list)
        self.assertGreater(len(output), 15)

    """
    @unittest.skip("skipping test récupération des sorties(temps d'execution)")
    def test_get_outings(self):
        output = self.c2c.get_outings()
        self.assertIsInstance(output, str)
        self.assertIn(output, '\n')
        self.assertGreater(len(output), 500)
    """


# --------------------------------------------------------------------------
# Execution principale des tests
# --------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
