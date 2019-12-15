# -*- coding: utf-8 -*-

import unittest
from unittest import mock
from camptocamp.c2cparser import C2CParser
from camptocamp.voie import Voie
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------------------------------
# Implémentation des Tests unitaires de la classe de Parser
# TEST SUR DES FICHIERS STATIQUES en date du 28.09.19 => OK
# Les datas se trouvent dans le répertoire test_data
# Auteur : SDI
# Date   : 28/09/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# ------------------------------------------------------------------------------------------------------


class TestParserMocked(unittest.TestCase):

    # -----------------------------------------------------------------------------------------
    # Initialisation des inputs et des fonctions de tests
    # -----------------------------------------------------------------------------------------

    # Chargement une seule fois pour la classe
    @classmethod
    def setUpClass(cls):
        cls.expected_liste = ['https://www.camptocamp.org/routes/53914']
        cls.liste_urlsorties = ['/outings/1000237', '/outings/857663', '/outings/824689', '/outings/813316',
                                '/outings/739505',  '/outings/693927', '/outings/638485', '/outings/641770',
                                '/outings/631311',  '/outings/579792', '/outings/563566', '/outings/531207',
                                '/outings/558521', '/outings/282536', '/outings/291154',  '/outings/171403']
        cls.expected_baseurl = C2CParser.baseurl
        cls.c2c = TestParserMocked.htmlfile_to_c2c('test_data/_routes_171402_fr_presles-eliane-bim-bam-boum.html')

    # Depuis un fichier html renvoie une instance de C2CParser
    @staticmethod
    def htmlfile_to_c2c(filename):
        html = TestParserMocked.read_file_to_html(filename)
        soup = BeautifulSoup(html, 'lxml')
        c2c = C2CParser(url=None)
        c2c.rawsoup = soup
        c2c.urlvoie = 'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum'
        return c2c

    # Lecture des fichier html en utf8
    @staticmethod
    def read_file_to_html(filename):
        with open(filename, encoding="utf-8") as f:
            html = f.read()
        return html

    # -----------------------------------------------------------------------------------------
    # Tests des méthodes statiques
    # -----------------------------------------------------------------------------------------

    def test_filtre_doublon(self):
        liste_non_filtree = ['https://www.camptocamp.org/routes/53914',
                             'https://www.camptocamp.org/routes/53914']
        liste_filtree = C2CParser.filter_url(liste_non_filtree)
        self.assertCountEqual(liste_filtree, self.expected_liste)

    def test_filtre_mauvais_baseurl(self):
        liste_non_filtree = ['https://www.camp.org/routes/53914',
                             'https://www.tocamp.org/routes/53914',
                             'https://www.camptocamp.org/routes/53914']
        liste_filtree = C2CParser.filter_url(liste_non_filtree)
        self.assertCountEqual(liste_filtree, self.expected_liste)

    def test_get_baseurl(self):
        baseurl = C2CParser.get_baseurl('https://www.camptocamp.org/routes/53914')
        self.assertEqual(baseurl, self.expected_baseurl)

    def test_get_urlvoie(self):
        inputurl = 'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum'
        expected = 'https://www.camptocamp.org/routes/171402'
        output = C2CParser.get_urlvoie(inputurl)
        self.assertEqual(output, expected)

    # -----------------------------------------------------------------------------------------
    # Tests fonctionnels sur fichier html principal
    # -----------------------------------------------------------------------------------------

    def test_get_titre(self):
        output_titre = self.c2c.get_titre()
        self.assertEqual(output_titre, 'Presles - Eliane : Bim Bam Boum')

    def test_get_area(self):
        output = self.c2c.get_area()
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 3)
        self.assertIn('France', output[0])
        self.assertIn('Vercors', output[2])

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

    # -----------------------------------------------------------------------------------------
    # Tests fonctionnels avec mock de fonctions
    # -----------------------------------------------------------------------------------------

    # Exemple remplacement fonction simple
    @mock.patch('camptocamp.c2cparser.C2CParser.to_mock_function')
    def test_to_mock(self, simple_mock):
        simple_mock.return_value = "Fonction Monkee OK !"
        output = self.c2c.to_mock_function()
        print(output)

    # Remplacemement du chargement
    @mock.patch('camptocamp.c2cparser.C2CParser.get_soup_from_url')
    def test__get_urls_outings(self, simple_mock):
        simple_mock.return_value = self.htmlfile_to_c2c('test_data/_outings_r_171402.html').rawsoup
        output = self.c2c._get_urls_outings()
        self.assertIsInstance(output, list)
        self.assertGreater(len(output), 15)
        self.assertCountEqual(output, self.liste_urlsorties)

    # Plusieurs mock : attention a l'ordre entre les décorateurs et les arguments de la fonction de test
    @mock.patch('camptocamp.c2cparser.C2CParser._get_urls_outings')
    @mock.patch('camptocamp.c2cparser.C2CParser.get_soup_from_url')
    def test_get_outings(self, get_soup_mock, _get_urls_outings_mock):
        _get_urls_outings_mock.return_value = ['/outings/1000237']
        get_soup_mock.return_value = TestParserMocked.htmlfile_to_c2c('test_data/_outings_1000237.html').rawsoup
        output = self.c2c.get_outings()
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)
        self.assertIn('Vendredi 11 mai 2018', output[0])
        self.assertIn('mousquetonnage', output[0])

    @mock.patch('camptocamp.c2cparser.C2CParser._get_urls_outings')
    @mock.patch('camptocamp.c2cparser.C2CParser.get_soup_from_url')
    def test_from_c2cparser(self, get_soup_mock, _get_urls_outings_mock):
        _get_urls_outings_mock.return_value = ['/outings/1000237']
        get_soup_mock.return_value = TestParserMocked.htmlfile_to_c2c('test_data/_outings_1000237.html').rawsoup
        v = Voie.from_c2cparser(self.c2c)
        self.assertIsInstance(v, Voie)
        self.assertIsInstance(v.approche, dict)
        self.assertIsInstance(v.longueurs, list)
        self.assertIsInstance(v.sorties, list)
        self.assertEqual(len(v.sorties), 1)
        self.assertEqual(len(v.longueurs), 4)
        self.assertEqual(v.titre, 'Presles - Eliane : Bim Bam Boum')
        self.assertEqual(v.url, 'https://www.camptocamp.org/routes/171402')
        self.assertIn('L1 4c', v.longueurs[0])
        self.assertIn('falaises de Presles', v.commentaires)
        self.assertIn('le 5c passe tout seul', v.sorties[0])

    # Mock du constructeur
    @mock.patch('camptocamp.c2cparser.C2CParser')
    def test_get_list_from_waypoint_escalade(self, mock_class):
        mock_class.return_value = \
            TestParserMocked.htmlfile_to_c2c('test_data/_waypoints_40766_fr_presles-eliane.html')
        output = self.c2c.get_list_from_waypoint('https://www.camptocamp.org/waypoints/40766/fr/presles-eliane',
                                                 typecourse='Escalade')
        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 13)


# --------------------------------------------------------------------------
# Execution principale des tests
# --------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
