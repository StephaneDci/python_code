# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------------------
# Classe de Download de Ressources sur des Pages Web. Multithread.
# Auteur : SDI
# Date   : 15/02/2020
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# Python >= 3.8 + modules dans les requirements
# ------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
import re
import requests
from urllib.parse import urlparse
from typing import List, Set, Union
from tqdm import tqdm
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from downloader.utils.netw import make_get_requests
from downloader.utils.system import create_target_directory, verify_if_file_exists
from downloader import logger

# --------------------------------------------------------------------------
# Data Classe RessourceFile : Permet de définir une ressource à télécharger
# --------------------------------------------------------------------------
@dataclass
class RessourceFile:
    link: str
    page: Page
    headers: {} = field(repr=False, default_factory=lambda: {})
    downloaded: bool = field(default=False)

    # --------------------------------------------------------------------------
    # Déclaration des propriétés de la classe
    # peuvent être appelée dans le code avec self.<nom_de_la_methode>
    # --------------------------------------------------------------------------

    @property
    def filename(self):
        return self.link.rsplit('/', 1)[-1]

    @property
    def filepath(self):
        return os.path.join(self.page.directory, self.filename)

    @property
    def size(self):
        return int(self.headers.get('Content-Length', 0))

    # --------------------------------------------------------------------------
    # Réecriture de l'opérateur d'égalité des ressources (onse base uniquement sur le lien http)
    # --------------------------------------------------------------------------
    def __eq__(self, other):
        if type(other) is type(self):
            return self.link == other.link
        return False

    def __hash__(self):
        return hash(self.link)


# --------------------------------------------------------------------------
# Classe WebRessourcePattern
# TODO implement exclude patterns
# --------------------------------------------------------------------------
class WebRessourcePattern:
    default_pattern = r"http\S+"

    def __init__(self, extension: str, include_pattern: str = ""):
        self.extension = extension
        self.include_pattern = include_pattern
        self.re_pattern = self.set_regex_pattern()

    def set_regex_pattern(self) -> str:
        if not isinstance(self.include_pattern, str) and not isinstance(self.extension, str):
            raise Exception("Les patterns doivent être des instances de strings")
        if self.include_pattern != "":
            return WebRessourcePattern.default_pattern + \
               self.include_pattern + r"\S+" + self.extension
        else:
            return WebRessourcePattern.default_pattern + \
               self.include_pattern + self.extension

    @staticmethod
    def get_pattern(pattern: Union[str, WebRessourcePattern]) -> str:
        if isinstance(pattern, str):
            return str(WebRessourcePattern.default_pattern + pattern)
        elif isinstance(pattern, WebRessourcePattern):
            return str(pattern)
        else:
            raise Exception("pattern must be string or WebRessourcePattern")

    # --------------------------------------------------------------------------
    # Surchage de l'affichage pour l'utilisation du pattern via src(ptrn)
    # --------------------------------------------------------------------------
    def __str__(self):
        return self.re_pattern


