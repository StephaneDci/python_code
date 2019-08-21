# -*- coding: utf-8 -*-

import requests
import json
import Slack.Slackapi as Slack

proxies = {"http": None, "https": None}


#############
# Fonctions #
#############


def get_prevision_mf_pluie_heure(codeinsee):
    """
    Fonction pour récupérer le niveau de pluie dans une heure depuis Meteo France
    Attention, différentes chaines étant concatenées de différentes sources (unicode, api, json, python)
    Il faut être sur qu'elles aient toutes le même encoding ce que fait la fonction
    :param codeinsee: le code insee du ou des lieux sont on souhaite la prévision
    :return: chaine formatee de la prévision
    """

    # Attention il faut rajouter un '0' au code insee avant appel api
    url = "http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/{}0".format(codeinsee)
    source = requests.get(url, proxies=proxies).text
    data = json.loads(source)
    strpluie = ""

    if data['hasData']:
        for npluie in data['niveauPluieText']:
            stri = npluie.encode('utf-8').strip()
            strpluie += "\n\t " + str(stri)
    else:
        return str(" : nodata!")

    str_retour = str(data['idLieu'] + "  (Last update: " + data['lastUpdate'] + ")") + strpluie
    return str_retour


def get_commune_and_insee_code_from_cp(codepostal):
    """
    Conversion code postal and code insee + affichage commune
    :param codepostal: le CP en entrée pour conversion
    :return: nombre de résulats, liste des communes et liste des codes insees correspondant
    """
    urlapi = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=correspondance-code-insee-code-postal&q={}&facet=insee_com&facet=nom_dept&facet=nom_region".format(codepostal)
    str_conversion = requests.get(urlapi, proxies=proxies).text
    json_conversion = json.loads(str_conversion)
    nb_res = len(json_conversion['records'])

    list_commune = []
    list_codeinsee = []

    for record in json_conversion['records']:
        list_commune.append(record['fields']['nom_comm'])
        list_codeinsee.append(record['fields']['insee_com'])

    return nb_res, list_commune, list_codeinsee


def get_pluie_from_cp(codepostal):
    """
    Fonction permettant de recupérer la pluie dans l'heure sur un CP
    Renvoie une liste 1D
    """
    nb_res, list_commune, list_codeinsee = get_commune_and_insee_code_from_cp(codepostal)
    liste_reponse = list()
    # Aucun Résultat pour le CP
    if nb_res == 0:
        liste_reponse.append("Aucun enregistrement trouvé pour CP: " + codepostal)
        return liste_reponse
    # Plusieurs résultat par CP
    elif nb_res > 1:
        for cpinsee, commune in zip(list_codeinsee, list_commune):
            previ = get_prevision_mf_pluie_heure(cpinsee)
            liste_reponse.append(str(commune) + " " + previ)
        return liste_reponse
    # 1 seul résultat par CP
    elif nb_res == 1:
        previ = str(get_prevision_mf_pluie_heure(list_codeinsee[0]))
        liste_reponse.append(str(list_commune[0]) + " " + previ)
        return liste_reponse


def get_meteo_from_liste_cp(liste_codepostaux):
    """
    Renvoie une liste en 2D des bulletins meteos(ajoute une liste dans une liste)
    :param liste_codepostaux:
    :return:
    """
    liste2d_meteo = list()
    for cpost in liste_codepostaux:
        liste2d_meteo.append(get_pluie_from_cp(cpost))
    return liste2d_meteo


def formatte_liste(liste_non_formatee):
    """
    Formatte les erreurs dans la chaines pour traitment et pour faciliter le traitement des précipitations
    Remplacement de Pas de précipitation par Pas de pluie pour simplifier les traitements de liste de précipitation
    :param liste_non_formatee: liste en entrée
    :return: liste formatee: corrections typographiques
    """
    liste_formatee = list()
    for i in liste_non_formatee:
        m = str(i.strip().replace("De", "De ").replace("Pas de précipitations", "Pas de pluie"))
        liste_formatee.append(m)
    return liste_formatee


def get_simple_list(liste_2d):
    """
    Conversion d'une liste 2D en liste simple
    :param liste_2d: liste 2D (si plusieurs enregistrements pour un CP
    :return: liste simple
    """
    liste_simple = list()
    for i in range(len(liste_2d)):
        for j in range(len(liste_2d[i])):
                liste_simple.append(liste_2d[i][j])
    return formatte_liste(liste_simple)


def get_liste_precipitation(liste_meteo_formattee):
    """
    Création d'une liste des précipitations , cad des lors qu'une pluie dans l'heure est prévue
    Détection du terme Précipitation
    :param liste_meteo_formattee:
    :return:
    """
    liste_precipitation = list()
    for i in liste_meteo_formattee:
        if i.find("Précipitations") > 0:
            liste_precipitation.append(i)
        else:
            continue
    return liste_precipitation

#######################
# Programme principal #
#######################

# Surveillance d'une liste de CP
liste_cp = ['92340', '92160']

liste_2D_bulletin_meteo = get_meteo_from_liste_cp(liste_cp)
liste_simple_meteo = get_simple_list(liste_2D_bulletin_meteo)
liste_des_precipitations = get_liste_precipitation(liste_simple_meteo)

# Affichage
print(str.center("Bulletin Méteo", 60, "-"))
print('\n'.join(liste_simple_meteo))

print("\n")
print(str.center("Bulletin Précipitations", 60, "-"))
print('\n'.join(liste_des_precipitations))

