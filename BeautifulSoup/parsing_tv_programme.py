# -*- coding: utf-8 -*-

"""
Parsing TV programme
"""

import requests
import datetime
from bs4 import BeautifulSoup

proxies = {"http": None, "https": None}


def programme_tv(url):

    output = (url + "\n\n")
    source = requests.get(url, proxies=proxies).text
    soup = BeautifulSoup(source, 'lxml')
    bheader = soup.find_all('div', class_='bheader')

    nbchaines = len(bheader)        # Nombre de chaines
    dict_prgs = dict()              # Dictionnaire classé par chaine contenant une liste de contenu

    # chaines choisies et ordre d'affichage
    ordre_chaine = ['TF1', 'France 2', 'France 3', 'Canal+', 'France 4', 'France 5', 'M6',
                    'Arte', 'C8', 'W9', 'TMC', 'RMC Découverte', 'NRJ 12', 'Numéro 23', 'Chérie 25',
                    'CNEWS', 'La Chaîne parlementaire', 'BFM TV', 'CSTAR', 'France Ô']

    # boucle sur toutes les chaines
    for i in range(0, nbchaines):

        # chaine = (bheader[i].span['title'])[10:]
        # chaine = (bheader[i].a['title'])[10:]
        chaine = (bheader[i].img['alt'])[10:]           # Slicing pour supprimer "Programme " en debut de chaque chaine

        # Permet de trouver les classes commençant par une chaine spécifique
        scores = bheader[i].find_all("span", class_=lambda value: value and value.startswith("score"))
        types = bheader[i].find_all("span", class_=lambda value: value and value.startswith("type"))

        score = scores[0]['title']
        type_prg = types[0].text

        heures = bheader[i].find_all('span', class_='hour')
        heure_debut = heures[0].text

        titres = soup.find_all('div', class_='figure')
        titre = titres[i].img['alt']

        resumes = soup.find_all('p', class_='resume')
        resume = (str(resumes[i].text).strip())

        # constitution du dictionnaire classé par 'chaine' contenant la liste du contenu (emission)
        emission = [chaine, titre, heure_debut, type_prg, score, resume]
        dict_prgs[chaine] = emission

    # affichage dans l'ordre des chaines choisis
    for ordre in ordre_chaine:
        try:
            # expansions de la liste dans les variables
            chaine, titre, heure_debut, type_prg, score, resume = dict_prgs[ordre]

            output += chaine.lower() + " : " + titre.upper() + " (" + heure_debut + ")" + "  " + type_prg + "\n"
            if score:
                output += "Avis : " + score.upper() + ". Resumé: " + resume + "\n"
            else:
                output += "Resumé: " + resume + "\n"
            output += "\n"
        except KeyError:
            pass

    return output


def cesoirtv_com():
    print("\nProgramme ce SOIR TV")
    source = requests.get("http://www.cesoirtv.com/", proxies=proxies).text
    soup = BeautifulSoup(source, 'lxml')
    progs = soup.find_all('div', class_="soiree-container lazyload")

    for prog in progs:
        chaine = str(prog.find('div', class_="broadcast-channel").img['alt'])
        heure = prog.find('span', class_="HJB").text
        emission = prog.find('span', class_="fw-700").text
        print(chaine.upper() + "   : " + emission + " - " + heure)

    """
    Notez : attention il existe une difference entre la construction des pages html de
    http://www.programme.tv/ ET http://www.programme.tv/tnt
    """


out = "Programme TV - Début de soirée\n".upper()
out += programme_tv("http://www.programme.tv/")


out += "\nProgramme TV - Fin de soirée\n".upper()
jour_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
now = datetime.datetime.today()
jour = jour_semaine[now.weekday()]
out += programme_tv("http://www.programme.tv/tnt/soiree2/" + jour + ".php")

print(out)
# cesoirtv_com()
