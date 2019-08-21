# -*- coding: utf-8 -*-

"""
Parsing du site CamptoCamp avec Selenium (car nécessite javascript pour le rendu du site)
Scraping de la description de la voie et des commentaires de toutes les sorties.
Auteur : SDI
Date   : 21/08/2019
"""

# Import des librairies nécessaire
import re                           # regex
import logging                      # pour les fonction de logging
from bs4 import BeautifulSoup       # pour le scrapping du site
from urllib.parse import urlparse   # Parsing des urls

# Librairies pour Selenium Chromedriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Options_chrome
from selenium.webdriver.support.ui import WebDriverWait

# Configuration du logging pour les classes
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(asctime)s - %(message)s',
                    datefmt='%I:%M:%S %p')
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Classe Définition de la classe Voie permettant le stockage des attributs
# --------------------------------------------------------------------------
class Voie:
    def __init__(self, url):
        self.url = url                  # L'url de la voie : baseurl/routes/54788/fr/presles-buis-point-trop-n-en-faut
        self.titre = ""                 # Titre de la voie : Presles - Buis : Point trop n'en faut
        self.raw = None                 # L'attribut BeautifulSoup pour le parsing
        self.approche = dict()          # Approche / Itinéraire / Descente
        self.longueurs = list()         # Description des longueurs de la voie
        self.commentaires = ""
        self.cotations = dict()         # Récupération des différentes cotations (dictionnaire)
        self.remarques = ""
        self.url_sorties = ""           # url contenant les liens vers les sorties (ie outings?r=54788)
        self.urls_sorties = list()      # liste des urls de toutes les sorties
        self.sorties = list()           # Contenu des sorties

    # Redéfinition pour l'affichage de la voie
    def __str__(self):
        return "\n" \
               "Voie : {} \n" \
               " URL : {} \n" \
               " Approche : {} \n" \
               " Itinéraire : {} \n" \
               " Nombre de sorties : {} \n" \
               " Details longueurs : \n{}".format(
                                            self.titre,
                                            self.url,
                                            self.approche.get('approche'),
                                            self.approche.get('itineraire'),
                                            len(self.sorties),
                                            '\n'.join(self.longueurs))


