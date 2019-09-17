# -*- coding: utf-8 -*-

from camptocamp.DAO.db_model import VoieDb
from camptocamp import Session

session = Session()

# Comptage des voies
q = session.query(VoieDb)
print("Il y a {} voies dans sqlite".format(q.count()))

# extraction de toute les voies
voiesdb = session.query(VoieDb).all()

# 4 - Affichage
for voie in voiesdb:
    print(voie)
print('')

# Autre exemple avec filtre
print(session.query(VoieDb).filter(VoieDb.cotationG.contains('TD')).all())

# Exemple test existance sur le nom de voie
urlvoie = 'https://www.camptocamp.org/routes/54788/fr/presles-buis-point-trop-n-en-fau'
q = session.query(VoieDb).filter_by(url=urlvoie)
q.count()
is_existant = q.first()
if is_existant is not None:
    print("Existe deja : {}".format())


session.close()
