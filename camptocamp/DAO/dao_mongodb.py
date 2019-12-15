from pymongo import MongoClient
from camptocamp import logger
from camptocamp import mongodburl
from pprint import pprint
from pymongo.errors import ServerSelectionTimeoutError
# --------------------------------------------------------------------------
# Classe DAO pour la persistence des Données dans MongoDB
# --------------------------------------------------------------------------


class MongoDbDAO:
    """
    Classe pour communiquer avec le backend MongoDb
    """

    def __init__(self, url_connection=mongodburl, database='camptocamp'):
        """
        Constructeur pour intialisation une connection MongoDB sur une collection
        :param url_connection: endpoint de connection vers MongoDb
        :param database: nom de la Database
        """
        try:
            logger.debug("Connection MongoDb en cours: {}".format(url_connection))
            self.client = MongoClient(url_connection)  # Docker IP
            self.db = self.client[database]
        except ServerSelectionTimeoutError as err:
            logger.error("Erreur Connection MongoDB {}".format(err))

    def insert(self, voie, collection='voies'):
        """
        Insertion d'une voie dans MongoDB
        :param voie: la voie a enregistrer (transformée en dictionnaire pendant l'insertion)
        :param collection: la collection pour l'enregistrement
        :return ids : le numero d'enregistrement en base
        """
        logger.info("Insertion en dans la collection '{}' de la voie : {}".format(collection, voie.url))
        ids = self.db[collection].insert_one(voie.to_dict())
        return ids

    def exists_voie(self, url, collection='voies'):
        """
        Recherche de l'existance d'une voie par son URL
        :param url: l'url identifiant de la voie
        :param collection: la collection mongoDB dans laquelle faire la recherche
        :return: true si la voie existe, false sinon
        """
        exist = self.db[collection].find_one({'url': url})
        return False if exist is None else True

    def query_all(self, collection, limit=10):
        """
        Affichage de tous les enregistrements dans la Collection MongoDb
        :param collection: la collection à afficher
        :param limit: le nombre d'enregistrements max
        """
        print('Total Record for the collection: ' + str(self.db.voies.count()))
        for record in self.db[collection].find().limit(limit):
            pprint(record)


# --------------------------------------------------------------------------
# Execution du main
# --------------------------------------------------------------------------

if __name__ == '__main__':

    mongo = MongoDbDAO()
    logger.info("Insertion en base d'une voie de test")
    voietest = {'nom': 'nom de la voie de test',
                'diff': '6a',
                'commentaires': 'un commentaire 2',
                'rating': 5}
    res = mongo.db.voies_test.insert_one(voietest)

    logger.info("Affichage voie de test rating=5 :")
    fivestar = mongo.db.voies_test.find_one({'rating': 5})
    print(fivestar)

    logger.info("Affichage de tous les éléments dans voies")
    mongo.query_all(collection='voies')

    logger.info("Test existance d'une voie non existante")
    res2 = mongo.exists_voie('jenexistepas')
    print(res2)