# --------------------------------------------------------------------------
# Classe Page:
# TODO handle requests with BasicAuth
# --------------------------------------------------------------------------
class Page:
    """ Representation of a web Page with ressources inside """
    DEFAULT_DIR = "DL"

    def __init__(self, url: str, pattern: Union[str, WebRessourcePattern], directory: str = "", proxies: str = ""):
        """
        :param url: string: url page where are ressources to download.
        :param pattern: <str> or Webpattern: if str : you must specify extension
        :param directory: string: local directory where to store downloaded ressources on host.
        :param proxies: <dict> : proxy parameters. ie "127.0.0.1:3128"
        """
        self.url = url
        self.pattern = WebRessourcePattern.get_pattern(pattern)
        self.directory = self.set_directory(directory)
        self.proxies = self.set_proxies(proxies)
        self.ressources = list()                               # type: List[RessourceFile]
        self.srcpage = ""                                      # type: str
        self.session = requests.Session()

    # --------------------------------------------------------------------------
    # Déclaration des propriétés de la classe
    # peuvent être appelée dans le code avec self.<nom_de_la_methode>
    # --------------------------------------------------------------------------
    @property
    def size_ressources(self):
        return sum(r.size for r in self.ressources)

    @property
    def nbr_download(self):
        return sum(r.downloaded for r in self.ressources)

    # --------------------------------------------------------------------------
    # Déclaration des méthodes de la classe Page
    # --------------------------------------------------------------------------
    def set_directory(self, directory: str) -> str:
        """ Define directory to create based on url IF no directory parameter provided
        ie  for 'http://www.audiolitterature.com/michel-onfray-contre-histoire-de-la-philosophie-volume-1/'
            return 'michel-onfray-contre-histoire-de-la-philosophie-volume-1'"""
        if not isinstance(directory, str):
            raise Exception("Directory must be a string")
        return str(Page.DEFAULT_DIR + '\\' + urlparse(self.url).path[1:].rstrip('/')).replace('/', '\\') \
            if directory == "" else directory

    def set_proxies(self, proxies: str) -> dict:
        if not isinstance(proxies, str):
            raise Exception("Proxy Should be string: ie '127.0.0.1:3128' or '' ")
        if proxies != "" and ":" not in proxies:
            raise Exception("Proxy Must be in format ip:port")
        return {"http": "{}".format(proxies), "https": "{}".format(proxies)} \
            if proxies != "" else {"http": None, "https": None}

    def process(self):
        """ Web Page Processing: create directories and getting ressources list. """
        try:
            logger.info(f"\nPage {self.url}")
            create_target_directory(self.directory)
            self.srcpage = make_get_requests(self.url, proxies=self.proxies, session=self.session).text
            self.ressources = list(self.get_ressources_list_matching_pattern(self.srcpage, self.pattern))
            self.set_ressources_infos_parallel(self.ressources)
            logger.info(f"Taille totale: {self.size_ressources//1024//1024}Mo ({self.size_ressources//1024} Ko)\n")
        except Exception as exc:
            logger.exception(exc)
        finally:
            logger.debug(f"Fin de Processing de la Page {self.url}")

    def get_ressources_list_matching_pattern(self, srcpage: str, pattern: str) -> List[RessourceFile]:
        """ Get List of ressources on url matching regex pattern in a href link
        :return: list of ressources matching pattern for page """
        logger.debug(f"Searching ressources matching pattern '{pattern}' on url '{self.url}'")
        try:
            links = BeautifulSoup(srcpage, 'lxml').find_all('a', href=True)
            matching_ressources = list()
            for link in links:
                if re.match(pattern, lk:=str(link['href'])):
                    matching_ressources.append(RessourceFile(link=lk, page=self))
                    logger.debug(lk)
            logger.info(f"{len(matching_ressources)} ressources found!")
            # Remove duplicate and preserve order :
            return list(dict.fromkeys(matching_ressources))
        except TypeError as typ:
            logger.warning(f"No ressources found (msg : {typ})")
            return []

    def set_unit_ressource_infos(self, res: RessourceFile):
        head = make_get_requests(res.link, verb='HEAD', proxies=self.proxies, session=self.session)
        if head.headers is not None:
            res.headers = head.headers
        else:
            logger.warning(f"Probleme récupération headers pour ressource {res}")

    # Parallelisation
    def set_ressources_infos_parallel(self, ressources_list: List[RessourceFile]):
        with ThreadPoolExecutor(max_workers=4) as executor:
            future = {executor.submit(self.set_unit_ressource_infos, r): r for r in ressources_list}
            for f in as_completed(future):
                logger.debug("[Headers] Fin {}".format(future[f]))

    # --------------------------------------------------------------------------
    # Surchage des opérateurs
    # --------------------------------------------------------------------------

    def __repr__(self):
        return f"url: {self.url}\n" \
               f"directory: {self.directory}\n" \
               f"pattern: {self.pattern}\n" \
               f"proxies: {self.proxies}\n"

    def __eq__(self, other):
        if type(other) is type(self):
            return (self.url == other.url and
                    self.pattern == other.pattern)
        return False


