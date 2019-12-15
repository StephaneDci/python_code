# -*- coding: utf-8 -*-

from camptocamp import logger, nb_workers
from camptocamp.c2cparser import C2CParser
from camptocamp.DAO.dao_interface import InterfaceDAO
from camptocamp.voie import Voie
from concurrent.futures import ThreadPoolExecutor, as_completed

# ------------------------------------------------------------------------------------------------------
# Classe Principale de Processing permettant de traiter les entrées de l'utilisateur pour le parsing.
# Version avec Multithreading pour permettre 1 thread par voie
# Auteur : SDI
# Date   : 21/08/2019
# Evol   : 13/09/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights
# ------------------------------------------------------------------------------------------------------


class Processing:
    """
    Classe pour le processing du parsing des voies
    """
    def __init__(self, userinput, backends, update=False):
        """
        Initialisation de la classe de Processing pour le parsing des voies
        :param userinput: un waypoint, une url de voie ou une liste d'url de voies
        :param backends: liste des backend de persistence
        :param update: True pour reparser les voies existantes, False pour skip si dejà existante
        """
        logger.info('Processing avec backends={}, maj={}'.format(backends, update))
        self.userinput = userinput
        self.backends = backends
        self.update = update
        self.count_parsed = 0              # compteur de voies parsées

    def parse(self):
        """
        Wrapper pour l'execution du parser permettant de clore proprement le webdriver
        """
        try:
            self.execute_parser()
        except AttributeError:
            pass
        finally:
            logger.info("Nombre de voie parsées : {}".format(self.count_parsed))
            logger.info("End of Parsing Program.")

    def execute_parser(self):
        """
        Execution du parser selon les inputs fournies par l'utilisateur
        :return:
        """
        if isinstance(self.userinput, list):
            logger.debug(" Parsing d'une liste en input")
            self.process_list()

        # Il faut Gérer le cas de figure ou la chaine fournie est un waypoint ;-)
        elif isinstance(self.userinput, str):
            logger.debug(" Parsing d'une chaine en input => conversion en list")
            liste = list()
            liste.append(self.userinput)
            self.userinput = liste
            self.process_list()

    def process_list(self):
        """
        Processing de tous les éléments d'une liste avec un thread par voie
        """
        listaparser = C2CParser.init_with_list(self.userinput)
        with ThreadPoolExecutor(max_workers=nb_workers) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(self.process_unit, url): url for url in listaparser}
            for future in as_completed(future_to_url):
                logger.info("Fin de traitement de {}".format(future_to_url[future]))

    def process_unit(self, urlvoie):
        """
        Processing unitaire d'une voie
        :param urlvoie: url de la voie à Parser
        :return: 0 si pas de parsing, 1 si parsing.
        """
        urlmin = C2CParser.get_urlvoie(urlvoie)
        exist = InterfaceDAO.check_exists(urlmin, self.backends)
        # Si la voie n'existe pas ou si nous sommes en mode update
        if not exist or self.update:
            logger.info("Voie: {} existante id: {}, mode Update: {}".format(urlvoie, exist, self.update))
            parser = C2CParser(urlmin)
            voie = Voie.from_c2cparser(parser)
            InterfaceDAO.persistance_voie(voie, self.backends)
            logger.info(voie)
            self.count_parsed = self.count_parsed + 1
            voie = None
            return 1
        else:
            logger.info("Voie déjà existante: {} et aucun reparsing demandé".format(urlmin))
            return 0


# --------------------------------------------------------------------------
# Execution principale du programme de Processing
# --------------------------------------------------------------------------
if __name__ == '__main__':

    # Exemple de déclaration des voies à parser
    listevoies = ['https://www.camptocamp.org/routes/54788/fr/presles-buis-point-trop-n-en-faut',
                  'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum',
                  'https://www.camptocamp.org/routes/54453/fr/les-trois-becs-la-pelle-roche-courbe-voie-des-parisiens',
                  'https://www.camptocamp.org/waypoints/104212/fr/telepherique-des-grands-montets']
    wpoint = 'https://www.camptocamp.org/waypoints/40766/fr/presles-eliane'
    testvoie = 'https://www.camptocamp.org/routes/53914'
    bimbam = 'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum'

    # Exemple d'utilisation du Parsing avec un waypoint et un backend db
    processor = Processing(wpoint, backends=['db'], update=False)
    processor.parse()
