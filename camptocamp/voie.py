# -*- coding: utf-8 -*-

from camptocamp import logger
from camptocamp.c2cparser import C2CParser

# --------------------------------------------------------------------------
# Classe Définition de la classe Voie permettant le stockage des attributs
# Il s'agit également de la classe pour la restitution (Vue)
# --------------------------------------------------------------------------


class Voie:
    def __init__(self, url, titre, area, approche, longueurs, difficultes, commentaires, cotations, sorties):
        """
        Initialisation de la classe Voie avec tous ses attributs
        :param url: l'url unique de la voie (version minifiée: ie 'baseurl/routes/54788') (String)
        :param titre: le titre de la voie (ie 'Presles - Buis : Point trop n'en faut') (String)
        :param area: localisation de la voie (liste)
        :param approche: le dictionnaire de l'approche de la voie
        :param longueurs: la description des longueurs de la voie (liste)
        :param difficultes: la description des difficultés de la voie (dictionnaire)
        :param commentaires: les commentaires (String)
        :param cotations: les cotations de la voie (dictionnaire)
        :param sorties:  les sorties relatives (liste)
        """
        logger.debug("Init de la classe {}".format(self.__class__))
        self.url = url
        self.titre = titre
        self.area = area
        self.approche = approche
        self.longueurs = longueurs
        self.difficultes = difficultes
        self.commentaires = commentaires
        self.cotations = cotations
        self.sorties = sorties

    # --------------------------------------------------------------------------
    # Déclaration des propriétés de la classe
    # peuvent être appelée dans le code avec self.<nom_de_la_methode>
    # --------------------------------------------------------------------------
    @property
    def get_nblongueurs(self):
        return len(self.longueurs) if self.longueurs is not None else 0

    @property
    def get_nbsorties(self):
        return len(self.sorties) if self.sorties is not None else 0

    # --------------------------------------------------------------------------
    # Constructeur alternatif de classe
    # Pour construire une voie à partir d'un parseur camp2camp
    # --------------------------------------------------------------------------
    @classmethod
    def from_c2cparser(cls, c2cparser):
        """
        Construction alternative de l'objet Voie à partir d'un parser camptocamp
        :param c2cparser: parser permettant de construire l'objet
        :return: objet Voie
        """
        url = C2CParser.get_urlvoie(c2cparser.urlvoie)
        titre = c2cparser.get_titre()
        area = c2cparser.get_area()
        approche = c2cparser.get_approche()
        longueurs = c2cparser.get_details_longueurs()
        difficultes = c2cparser.get_alt_difficultes()
        commentaires = c2cparser.get_commentaires()
        cotations = c2cparser.get_cotations()
        sorties = c2cparser.get_outings()
        return cls(url, titre, area, approche, longueurs, difficultes, commentaires, cotations, sorties)

    # Redéfinition pour l'affichage de la voie
    def __str__(self):
        return "\n" \
               "----------------------------------------------------------------------- \n" \
               " Voie : {} \n" \
               " Localisation : {} \n" \
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
               "".format(self.titre, self.area, self.url, self.cotations, self.difficultes,
                         self.approche.get('approche'), self.approche.get('itineraire'),
                         self.get_nbsorties, self.get_nblongueurs,
                         '\n'.join(self.longueurs), self.approche.get('descente'),
                         self.commentaires, '\n\n'.join(self.sorties))

    def to_dict(self):
        """
        Conversion de l'objet Voie en dictionnaire
        :return: dictionnaire
        """
        return {'titre': '{}'.format(self.titre),
                'url': '{}'.format(self.url),
                'localisation': '{}'.format(self.area),
                'cotations': self.cotations,
                'longueurs': self.longueurs,
                'difficultes': self.difficultes,
                'approche': self.approche,
                'commentaires': '{}'.format(self.commentaires),
                # conversion liste de sorties en dict avec clé en str
                'sorties': {'{}'.format(i): self.sorties[i] for i in range(0, len(self.sorties))}
                }
