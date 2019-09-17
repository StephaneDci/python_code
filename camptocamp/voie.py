# -*- coding: utf-8 -*-

from camptocamp import logger
from camptocamp.c2cparser import C2CParser
from camptocamp.DAO.pickle_model import Pickle_DAO


# --------------------------------------------------------------------------
# Classe Définition de la classe Voie permettant le stockage des attributs
# Il s'agit également de la classe pour la restitution (Vue)
# --------------------------------------------------------------------------
class Voie:
    def __init__(self, url, titre, approche, longueurs, difficultes, commentaires, cotations, sorties):
        logger.debug("Init de la classe {}".format(self.__class__))

        self.url = url                      # L'url minifiée de la voie : baseurl/routes/54788
        self.titre = titre                  # Titre de la voie : Presles - Buis : Point trop n'en faut
        self.approche = approche            # Approche / Itinéraire / Descente (Dict)
        self.longueurs = longueurs          # Description des longueurs de la voie (List)
        self.difficultes = difficultes      # Hauteurs des difficultés
        self.commentaires = commentaires    # Récupération des commentaires de la voie
        self.cotations = cotations          # Récupération des différentes cotations (dictionnaire)
        self.sorties = sorties              # Contenu des sorties (String)

    # Déclaration des propriétés de la classe
    # peuvent être appelée dans le code avec self.<nom_de_la_methode>
    @property
    def get_nblongueurs(self):
        return len(self.longueurs) if self.longueurs is not None else 0

    @property
    def get_nbsorties(self):
        return len(self.sorties) if self.sorties is not None else 0

    # Constructeur alternatif
    # Pour construire une voie à partir d'un parseur camp2camp
    @classmethod
    def from_c2cparser(cls, c2cparser):
        url = C2CParser.get_urlvoie(c2cparser.urlvoie)
        titre = c2cparser.get_titre()
        approche = c2cparser.get_approche()
        longueurs = c2cparser.get_details_longueurs()
        difficultes = c2cparser.get_alt_difficultes()
        commentaires = c2cparser.get_commentaires()
        cotations = c2cparser.get_cotations()
        sorties = c2cparser.get_outings()
        return cls(url, titre, approche, longueurs, difficultes, commentaires, cotations, sorties)

    # Redéfinition pour l'affichage de la voie
    def __str__(self):
        return "\n" \
               "----------------------------------------------------------------------- \n" \
               " Voie : {} \n" \
               " URL : {} \n" \
               " Cotations : {} \n" \
               " Hauteur des diffs : {} \n" \
               " Approche : {} \n" \
               " Itinéraire : {} \n" \
               " Nombre de sorties : {} \n" \
               " Nombre de longueurs : {} \n" \
               " \n Details longueurs : \n{} \n" \
               " \n Descente : {} \n" \
               " \n Commentaires : {} \n" \
               " \n ** Sorties  ** \n{} \n" \
               "-----------------------------------------------------------------------" \
               "".format(
                self.titre,
                self.url,
                self.cotations,
                self.difficultes,
                self.approche.get('approche'),
                self.approche.get('itineraire'),
                self.get_nbsorties,
                self.get_nblongueurs,
                '\n'.join(self.longueurs),
                self.approche.get('descente'),
                self.commentaires,
                '\n\n'.join(self.sorties))

    def pickle_persistence(self):
        logger.info("Persistance avec Pikcle")
        Pickle_DAO.insert(self)
