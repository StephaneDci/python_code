# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, PickleType, DateTime
from sqlalchemy.sql import func
from camptocamp import Base, Session
from camptocamp import logger

# --------------------------------------------------------------------------
# Classe VoieDb pour la persistence des Données en Database SQLite (ou autre)
# Utilisée ici pour montrer les possibilités d'enregistrement en SGBD
# --------------------------------------------------------------------------


class VoieDb(Base):
    """
    Classe pour la persistence des voies via SQL Alchemy
    """
    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    __tablename__ = 'voies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    url = Column(String(128), index=True, unique=True)
    titre = Column(String(100))
    area = Column(PickleType())
    approche = Column(String)
    itineraire = Column(String)
    descente = Column(String)
    longueurs = Column(PickleType())
    commentaires = Column(String)
    cotationG = Column(String)
    cotations = Column(PickleType())
    difficultes = Column(PickleType())
    sorties = Column(PickleType())

    def __init__(self, titre, area, url, approche, itineraire, descente, longueurs,
                 commentaires, cotationg, cotations, difficultes, sorties):
        """
        Constructeur de la classe avec les paramètres unitaire
        :param titre:
        :param area:
        :param url:
        :param approche:
        :param itineraire:
        :param descente:
        :param longueurs:
        :param commentaires:
        :param cotationg:
        :param cotations:
        :param difficultes:
        :param sorties:
        """
        self.titre = titre
        self.area = area
        self.url = url
        self.approche = approche
        self.itineraire = itineraire
        self.descente = descente
        self.longueurs = longueurs
        self.commentaires = commentaires
        self.cotationG = cotationg
        self.cotations = cotations
        self.difficultes = difficultes
        self.sorties = sorties

    @classmethod
    def from_voie(cls, voie):
        """
        Constructeur alternatif à partir d'un objet "Voie"
        :param voie: l'objet
        :return: un objet VoieDb
        """
        titre = voie.titre
        area = voie.area
        url = voie.url
        approche = voie.approche.get('approche')
        itineraire = voie.approche.get('itineraire')
        descente = voie.approche.get('descente')
        longueurs = voie.longueurs
        commentaires = voie.commentaires
        cotationg = voie.cotations.get('Cotation globale')
        cotations = voie.cotations
        difficultes = voie.difficultes
        sorties = voie.sorties
        return cls(titre, area, url, approche, itineraire, descente, longueurs,
                   commentaires, cotationg, cotations, difficultes, sorties)

    @staticmethod
    def exists(urldevoie):
        """
        Vérification de l'existence d'une voie
        :param urldevoie: l'url
        :return: Retourne id si voie existe, False sinon
        """
        session = Session()
        r = session.query(VoieDb.id).filter_by(url=urldevoie).first()
        return r.id if r is not None else False

    def insert(self):
        """
        Insertion ou update (delete puis insert) d'une voie
        :return: l'id d'insertion en base
        """
        logger.info("Insertion en Base de la voie : {}".format(self.url))
        session = Session()
        idvoie = VoieDb.exists(self.url)
        if idvoie:
            logger.info("Suppression de l'id : {}".format(idvoie))
            session.query(VoieDb.id).filter_by(id=idvoie).delete()
        # Ajout en base
        session.add(self)
        session.commit()
        # Récupération de l'id de l'insertion
        session.refresh(self)
        logger.info('Insertion en Base Id: {}'.format(self.id))
        return self.id

    @staticmethod
    def query_coration_globale(value):
        session = Session()
        print(session.query(VoieDb).filter(VoieDb.cotationG.contains(value)).all())

    @staticmethod
    def query(value):
        session = Session()
        # print(session.query(VoieDb).filter(VoieDb.cotationG.contains(value)).all())
        # filters = {'nblongueurs': '4'}
        # print(session.query(VoieDb).filter_by(**filters).all())

        userfilter = (VoieDb.nblongueurs > 5)
        r = session.query(VoieDb).filter(*userfilter).all()
        print(r)

        # filters = session.query(VoieDb).filter(
        #    VoieDb.nblongueurs > 10).all()
        # print(filters)

    # Affichage des voies Stockées
    def __repr__(self):
        return "\n(id:{}) - {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n".format(
            self.id, self.titre, self.area, self.url, self.approche, self.itineraire, self.descente,
            self.longueurs, self.commentaires, self.cotationG, self.difficultes)