# --------------------------------------------------------------------------
# Classe FileDownloader
# --------------------------------------------------------------------------
class FileDownloader:
    """ Classe to Handle the Download of Ressources on webpages. """
    def __init__(self, page: Union[Page, List[Page]], nmax_threads: int = 10):
        """ :param page: page: list of page or page object """
        self.MAX_THREADS = nmax_threads
        self.session = requests.Session()
        self.pages = list()                  # type: List[Page]
        self.global_ressources = set()       # type: Set[RessourceFile]
        self.add_download_page(page)

    # --------------------------------------------------------------------------
    # Déclaration des méthodes de la classe FileDownloader
    # --------------------------------------------------------------------------
    def add_download_page(self, page_or_list: Union[Page, List[Page]]):
        if page_or_list not in self.pages:
            if isinstance(page_or_list, Page):
                self.pages.append(page_or_list)
            elif isinstance(page_or_list, list):
                for p in page_or_list:
                    self.pages.append(p)
            else:
                raise Exception(f"Operation nor supported on object other than Page or list(Page)")

    def process(self):
        logger.info(" *** Initialisation : Processing des Pages *** ")
        try:
            for p in tqdm(self.pages, position=0, desc="Processing des Pages"):
                p.process()
                self.global_ressources.update(p.ressources)

            logger.info(f"\n*** Processing des Downloads: {len(self.global_ressources)} ressources à télécharger ***")
            self.download_ressources_parallel(self.global_ressources)

        except Exception as exc:
            logger.exception(exc)
        else:
            logger.info("Traitement réussi.")
        finally:
            logger.info("Fin de traitement.")

    # TODO fait partie d'une lib utilitaire en rendant plus générique
    def download_unit(self, res: RessourceFile) -> str:
        logger.debug(f"Downloading {res.link}")
        filename, filepath = res.filename, res.filepath

        downloaded, msg = verify_if_file_exists(filepath, res.size)
        logger.debug(msg)

        if not downloaded:
            rep = make_get_requests(res.link, stream=True, proxies=res.page.proxies, session=self.session)

            with open(filepath, "wb") as f:
                for chunk in rep.iter_content(chunk_size=2048):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        else:
            return "FILE ALREADY EXIST"

        success, msg = verify_if_file_exists(filepath, res.size)
        if success:
            res.downloaded = True
            return "FILE OK"
        else:
            logger.exception(msg)
            raise Exception(msg)

    def download_ressources_parallel(self, global_ressources_list: Set[RessourceFile]):
        with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
            future = {executor.submit(self.download_unit, r): r for r in global_ressources_list}
            pbar = tqdm(total=len(global_ressources_list), position=0)
            for f in as_completed(future):
                pbar.update()
                pbar.set_description("Progression Totale: ")
                logger.debug(f"{f.result()} : {future[f]}")

    def __repr__(self):
        return f"pages: {self.pages}\n"


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
if __name__ == '__main__':

    # Utilisation:
    # Ajout de pages à télécharger:
    p1 = Page(url="https://www.audiolitterature.com/michel-onfray-traite-datheologie/", pattern="mp3")

    # Sans préciser le répertoire celui-ci sera déduit de l'url
    p2 = Page("https://www.audiolitterature.com/michel-onfray-nietzsche-en-quatre-questions/", "mp3")

    # Exemple en utilisant les patterns
    # wbp = WebRessourcePattern(extension="mp3", include_pattern="onfray")
    # p3 = Page(url="https://www.audiolitterature.com/...", pattern=wbp)

    # Création du downloader
    fd = FileDownloader(p1)

    # Ajout d'une page ...
    fd.add_download_page(p2)

    # Ajout d'une liste de page
    p3 = Page("https://www.audiolitterature.com/michel-onfray-breve-encyclopedie-du-monde-saison-4/", "mp3")
    p4 = Page("https://www.audiolitterature.com/michel-onfray-le-souci-des-plaisirs/", "mp3")
    p5 = Page("https://www.audiolitterature.com/michel-onfray-le-pur-plaisir-dexister/", "mp3")
    lst = [p3, p4, p5]
    fd.add_download_page(lst)

    # Ou ajout des pages comme ceci evidemment
    fd.add_download_page([Page("https://www.audiolitterature.com/michel-onfray-breve-encyclopedie-du-monde-saison-3/", "mp3"),
                         Page("https://www.audiolitterature.com/michel-onfray-breve-encyclopedie-du-monde-saison-2/", "mp3"),
                         Page("https://www.audiolitterature.com/michel-onfray-breve-encyclopedie-du-monde-saison-1/", "mp3")])


    # Lancement du processins et des téléchargements !
    fd.process()
