# -*- coding: utf-8 -*-

import unittest
import html
from downloader.file_downloader import Page, WebRessourcePattern, RessourceFile, FileDownloader

# ------------------------------------------------------------------------------------------------------
# Implémentation des Tests unitaires
# Auteur : SDI
# Date   : 15/02/2020
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# ------------------------------------------------------------------------------------------------------


class TestDownloaderMocked(unittest.TestCase):

    # Chargement une seule fois pour la classe
    @classmethod
    def setUpClass(cls):
        cls.url = "https://www.audiolitterature.com/michel-onfray-traite-datheologie/"
        cls.directory = "rep1"
        cls.pattern = r"http\S+mp3"
        cls.srcpage = TestDownloaderMocked.read_file_to_html(
            'test_data/test_www.audiolitterature.com_michel-onfray-traite-datheologie_.html')
        cls.Page = Page(url=cls.url, directory=cls.directory, pattern=cls.pattern)
        cls.Ressource = RessourceFile(link="https://link1/monrepn1/monrepn2/audio1.mp3", page=cls.Page)

    # Lecture des fichier html en utf8
    @staticmethod
    def read_file_to_html(filename):
        with open(filename) as f:
            h = f.read()
        return html.unescape(h)

    # --------------------------------------------------------------------------
    # Tests Classe RessourceFile
    # --------------------------------------------------------------------------
    def test_properties_ressource1(self):
        self.assertEqual('audio1.mp3', self.Ressource.filename)
        self.assertEqual('rep1\\audio1.mp3', self.Ressource.filepath)

    def test_properties_ressource2(self):
        p = Page(url="https://supersiteaudio.com/monartiste", directory="", pattern=r"http\S+mp3")
        r = RessourceFile(link="https://link2/monrepn2/audio2.mp3", page=p)
        self.assertEqual('audio2.mp3', r.filename)
        self.assertEqual(p.DEFAULT_DIR+r'\monartiste\audio2.mp3', r.filepath)

    def test_properties_ressource3(self):
        p = Page(url="https://supersiteaudio.com/artiste1/listings/1/", directory="", pattern=r"http\S+mp3")
        r = RessourceFile(link="https://127.0.0.1:8080/monrepn_bizaroide_221522/12345.mp3", page=p)
        self.assertEqual('12345.mp3', r.filename)
        self.assertEqual(p.DEFAULT_DIR+'\\artiste1\\listings\\1\\12345.mp3', r.filepath)

    def test_properties_ressource_size(self):
        p = Page(url="http://myurl.com", directory="myrep", pattern="nopattern")
        r1 = RessourceFile(link="1.mp3", headers={'Content-Length': 1024}, page=p)
        self.assertEqual(1024, r1.size)
        r2 = RessourceFile(link="null.mp3", page=p)
        self.assertEqual(0, r2.size)

    def test_ressources_equality_and_appartenance(self):
        p = Page(url="http://myurl.com", directory="myrep", pattern="nopattern")
        r1 = RessourceFile(link="http://monsite.com/rep1/1.mp3", headers={'Content-Length': 1024}, page=p)
        r2 = RessourceFile(link="1.mp3", page=p)
        r3 = RessourceFile(link="rep1/1.mp3", page=p)
        r4 = RessourceFile(link="127.0.0.1:80/1.mp3", page=p)
        r5 = RessourceFile(link="1.mp3", page=p)
        self.assertNotEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertNotEqual(r1, r4)
        b1 = r2.__eq__(r5)
        b2 = r2 == r5
        self.assertEqual(True, b1)
        self.assertEqual(True, b2)
        self.assertEqual(r2, r5)
        # liste initiale et test si r5 dans liste => Faux
        l1 = [r1, r3, r4]
        appartenance = r5 in l1
        self.assertEqual(False, appartenance)
        # ajout de r2 (==r5) et test si r5 dans l1 => True
        l1.append(r2)
        appartenance = r5 in l1
        self.assertEqual(True, appartenance)
        # ajout de r5 et test si r5 dans l1 => True
        l1.append(r5)
        appartenance = r5 in l1
        self.assertEqual(True, appartenance)

    # --------------------------------------------------------------------------
    # Tests Classe Page:
    # --------------------------------------------------------------------------

    def test_size_ressources(self):
        p = Page(url="http://myurl.com", directory="myrep", pattern="nopattern")
        r1 = RessourceFile(link="1.mp3", page=p, headers={'Content-Length': 1})
        r2 = RessourceFile(link="2.mp3", page=p, headers={'Content-Length': 2})
        r3 = RessourceFile(link="3.mp3", page=p, headers={'Content-Length': 3})
        p.ressources = [r1, r2, r3]
        s = p.size_ressources
        self.assertEqual(6, s)

    def test_nbr_download_for_a_page(self):
        p = Page(url="http://myurl.com", directory="myrep", pattern="nopattern")
        r1 = RessourceFile(link="1.mp3", page=p, downloaded=True)
        r2 = RessourceFile(link="2.mp3", page=p, downloaded=False)
        r3 = RessourceFile(link="3.mp3", page=p)
        p.ressources = [r1, r2, r3]
        s = p.nbr_download
        self.assertEqual(1, s)

    def test_set_pattern(self):
        p = WebRessourcePattern.get_pattern("mp3")
        self.assertEqual(r'http\S+mp3', p)
        wb = WebRessourcePattern(extension='mp3')
        p = WebRessourcePattern.get_pattern(wb)
        self.assertEqual(r'http\S+mp3', p)
        wb = WebRessourcePattern(extension='mp3', include_pattern='mypattern')
        p = WebRessourcePattern.get_pattern(wb)
        self.assertEqual(r'http\S+mypattern\S+mp3', p)
        with self.assertRaises(Exception):
            wb = WebRessourcePattern(extension=123, include_pattern=[])
            p = self.Page.set_pattern(wb)

    def test_set_directory(self):
        dir = self.Page.set_directory(directory="")
        self.assertEqual(self.Page.DEFAULT_DIR+r'\michel-onfray-traite-datheologie', dir)
        dir = self.Page.set_directory(directory="reptest")
        self.assertEqual('reptest', dir)
        with self.assertRaises(Exception):
            self.Page.set_directory(directory=999)
        with self.assertRaises(Exception):
            self.Page.set_directory(directory=None)

    def test_set_proxies(self):
        p = self.Page.set_proxies("127.0.0.1:3128")
        self.assertEqual({"http": "127.0.0.1:3128", "https": "127.0.0.1:3128"}, p)
        with self.assertRaises(Exception):
            self.Page.set_proxies("noport")
        with self.assertRaises(Exception):
            self.Page.set_proxies(["list"])
        with self.assertRaises(Exception):
            self.Page.set_proxies(None)

    def test_get_ressources_list_matching_pattern_mp3(self):
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, self.pattern)
        self.assertIsInstance(rsc, list)
        self.assertEqual(10, len(rsc))
        self.assertIsInstance(rsc[0], RessourceFile)
        self.assertEqual(False, rsc[0].downloaded)
        self.assertEqual('rep1', rsc[0].page.directory)
        self.assertEqual('https://www.audiolitterature.com/wp-content/uploads/audio/michel-onfray/michel-onfray-traite-d\'atheologie-01.mp3', rsc[0].link)
        self.assertEqual('https://www.audiolitterature.com/wp-content/uploads/audio/michel-onfray/michel-onfray-traite-d\'atheologie-09.mp3', rsc[8].link)

    def test_get_ressources_list_matching_webpattern_mp3(self):
        wbp = WebRessourcePattern(extension="mp3", include_pattern="atheologie-01")
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, str(wbp))
        self.assertIsInstance(rsc, list)
        self.assertEqual(1, len(rsc))
        self.assertIsInstance(rsc[0], RessourceFile)
        self.assertEqual(False, rsc[0].downloaded)
        self.assertEqual('rep1', rsc[0].page.directory)
        self.assertEqual('https://www.audiolitterature.com/wp-content/uploads/audio/michel-onfray/michel-onfray-traite-d\'atheologie-01.mp3', rsc[0].link)

    def test_get_ressources_list_matching_pattern_alternative_cases(self):
        rsc = self.Page.get_ressources_list_matching_pattern("", self.pattern)
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern(None, self.pattern)
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern("<html><head>1234>aHeee<b>...12'ttt'<alert>", self.pattern)
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, None)
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, 12345)
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, "NOPATTERN")
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))
        rsc = self.Page.get_ressources_list_matching_pattern("NOHTML", "NOPATTERN")
        self.assertIsInstance(rsc, list)
        self.assertEqual(0, len(rsc))

    def test_get_ressources_list_matching_pattern_doublons_cases(self):
        wbp = WebRessourcePattern(extension="mp3")
        srcpage = """<html><head>test</head>
                     <a href="http://monsite/lien1.mp3">lien1</a>
                     <a href="http://monsite/lien2.mp3">lien2</a>
                     <a href="http://monsite/lien3.mp3">lien</a>
                     <a href="http://monsite/lien1.mp3">lien1_bis</a>
                     <a href="http://monsite/lien1_bis.mp3">lien1</a>
                     </html>
                     """
        srcpage = html.unescape(srcpage)
        rsc = self.Page.get_ressources_list_matching_pattern(srcpage, str(wbp))
        self.assertIsInstance(rsc, list)
        self.assertEqual(4, len(rsc))

    def test_get_headers_on_ressources(self):
        wbp = WebRessourcePattern(extension="mp3", include_pattern="atheologie-01")
        rsc = self.Page.get_ressources_list_matching_pattern(self.srcpage, str(wbp))
        self.Page.set_ressources_infos_parallel(rsc)
        self.assertEqual(rsc[0].downloaded, False)
        self.assertEqual(rsc[0].size, 33345344)
        self.assertEqual(rsc[0].headers.get('Content-Type'), 'audio/mpeg')

    # --------------------------------------------------------------------------
    # Tests Classe Downloader:
    # --------------------------------------------------------------------------

    def test_add_download_Page(self):
        fd = FileDownloader(page=self.Page)
        self.assertEqual(1, len(fd.pages))
        fd.add_download_page(Page(url="url2", pattern='pattern2'))
        self.assertEqual(2, len(fd.pages))
        lpages = [Page(url="url3", pattern='pattern3'), Page(url="url4", pattern='pattern4')]
        fd.add_download_page(lpages)
        self.assertEqual(4, len(fd.pages))
        with self.assertRaises(Exception):
            fd.add_download_page(None)
        with self.assertRaises(Exception):
            fd.add_download_page("chaine")
        # Test doublon
        p5 = Page(url="url3", pattern='pattern3')
        fd.add_download_page(p5)
        self.assertEqual(4, len(fd.pages))

    def test_doublon_dans_global_ressources(self):
        p1 = Page(url="http://myurl1.com", directory="myrep1", pattern="mp3")
        p2 = Page(url="http://myurl2.com", directory="myrep2", pattern="mp3")

        r1 = RessourceFile(link="1.mp3", page=p1)
        r2 = RessourceFile(link="2.mp3", page=p1)
        r3 = RessourceFile(link="3.mp3", page=p1)
        # Doublon entre r3 et r4 sur deux pages differentes
        r4 = RessourceFile(link="3.mp3", page=p2)
        r5 = RessourceFile(link="4.mp3", page=p2)
        r6 = RessourceFile(link="5.mp3", page=p2)

        p1.ressources = [r1, r2, r3]
        p2.ressources = [r4, r5, r6]
        self.assertEqual(3, len(p1.ressources))
        self.assertEqual(3, len(p2.ressources))

        fd = FileDownloader(page=p1)
        fd.add_download_page(p2)
        self.assertEqual(2, len(fd.pages))

        for p in fd.pages:
            fd.global_ressources.update(p.ressources)

        self.assertEqual(5, len(fd.global_ressources))