# --------------------------------------------------------------------------
# Classe de parsing du site CamptoCamp
# --------------------------------------------------------------------------
class C2C:
    version = 1.0
    datesite = '21.08.2019'
    baseurl = 'https://www.camptocamp.org'

    def __init__(self, listevoies):
        self.voies = self.filter_url(listevoies)
        self.proxies = {"http": None, "https": None}
        self.chromedriver = r"E:\\Logiciels\\Developpement\\chromedriver\\chromedriver_76.exe"
        self.driver = self.set_driver()

    # Driver chrome headless (prendre le driver ici http://chromedriver.chromium.org/downloads)
    # Il faut prendre la même version que Chrome installée sur le PC
    # https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug
    def set_driver(self):
        logger.info("Initialisation Chromedriver ...")
        options = Options_chrome()
        options.headless = True
        driver = webdriver.Chrome(options=options,
                                  executable_path=self.chromedriver)
        return driver

    # Calcul du baseurl ie https://www.camptocamp.org
    def get_baseurl(self, url):
        try:
            parse_url = list(urlparse(url))
            baseurl = parse_url[0]+"://"+parse_url[1]
            return baseurl
        except AttributeError:
            logger.warning("Attention Url non parsable {}".format(url))

    def parsing_voies(self):
        voies = list()
        for voieurl in self.voies:
            logger.info("Traitement de {} ...".format(voieurl))
            v = Voie(voieurl)
            v.raw = self.get_soup(v)
            v.titre = self.get_titre(v)
            v.cotations = self.get_cotations(v)
            v.approche = self.get_approche(v)
            v.longueurs = self.get_details_longueurs(v)
            v.commentaires = self.get_commentaires(v)
            v.url_sorties = self.get_url_outings(v)
            v.urls_sorties = self.get_urls_outings(v)
            v.sorties = self.get_outings(v)
            voies.append(v)
        return voies

    def filter_url(self, listevoies):
        logger.info("Filtrage des voies fournies...")
        filteredlistvoies = list()
        # Suppression des doublons et Verification du baseurl
        for voie in set(listevoies):
            if self.get_baseurl(voie) == C2C.baseurl:
                filteredlistvoies.append(voie)
        logging.debug(f"Liste voie AVANT filtrage: {listevoies}")
        logging.debug(f"Liste voie APRES filtrage: {filteredlistvoies}")
        return dict.fromkeys(filteredlistvoies)

    def get_soup(self, voie):
        logger.info("Récuperation du parsing de la page...")
        dic = dict()
        self.driver.get(voie.url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def get_titre(self, voie):
        soup = voie.raw
        # TODO add try/catch
        titre = str(soup.find('h1').text)
        return titre

    def get_approche(self, voie):
        soup = voie.raw
        # approche, itineraire et descente:
        # Ce sont les éléments qui suivent les balises <h3> avec id=[liste_id]
        approche = dict()
        liste_id = ['approche', 'itineraire', 'descente']
        # https://stackoverflow.com/questions/42809252/beautifulsoup-get-tags-after-p-tag-after-h3-and-br-tag-between-p
        for iddesc in liste_id:
            try:
                header = soup.find('h3', {'id': iddesc})
                nextnode = header.nextSibling.nextSibling
                approche[iddesc] = nextnode.get_text(strip=True)
            except AttributeError:
                logger.warning("pas de {} pour : {}".format(iddesc, voie.url))
        logger.debug(approche)
        return approche

    def get_decente(self, voie):
        soup = voie.raw
        try:
            descente = soup.find('h3', {'id': 'descente'}).text.lstrip().rstrip()
            return str(descente)
        except AttributeError:
            logger.warning("erreur recuperation de la descente pour : {}".format(voie.url))

    def get_details_longueurs(self, voie):
        details = list()
        for exp in voie.raw.find_all('div', {'class': 'content markdown-content'}):
            for detail in exp.find_all('tr'):
                details.append(str(detail.text).replace('\n', ' '))
        return details

    def get_commentaires(self, voie):
        commentaires = list()
        for exp in voie.raw.find_all('div', {'class': 'content markdown-content'}):
            for comment in exp.find_all('p'):
                commentaires.append(comment.text)
        return " ".join(commentaires)

    def get_cotations(self, voie):
        # Initialisation d'une liste des attributs à récupérer pour la cotation de la voie
        cotations = dict()
        liste = ['Cotation globale', 'Cotation libre', 'Cotation obligatoire', 'Cotation obligatoire',
                 'Engagement', 'Qualité de l\'équipement', 'Exposition rocher']
        for cote in liste:
            try:
                # print("{} : {}".format(cote, voie.raw.find('span', title=cote).text.lstrip().rstrip()))
                cotations[cote] = voie.raw.find('span', title=cote).text.strip()
            except AttributeError as atr_err:
                pass
        logging.debug(cotations)
        return cotations

    def get_url_outings(self, voie):
        # Récupération de la page contenant la liste de toutes les sorties
        for link in voie.raw.findAll('a'):
            ln = str(link.get('href'))
            if '/outings?r' in ln:
                return ln

    def get_urls_outings(self, voie):
        outings_links = list()

        # Récupération de la page qui contient les liens de toutes les sorties
        self.driver.get(self.baseurl + voie.url_sorties)
        wait = WebDriverWait(self.driver, 10)
        html_outings = self.driver.page_source
        soup_outings = BeautifulSoup(html_outings, 'lxml')

        # pour ne garder que les sorties /outings/<digits>
        r = re.compile("/outings/[0-9]+")

        for links in soup_outings.findAll('a'):
            ln = str(links.get('href'))
            if r.match(ln):
                outings_links.append(ln)
        return outings_links

    def get_outings(self, voie):
        logger.info("Récupération des sorties ...")
        details_sortie = list()

        # Boucle sur toutes les sorties page par page
        for out in voie.urls_sorties:
            # Chargement de la nouvelle page
            self.driver.get(self.baseurl + out)
            html_outing = self.driver.page_source
            soup_outing = BeautifulSoup(html_outing, 'lxml')
            try:
                # Date de la sortie
                date_sortie = soup_outing.find('span', attrs={'class': 'outing-date is-size-5'}).text.strip()
                # Description de la sortie
                for desc_sortie in soup_outing.find_all('div', {'class': 'content markdown-content'}):
                    details_sortie.append(str(date_sortie + " " + desc_sortie.text))
            except:
                details_sortie.append(out + ": Aucun commentaire pour cette sortie")

        return details_sortie


# --------------------------------------------------------------------------
# Execution principale du programme
# --------------------------------------------------------------------------
if __name__ == '__main__':
    voies = ['https://www.camptocamp.org/routes/54788/fr/presles-buis-point-trop-n-en-faut',
             'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum']
    c2c = C2C(voies)
    liste_voies = c2c.parsing_voies()
    for v in liste_voies:
        print(v)
    print("Fin des traitements")
