# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, PickleType, DateTime
from sqlalchemy.sql import func
from camptocamp import Base, Session
from camptocamp import logger

# --------------------------------------------------------------------------
# Classe Voie pour la persistence des Données en Database
# Utilisée ici pour montrer les possibilités d'enregistrement en SGBD
# --------------------------------------------------------------------------


class VoieDb(Base):

    # Classe pour la persistence des voies via SQL Alchemy
    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    __tablename__ = 'voies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    url = Column(String(128), index=True, unique=True)
    titre = Column(String(100))
    approche = Column(String)
    itineraire = Column(String)
    descente = Column(String)
    longueurs = Column(PickleType())
    commentaires = Column(String)
    cotationG = Column(String)
    cotations = Column(PickleType())
    difficultes = Column(PickleType())
    sorties = Column(PickleType())

    # Constructeur avec tous les paramètres unitaires
    def __init__(self, titre, url, approche, itineraire, descente, longueurs,
                 commentaires, cotationg, cotations, difficultes, sorties):
        self.titre = titre
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

    # Constructeur alternatif à partir d'une voie
    @classmethod
    def from_voie(cls, voie):
        titre = voie.titre
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
        return cls(titre, url, approche, itineraire, descente, longueurs,
                   commentaires, cotationg, cotations, difficultes, sorties)

    # Vérification de l'existence d'une voie
    # Retourne id si voie existe, False sinon
    @staticmethod
    def exists(urldevoie):
        session = Session()
        r = session.query(VoieDb.id).filter_by(url=urldevoie).first()
        return r.id if r is not None else False

    # Insertion ou update (delete puis insert)
    def insert(self):
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

    @staticmethod
    def query_corationG(value):
        session = Session()
        print(session.query(VoieDb).filter(VoieDb.cotationG.contains(value)).all())

    # Affichage des voies Stockées
    def __repr__(self):
        return "\n(id:{}) - {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n {} \n".format(
            self.id, self.titre, self.url, self.approche, self.itineraire, self.descente,
            self.longueurs, self.commentaires, self.cotationG, self.difficultes)
