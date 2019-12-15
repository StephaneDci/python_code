# -*- coding: utf-8 -*-

""" ------------------------------------------------------------------------------------------------------
Parsing du site CamptoCamp avec Selenium (car contenu dynamique)
Scraping de la description de voie et des commentaires de toutes les sorties associées
Permet l'utilisation de liste de voies ou de waypoints.
Auteur : SDI
Date   : 21/08/2019
Objectif : educationnal purpose only. Merci de respecter les copyrights.
"""

# --------------------------------------------------------------------------
# Import des librairies nécessaire
# --------------------------------------------------------------------------
import time
import re                                                       # Gestion des regex
from bs4 import BeautifulSoup                                   # Scrapping du site
from urllib.parse import urlparse                               # Parsing des urls
from tqdm import tqdm                                           # Progress bar
from camptocamp import logger                                   # le logger pour l'application
from camptocamp import init_driver                              # Fct d'initialisation du Driver
from selenium.common.exceptions import TimeoutException         # Gestion des timeout


# --------------------------------------------------------------------------
# Classe de parsing du site pour une url de type route
# --------------------------------------------------------------------------


class C2CParser:
    """
    Classe pour le parsing des voies d'escalade du site CamptoCamp.
    Permet la prise en compte des 'routes' et des 'waypoints'.
    """

    # Attributs de la Classe
    # Le webdriver est crée en tant qu'instance de classe initialisé à None
    # Ce méchanisme évite de lancer le driver si l'utilisateur ne fait pas de parsing
    version = 2.0
    datesite = '01.09.2019'
    baseurl = 'https://www.camptocamp.org'

    def __init__(self, url, savehtml=False):
        """
        Initialisation du parser. Appelé pour chaque nouvelle url.
        :param url: l'url à parser
        :param savehtml: True pour sauver le html des voies dans un fichier (debug) (1 fichier par voie)
        """
        if url is not None:
            self.driver = init_driver()
            logger.debug("Init de la classe {}".format(self.__class__))
            logger.info("Traitement de {}".format(url))
            self.savehtml = savehtml
            self.urlvoie = url
            self.rawsoup = self.get_soup_from_url(url)

    def __del__(self):
        try:
            self.driver.quit()
        except AttributeError:
            pass

    # --------------------------------------------------------------------------
    # Méthode Statiques
    # --------------------------------------------------------------------------

    @staticmethod
    def init_with_list(listedevoies):
        """
        Traitement à partir d'une liste de voies :
        - Suppression des doublons
        - Expansion des waypoints (contenant d'autres voies)
        - Filtrage des urls de route contenant 'routes'
        :param listedevoies: liste de voie en input
        :return: liste de voie après traitement (liste)
        """
        liste = list()
        filteredlist = C2CParser.filter_url(listedevoies)
        for i, voie in enumerate(filteredlist):
            if 'waypoints' in voie:
                ldc = C2CParser.get_list_from_waypoint(voie)
                liste.extend(ldc)
            elif 'routes' in voie:
                liste.append(voie)
        logger.info("Liste de voie complete : {}".format(liste))
        return liste

    @staticmethod
    def get_list_from_waypoint(wp, typecourse='Escalade'):
        """
        Récupération d'une liste de voie à partir d'un point de passage (waypoint ou wp)
        Attention on ne récupère que les voies correspondants au type de course souhaité
        Exemple de wp:  https://www.camptocamp.org/waypoints/104212/fr/telepherique-des-grands-montets
        :param wp: url de waypoint
        :param typecourse: str du type de course ['Escalade', '?', ...]
        :return: liste des voies du waypoint
        """
        logger.info("Waypoint fourni! récupération des courses '{}'.".format(typecourse))
        listedevoies = list()
        parser = C2CParser(wp)
        for h3 in parser.rawsoup.findAll('h3'):
            try:
                if h3.text.strip() == typecourse:
                    h3parent = h3.parent
                    for ln in h3parent.find_all('a'):
                        listedevoies.append(str(C2CParser.baseurl + ln.get('href')))
            except TypeError as te:
                logger.error(te)
                continue
        logger.info("{} voie(s) récupérée(s) à partir du waypoint.".format(len(listedevoies)))
        return listedevoies

    @staticmethod
    def get_baseurl(url):
        """
        Calcul du baseurl ie https://www.camptocamp.org avec l'url fournie en paramètre
        :param url: url en input
        :return: baseurl
        """
        try:
            parse_url = list(urlparse(url))
            baseurl = parse_url[0] + "://" + parse_url[1]
            return baseurl
        except AttributeError:
            logger.warning("Attention Url non parsable {}".format(url))

    @staticmethod
    def get_urlvoie(url):
        """
        Retourne une url de type: https://www.camptocamp.org/routes/171402
        sans toute la description dans l'url ie /fr/voiedulevant...
        Uniquement pour des url de type routes ou waypoints
        :param url: url en input
        :return: url minifiée
        """
        try:
            exp = re.compile(C2CParser.baseurl + "/(routes|waypoints)/\d+")
            minurl = exp.match(url).group()
            return minurl
        except IndexError:
            logger.warning("Probleme avec : {}".format(url))

    @staticmethod
    def filter_url(liste_des_voies):
        """
        Filtre des urls sur le baseurl et suppression des doublons
        :param liste_des_voies: input
        :return: dictionnaire de voies uniques et minifiées
        """
        logger.info("Filtrage des voies fournies.")
        filteredlistvoies = list()
        for voie in set(liste_des_voies):
            if C2CParser.get_baseurl(voie) == C2CParser.baseurl:
                minurl = C2CParser.get_urlvoie(voie)
                filteredlistvoies.append(minurl)
        logger.debug(f"Liste voie AVANT filtrage: {liste_des_voies}")
        logger.debug(f"Liste voie APRES filtrage: {filteredlistvoies}")
        return dict.fromkeys(filteredlistvoies)

    def get_soup_from_url(self, url, timeout=10, sleep_sec=0.5):
        """
        Récupération du parsing soup d'une url pour la recherche des éléments
        :param url: url
        :param timeout: timeout pour le chargement
        :param sleep_sec: délai entre chargement des différentes pages
        :return: objet BeautifulSoup
        """
        logger.debug("Récuperation Beautiful soup de la page {}".format(url))
        # https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
        # https://selenium-python.readthedocs.io/waits.html
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            time.sleep(sleep_sec)
            html = self.driver.page_source
            if self.savehtml:
                filename = url.replace(C2CParser.baseurl, '')
                filename = filename.replace('/', '_').replace('?', '_').replace('=', '_') + '.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
            soup = BeautifulSoup(html, 'lxml')
            return soup
        except TimeoutException as ex:
            logger.warning("Exception Timeout : {} ".format(ex))

    def get_titre(self):
        """
        Récupération du Titre de la voie
        :return: le titre de la voie
        """
        logger.debug("Récupération titre de la voie {}".format(self.urlvoie))
        soup = self.rawsoup
        try:
            titre = str(soup.find('h1').text)
            logger.info("Titre: {}".format(titre))
            return titre.strip()
        except:
            logger.error("Pas de titre trouvé")

    def get_area(self):
        """
        Récupération de la localisation de la voie
        :return: liste decrivant la localisation (Pays / Regions / Dpt)
        """
        area = list()
        for a in self.rawsoup.find_all('span', {'class': 'area-link'}):
            area.append(a.text.strip())
        return area

    def get_approche(self):
        """
        Récupération des approches d'une voie
        :return: dictionnaire avec les clés 'approche', 'itineraire', 'descente'
        """
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
        """
        Récupération des détails des longueurs d'une voie
        :return: liste avec une entrée par longueur
        """
        logger.debug("Récupération détails des longueurs.")
        details = list()
        for exp in self.rawsoup.find_all('div', {'class': 'content markdown-content'}):
            for detail in exp.find_all('tr'):
                details.append(str(detail.text).replace('\n', ' '))
        return details

    def get_commentaires(self):
        """
        Récupération des commentaires d'une voie
        :return: string contenant les commentaires
        """
        logger.debug("Récupération des commentaires")
        commentaires = list()
        for exp in self.rawsoup.find_all('div', {'class': 'content markdown-content'}):
            for comment in exp.find_all('p'):
                commentaires.append(comment.text)
        return " ".join(commentaires)

    def get_cotations(self):
        """
        Récupération des différentes cotations relatives à une voie
        :return: dictionnaire des cotations
        """
        logger.debug("Récupération des cotations de la voie")
        # Initialisation d'une liste des attributs à récupérer pour la cotation de la voie
        cotations = dict()
        liste = ['Cotation globale', 'Cotation libre', 'Cotation obligatoire', 'Cotation obligatoire',
                 'Engagement', 'Qualité de l\'équipement', 'Exposition rocher']
        for cote in liste:
            try:
                logger.debug("{} : {}".format(cote, self.rawsoup.find('span', title=cote).text.strip()))
                cotations[cote] = self.rawsoup.find('span', title=cote).text.strip()
            except AttributeError:
                pass
        logger.debug(cotations)
        return cotations

    def get_alt_difficultes(self):
        """
        Récupération des hauteurs des difficultés
        :return: dictionnaire des difficultés
        """
        logger.debug("Récupération des difficultés de la voie.")
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
        """
        Récupération de la page contenant la liste de toutes les sorties
        :return: url de la page listant les sorties d'une voies
        """
        for link in self.rawsoup.findAll('a'):
            ln = str(link.get('href'))
            if '/outings?r' in ln:
                return ln

    def _get_urls_outings(self):
        """
        Récupère toutes les sorties associées à une voie
        :return: liste contenant les url de toutes les sorties
        """
        outings_links = list()
        # Récupération de la page qui contient les liens de toutes les sorties
        try:
            pagedessorties = C2CParser.baseurl + self._get_url_outings()
            if pagedessorties is not None:
                soup_outings = self.get_soup_from_url(pagedessorties)

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
        """
        Récupération des informations de toutes les sorties d'une voie
        :return: une liste avec un élément par sortie
        """
        logger.info("Récupération des sorties de {}".format(self.urlvoie))
        urls_outing = self._get_urls_outings()

        # Boucle sur toutes les sorties page par page
        if urls_outing is None:
            return list(['aucune sortie'])
        else:
            logger.info("Il y a {} sortie(s) pour {}".format(len(urls_outing), self.urlvoie))
            list_sorties = list()
            for out in tqdm(urls_outing):
                s = self.getouting_unit(out)
                list_sorties.append(s)
            return list_sorties

    def getouting_unit(self, unesortie):
        """
        Récupération des informations d'une sortie
        :param unesortie: url de la sortie
        :return:
        """
        # Chargement de la nouvelle page
        logger.debug("  => {}".format(unesortie))
        soup_outing = self.get_soup_from_url(self.baseurl + unesortie)
        try:
            # Date de la sortie
            date_sortie = soup_outing.find('span', attrs={'class': 'outing-date is-size-5'}).text.strip()
            # Description de la sortie
            details = "-- " + date_sortie + " -- "
            for desc_sortie in soup_outing.find_all('div', {'class': 'content markdown-content'}):
                details += "\n" + desc_sortie.text
        except AttributeError as err:
            logger.warning("Exception: {}".format(err))
        else:
            return details

    @staticmethod
    def to_mock_function():
        return "Fonction non mockee"


# --------------------------------------------------------------------------
# Execution du parser si la classe est appelée en direct
# --------------------------------------------------------------------------
if __name__ == '__main__':
    urlvoie = 'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum'
    # Pour récupérer la page principale
    c2cparser = C2CParser(urlvoie)
    # Pour récupérer le titre
    # c2cparser.get_titre()
    # .....
