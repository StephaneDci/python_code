# -*- coding: utf-8 -*-

from camptocamp import logger, Session, init_driver
from camptocamp.c2cparser import C2CParser
from camptocamp.DAO.db_model import VoieDb
from camptocamp.voie import Voie

# ------------------------------------------------------------------------------------------------------
# Classe Principale de Processing permettant de traiter les entrées de l'utilisateur
# Auteur : SDI
# Date   : 21/08/2019
# Evol   : 13/09/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights
# ------------------------------------------------------------------------------------------------------


class Processing:

    def __init__(self, userinput, persistance='db', update=False):
        logger.info('Processing avec persistance={}, maj={}'.format(persistance, update))
        self.userinput = userinput
        self.persistance = persistance
        self.update = update

    @staticmethod
    def query(value):
        session = Session()
        # print(session.query(VoieDb).filter(VoieDb.cotationG.contains(value)).all())
        # filters = {'nblongueurs': '4'}
        # print(session.query(VoieDb).filter_by(**filters).all())

        filter = (VoieDb.nblongueurs > 5)
        r = session.query(VoieDb).filter(*filter).all()
        print(r)

        # filters = session.query(VoieDb).filter(
        #    VoieDb.nblongueurs > 10).all()
        # print(filters)

    # Wrapper pour le parsing
    def parse(self):
        try:
            self.execute_parser()
        finally:
            C2CParser.get_driver().quit()
            logger.debug('Killing webDrivers.')
            logger.info("End of Parsing Program.")

    # Méthode principale
    def execute_parser(self):
        if isinstance(self.userinput, list):
            logger.debug(" Parsing d'une liste en input")
            self.process_list()
        # Il faut Gérer le cas de figure ou la chaine fournie est un waypoint ;-)
        elif isinstance(self.userinput, str):
            logger.debug(" Parsing d'une chaine en input, conversion en list")
            liste = list()
            liste.append(self.userinput)
            self.userinput = liste
            self.process_list()

    # Traitement d'une liste en entrée
    def process_list(self):
        listaparser = C2CParser.init_with_list(self.userinput)
        for voie in listaparser:
            self.process_unit(voie)

    # Traitement d'une voie
    def process_unit(self, voie):
        urlmin = C2CParser.get_urlvoie(voie)
        exist = self.check_exists(urlmin)
        if not exist or self.update:
            logger.info("Voie existante id: {}, mode Update: {}".format(exist, self.update))
            logger.info("Parsing en cours...")
            parser = C2CParser(urlmin)
            v = Voie.from_c2cparser(parser)
            self.persistance_voie(v)
            print(v)
        else:
            logger.info("Voie déjà existante en DB: {} et aucun update demandé".format(urlmin))

    def check_exists(self, urlvoie):
        if self.persistance == 'db':
            return VoieDb.exists(urlvoie)
        if self.persistance == 'pickle':
            print("Pickle existance not implemented yet, return false")
            return False

    def persistance_voie(self, voie):
        if self.persistance == 'db':
            voiedb = VoieDb.from_voie(voie)
            voiedb.insert()
        if self.persistance == 'pickle':
            voie.pickle_persistence()


# --------------------------------------------------------------------------
# Execution principale du programme de Processing
# --------------------------------------------------------------------------
if __name__ == '__main__':

    # Déclaration des voies à parser
    listevoies = ['https://www.camptocamp.org/routes/54788/fr/presles-buis-point-trop-n-en-faut',
                  'https://www.camptocamp.org/routes/171402/fr/presles-eliane-bim-bam-boum',
                  'https://www.camptocamp.org/routes/54453/fr/les-trois-becs-la-pelle-roche-courbe-voie-des-parisiens',
                  'https://www.camptocamp.org/waypoints/104212/fr/telepherique-des-grands-montets']
    wpoint = 'https://www.camptocamp.org/waypoints/40766/fr/presles-eliane'
    testvoie = 'https://www.camptocamp.org/routes/53914'
    testvoie2 = 'https://www.camptocamp.org/routes/164063'

    # Parsing
    processor = Processing(wpoint, persistance='db', update=True)
    processor.parse()

    # Tests de requêtage
    # Processing.query('TD')
