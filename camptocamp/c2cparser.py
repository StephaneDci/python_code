# -*- coding: utf-8 -*-

""" ------------------------------------------------------------------------------------------------------
Parsing du site CamptoCamp avec Selenium (car contenu dynamique)
Scraping de la description de voie et des commentaires de toutes les sorties associées
Permet l'utilisation de liste de voies ou de waypoints.
Auteur : SDI
Date   : 21/08/2019
Objectif : educationnal purpose only. Merci de respecter les copyrights.
------------------------------------------------------------------------------------------------------ """

# Import des librairies nécessaire
import time
import re                           # Gestion des regex
from bs4 import BeautifulSoup       # Scrapping du site
from urllib.parse import urlparse   # Parsing des urls
from tqdm import tqdm               # Progress bar
from camptocamp import logger       # le logger pour l'application
from camptocamp import init_driver  # Fct d'initialisation du Driver

# --------------------------------------------------------------------------
# Classe de parsing du site pour une url de type route
# --------------------------------------------------------------------------


class C2CParser:
    # Attributs de la Classe
    # NB : le webdriver est crée en tant qu'instance de classe initialisé à None
    # Ce méchanisme évite de lancer le driver si l'utilisateur ne fait pas de parsing
    version = 2.0
    datesite = '01.09.2019'
    baseurl = 'https://www.camptocamp.org'
    driver = None

    # Construction du Parser
    def __init__(self, url, proxy=None, headless=True):
        logger.debug("Init de la classe {}".format(self.__class__))
        print("* Traitement de {}".format(url))
        C2CParser.init_cls_driver()         # Initialisation du driver
        self.urlvoie = url
        self.rawsoup = self.get_soup()

    def __repr__(self):
        return "C2CParser, urlvoie: '{}', rawsoup: {}".format(self.urlvoie, self.rawsoup)

    @classmethod
    def get_driver(cls):
        return cls.driver

    @classmethod
    def init_cls_driver(cls):
        # Si le driver de classe n'est pas initialisé nous le démarrons
        if cls.driver is None:
            cls.driver = init_driver()

    # initialisation à partir d'une liste de voies (avec ou sans waypoint)
    @staticmethod
    def init_with_list(listedevoies):
        listecomplete = list()
        filteredlist = C2CParser.filter_url(listedevoies)
        for i, voie in enumerate(filteredlist):
            if 'waypoints' in voie:
                ldc = C2CParser.get_list_from_waypoint(voie)
                listecomplete.extend(ldc)
            elif 'routes' in voie:
                listecomplete.append(voie)
        logger.info("Liste de voie complete : {}".format(listecomplete))
        return listecomplete

    # Récupération d'une liste de voie à partir d'un point de passage
    # Attention on ne récupère que les voies correspondants au type de course souhaité
    # Exemple https://www.camptocamp.org/waypoints/104212/fr/telepherique-des-grands-montets
    @staticmethod
    def get_list_from_waypoint(waypoint, typecourse='Escalade'):
        logger.info("Waypoint fourni! récupération des courses '{}' ...".format(typecourse))
        listedevoies = list()
        parser = C2CParser(waypoint)
        for h3 in parser.rawsoup.findAll('h3'):
            try:
                if h3.text.strip() == typecourse:
                    h3parent = h3.parent
                    for ln in h3parent.find_all('a'):
                        listedevoies.append(str(C2CParser.baseurl + ln.get('href')))
            except TypeError:
                continue
        print("\t{} voie(s) récupérée(s) à partir du waypoint.".format(len(listedevoies)))
        return listedevoies

    # Calcul du baseurl ie https://www.camptocamp.org avec l'url fournie en paramètre
    @staticmethod
    def get_baseurl(url):
        try:
            parse_url = list(urlparse(url))
            baseurl = parse_url[0] + "://" + parse_url[1]
            return baseurl
        except AttributeError:
            logger.warning("Attention Url non parsable {}".format(url))

    # Retourne une url de type: https://www.camptocamp.org/routes/171402
    # sans toute la description dans l'url ie /fr/voiedulevant...
    @staticmethod
    def get_urlvoie(url):
        try:
            exp = re.compile(C2CParser.baseurl + "/(routes|waypoints)/\d+")
            minurl = exp.match(url).group()
            return minurl
        except IndexError:
            logger.warning("Probleme avec : {}".format(url))

    @staticmethod
    def filter_url(liste_des_voies):
        logger.info("Filtrage des voies fournies...")
        filteredlistvoies = list()
        # Suppression des doublons (avec set) et Verification du baseurl
        # + minification urm
        for voie in set(liste_des_voies):
            if C2CParser.get_baseurl(voie) == C2CParser.baseurl:
                minurl = C2CParser.get_urlvoie(voie)
                filteredlistvoies.append(minurl)
        logger.debug(f"Liste voie AVANT filtrage: {liste_des_voies}")
        logger.debug(f"Liste voie APRES filtrage: {filteredlistvoies}")
        return dict.fromkeys(filteredlistvoies)

    # Récupération de l'objet soup afin de permettre l'extraction des informations
    def get_soup(self):
        logger.debug("Récuperation du parsing soup de la page {}".format(self.urlvoie))
        C2CParser.driver.get(self.urlvoie)
        time.sleep(1)
        html = C2CParser.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        self.rawsoup = soup
        return soup

    def get_titre(self):
        logger.debug("Récupération titre de la voie")
        soup = self.rawsoup
        try:
            titre = str(soup.find('h1').text)
            logger.info("Titre: {}".format(titre))
            return titre.strip()
        except:
            logger.error("Pas de titre trouvé")

    def get_approche(self):
        logger.debug("Récupération approche de la voie")
        soup = self.rawsoup
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
                logger.debug("pas de {} trouvé.".format(iddesc))
        logger.debug(approche)
        return approche

    def get_details_longueurs(self):
        logger.debug("Récupération détails des longueurs...")
        details = list()
        for exp in self.rawsoup.find_all('div', {'class': 'content markdown-content'}):
            for detail in exp.find_all('tr'):
                details.append(str(detail.text).replace('\n', ' '))
        return details

    def get_commentaires(self):
        logger.debug("Récupération des commentaires...")
        commentaires = list()
        for exp in self.rawsoup.find_all('div', {'class': 'content markdown-content'}):
            for comment in exp.find_all('p'):
                commentaires.append(comment.text)
        return " ".join(commentaires)

    def get_cotations(self):
        logger.debug("Récupération des cotations...")
        # Initialisation d'une liste des attributs à récupérer pour la cotation de la voie
        cotations = dict()
        liste = ['Cotation globale', 'Cotation libre', 'Cotation obligatoire', 'Cotation obligatoire',
                 'Engagement', 'Qualité de l\'équipement', 'Exposition rocher']
        for cote in liste:
            try:
                logger.debug("{} : {}".format(cote, self.rawsoup.find('span', title=cote).text.strip()))
                cotations[cote] = self.rawsoup.find('span', title=cote).text.strip()
            except AttributeError as atr_err:
                pass
        logger.debug(cotations)
        return cotations

    def get_alt_difficultes(self):
        # Récupération des hauteurs des difficultés
        logger.debug("Récupération des difficultés...")
        difficultes = dict()
        for diff in ['Altitude maximale', 'Dénivelé positif', 'Dénivelé des difficultés']:
            try:
                # Recherche du texte puis du parent et on avance à la balise suivante.
                address = self.rawsoup.find(text=diff)
                parent_tag = address.parent
                val = parent_tag.find_next().text
                # Remplacement car. spéciale par un espace
                difficultes[diff] = val.replace(u'\xa0', u' ')
            except AttributeError:
                logger.debug("Impossible de récupérer : {}".format(diff))
                continue
        logger.debug(difficultes)
        return difficultes

    def _get_url_outings(self):
        # Récupération de la page contenant la liste de toutes les sorties
        for link in self.rawsoup.findAll('a'):
            ln = str(link.get('href'))
            if '/outings?r' in ln:
                return ln

    def _get_urls_outings(self):
        outings_links = list()
        # Récupération de la page qui contient les liens de toutes les sorties
        try:
            pagedessorties = C2CParser.baseurl + self._get_url_outings()
            if pagedessorties is not None:
                C2CParser.driver.get(pagedessorties)
                time.sleep(1)
                html_outings = C2CParser.driver.page_source
                soup_outings = BeautifulSoup(html_outings, 'lxml')

                # pour ne garder que les sorties /outings/<digits>
                r = re.compile("/outings/[0-9]+")

                for links in soup_outings.findAll('a'):
                    ln = str(links.get('href'))
                    if r.match(ln):
                        outings_links.append(ln)
            return outings_links
        except TypeError:
            logger.warning('Probleme récupération page sortie')

    def get_outings(self):
        print("Récupération des sorties ...")
        urls_outing = self._get_urls_outings()

        # Boucle sur toutes les sorties page par page
        if urls_outing is None:
            return list(['aucune sortie'])
        else:
            logger.info("...Il y a {} sortie(s)".format(len(urls_outing)))
            details_sortie = list()
            for out in tqdm(urls_outing):
                # Chargement de la nouvelle page
                logger.debug("  => {}".format(out))
                C2CParser.driver.get(self.baseurl + out)
                # https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
                # https://selenium-python.readthedocs.io/waits.html
                time.sleep(1)   # Permet à la page de se charger (contenu dynamique)
                html_outing = C2CParser.driver.page_source
                soup_outing = BeautifulSoup(html_outing, 'lxml')
                try:
                    # Date de la sortie
                    date_sortie = soup_outing.find('span', attrs={'class': 'outing-date is-size-5'}).text.strip()
                    # Description de la sortie
                    details = "-- " + date_sortie + " -- "
                    for desc_sortie in soup_outing.find_all('div', {'class': 'content markdown-content'}):
                        details += "\n" + desc_sortie.text
                    details_sortie.append(details)
                except AttributeError as err:
                    logger.warning("Exception: {}".format(err))

            return details_sortie


# --------------------------------------------------------------------------
# Execution du parser
# --------------------------------------------------------------------------
if __name__ == '__main__':

    urlvoie = 'https://www.camptocamp.org/routes/53914'
    c2cparser = C2CParser(urlvoie)
