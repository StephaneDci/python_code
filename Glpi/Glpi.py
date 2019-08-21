# -*- coding: utf-8 -*-

# =================================================================================================
# Code pour Interface avec API GLPI
# -----------------------------------
# 
# Auteur: Stéphane DI CIOCCIO
#
# Fonctionne avec GLPI >= 9.2.3 ainsi que Python >= 3.4
# Testé également avec GLPI 9.3.3
#
# Permet l'utilisation de l'API à partir du Auth Token et App token (si défini)
#
# -------------------------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------------------------
# GLPI
# apptoken  : a definir dans API > Ajouter un client API > Jeton d'application (app_token)
# authToken : front/user.form.php > Clés accés distant > Jeton API
# front/config.form.php
#   Activer la connexion avec un jeton externe
#   Activer l'API
#
# SERVEUR WEB
# For rewrite Rules Config see: https://github.com/glpi-project/glpi/issues/4386
#
# Dépendances Externes : pip install requests
#
#
# Fonctions : Creation d'un ticket / Ajout d'un suivi / Suppression de ticket
#
# Utilisation :
#   Creation d'un ticket : <script.py> create "titre" "description" entite
#                exemple : <script.py> create "titre du ticket" "description" 213
#
#   Ajout d'un suivi     : script.py addfollowup id_ticket "description"
#                exemple : script.py addfollowup 2018001417 "description du suivi"
#
# =================================================================================================

import json
import requests
import logging
import sys
import argparse
import urllib3


# Configuration du niveau de Logging du script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s :%(levelname)s : %(funcName)s - %(message)s')

# Desactivation des erreurs de certificats HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GLPIUtils:
    """
    Classe Utilitaire pour
        * gérer les requêtes vers les endpoints de l'API
        * pour le parsing des Arguments
    """

    # méthode de construction des requetes vers l'API pour factoriser le code
    @staticmethod
    def make_api_call(glpi_inst, method, url, payload=""):

        # pour éviter d'appeler en boucle l'initialisation du Token de session
        if str(url).find("initSession") <= 0:
            if glpi_inst.session_token is None:
                glpi_inst.get_session_token()
        logging.debug("\n\n---------MAKE_API_CALL----------\n")

        # Définition des headers
        headers = {"Content-Type": "application/json"}

        # Si le session Token n'est pas positionné
        if glpi_inst.session_token is None:
            # headers.update({"Authorization": f"user_token {glpi_inst.auth_token}"})   # Need Python >= 3.5
            headers.update({"Authorization": "user_token {}".format(glpi_inst.auth_token)})

        # Si le token de session est défini
        elif not (glpi_inst.session_token is None):
            headers['Session-Token'] = "{}".format(glpi_inst.session_token)

        # Si app_token est defini on l'ajoute dans les headers
        if not (glpi_inst.app_token is None):
            headers['App-Token'] = glpi_inst.app_token

        # Gestion des méthodes d'appels
        if method == 'GET':
            r = requests.request(method, url, headers=headers, proxies=glpi_inst.proxies, verify=False)
        if method == 'POST' or method == 'DELETE' or method == 'PUT':
            r = requests.request(method, url, headers=headers,
                                 data=json.dumps(payload), proxies=glpi_inst.proxies, verify=False)

        logging.debug(r.request.body)
        logging.debug(r.request.headers)
        logging.debug(r.text)

        if r.status_code == 200 or r.status_code == 201:
            logging.debug("HTTP STATUS OK : {}".format(r.status_code))
            return r
        else:
            logging.error("[ FATAL ] HTTP ERROR {} : {}".format(r.status_code, r.text))
            sys.exit(2)

    @staticmethod
    def parse_arguments(instance):
        # Parsing des commandes
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help='commands')

        # ----- Définition des groupes de parsing -----

        # Create Ticket
        create_parser = subparsers.add_parser('create', help='Create a ticket')
        create_parser.set_defaults(func='create')
        create_parser.add_argument('glpi_title', help='Title of the ticket to create')
        create_parser.add_argument('glpi_descr', help='Description ot the Ticket')
        create_parser.add_argument("glpi_entity", type=int, help="GLPI Entity for the Ticket Creation", default=213)

        # Add a followup in ticket
        followup_parser = subparsers.add_parser('followup', help='Add a followup in an existing ticket')
        followup_parser.set_defaults(func='followup')
        followup_parser.add_argument('ticket_id', type=int, help='(int) id of the GLPI ticket')
        followup_parser.add_argument('description', help='Message to be added as followup')

        # Get Infos on a ticket
        infos_parser = subparsers.add_parser('infos', help='Get infos on an existing ticket')
        infos_parser.set_defaults(func='infos')
        infos_parser.add_argument('ticket_id', type=int, help='(int) id of the GLPI ticket')

        # Delete a ticket
        delete_parser = subparsers.add_parser('delete', help='Delete an existing ticket')
        delete_parser.set_defaults(func='delete')
        delete_parser.add_argument('ticket_id', type=int, help='(int) id of the GLPI ticket to Delete')

        arguments = parser.parse_args()

        logging.debug("--------- Arguments de la fonction ---------")
        logging.debug(arguments)

        if arguments.func == "create":
            ticket = GLPITicket(instance, arguments.glpi_title, arguments.glpi_descr)
            ticket.change_active_entitie(arguments.glpi_entity)
            numticket = ticket.post_ticket()

        if arguments.func == "followup":
            ticket = GLPITicket(instance)
            ticket.add_followup(arguments.description, arguments.ticket_id)

        if arguments.func == "infos":
            ticket = GLPITicket(instance)
            ticket.get_ticket_by_id(arguments.ticket_id)

        if arguments.func == "delete":
            ticket = GLPITicket(instance)
            ticket.delete_ticket_by_id(arguments.ticket_id)


class GLPIInstance:
    """ Classe représentant l'instance de connection à GLPI avec les Tokens de sessions """
    def __init__(self, authtoken, urlapi, apptoken=None, proxies={"http": None, "https": None}):
        self.auth_token = authtoken
        self.app_token = apptoken
        self.url = urlapi
        self.session_token = None
        self.proxies = proxies

    def get_session_token(self):
        """ Returns current session Token If not Set try to Set it"""

        if self.session_token is not None:
            return self.session_token
        else:
            self.set_session_token()
            logging.debug("[+] Session Token : {} ".format(self.session_token))
            return self.session_token

    def set_session_token(self):
        """  Mise en place du token de session avec l'authentification de l'utilisateur
        Le token de session est récupéré après un appel à initSession avec les bons paramètres
        :return: le token de session """

        # URL should be like: http://glpi.example.com/apirest.php/
        full_url = self.url + 'initSession/'
        r = GLPIUtils.make_api_call(self, 'GET', full_url)

        try:
            session_token = r.json()['session_token']
            logging.debug("[INIT SESSION OK] - Authentification GLPI OK , Session Token : {}".format(session_token))
            self.session_token = session_token
            return session_token
        except Exception as e:
            logging.error("[FATAL ERROR: INIT SESSION] when try to init session in GLPI server: %s".format(e))
            sys.exit(2)

    def __repr__(self):
        out = str.center("Affichage de l'instance", 50, "-")
        out += "\n" + "Auth Token: " + self.auth_token + "\n"
        out += "URL: " + self.url + "\n"
        out += "Proxies: " + str(self.proxies) + "\n"
        out += "App Token: " + str(self.app_token) + "\n"
        out += "Session Token: " + str(self.session_token)
        return out


class GLPITicket:
    """  Classe représentant un ticket (simplifié) """

    def __init__(self, instance_glpi, titre="", description="", entity=0):

        self.instance = instance_glpi
        self.titre = titre
        self.description = description
        self.entity = entity
        self.id = None

    def post_ticket(self):
        """ Création du ticket dans GLPI
        :return: Numéro de ticket """

        payload = '''{"input": [{"name": "titre", 
                "requesttypes_id": "1",
                "itilcategories_id":2,
                "content": "description",
                "type": "2"}] }'''

        data = json.loads(payload)
        data['input'][0]['name'] = self.titre
        data['input'][0]['content'] = self.description

        full_url = self.instance.url + "Ticket/"

        r = GLPIUtils.make_api_call(self.instance, 'POST', full_url, data)
        data = r.json()
        self.id = data[0]['id']
        self.print_json()
        return self.id

    def get_ticket_by_id(self, idticket):
        """ Affichage d'un ticket par son numéro
        :param idticket: numéro du ticket
        :return: affichage du ticket """
        full_url = self.instance.url + "Ticket/" + str(idticket)
        r = GLPIUtils.make_api_call(self.instance, 'GET', full_url)
        print(r.content)

    def delete_ticket_by_id(self, idticket):
        """ Suppression ticket par id
        :param idticket: numéro du ticket """
        full_url = self.instance.url + "Ticket/" + str(idticket)
        payload = '''{"input": {"id": 10}, "force_purge": true}'''
        data = json.loads(payload)
        data['input']['id'] = idticket
        GLPIUtils.make_api_call(self.instance, 'DELETE', full_url, data)

    def get_active_entitie(self):
        """  Récuperation de l'entité active  """
        full_url = self.instance.url + "getActiveEntities"
        GLPIUtils.make_api_call(self.instance, 'GET', full_url)

    def change_active_entitie(self, entity_id):
        """  Changement de l'entité active  """
        payload = '''{"entities_id": "213", "is_recursive": "true"}'''
        data = json.loads(payload)
        data['entities_id'] = entity_id
        full_url = self.instance.url + "changeActiveEntities"
        GLPIUtils.make_api_call(self.instance, 'POST', full_url, data)
        self.entity = entity_id

    def add_followup(self, message, idticket=None):
        """ Ajout d'un suivi dans un ticket
        :param message: Message du suivi
        :param idticket: facultatif : numero du ticket dans lequel poster le message """

        if not idticket:
            idticket = self.id

        payload = '''{"input": [{"tickets_id": "num", 
                "is_private": "0",
                "requesttypes_id": "6",
                "content": "descriptionsuivi"
                }] } '''

        data = json.loads(payload)
        data['input'][0]['tickets_id'] = idticket
        data['input'][0]['content'] = message

        full_url = self.instance.url + "Ticket/" + str(idticket) + "/TicketFollowup/"
        GLPIUtils.make_api_call(self.instance, 'POST', full_url, data)

    def print_json(self):
        val = {"id": self.id, "titre": self.titre, "description": self.description, "entity": self.entity}
        data = json.dumps(val)
        print(data)

    def __repr__(self):
        """  Réecriture de la fonction d'affichage
        :return: affichage (str)  """
        out = str.center("Affichage du Ticket", 50, "-")
        out += "\n" + "ID: " + str(self.id) + "\n"
        out += "Titre: " + self.titre + "\n"
        out += "Description: " + self.description + "\n"
        out += "Instance: \n" + str(self.instance)
        return out


# Main
if __name__ == '__main__':

    # Proxy configuration
    def_proxies = {"http": "127.0.0.1:3128", "https": "127.0.0.1:3128"}

    # Creation de l'instance GLPI
    glpi = GLPIInstance(urlapi="https://.....//apirest.php/",
                        apptoken="xxxxx",
                        authtoken="",
                        proxies=def_proxies)

    glpi_ppd = GLPIInstance(urlapi="https://...../apirest.php/",
                            apptoken="xxxxx",
                            authtoken="xxxxxx",
                            proxies=def_proxies)

    GLPIUtils.parse_arguments(glpi_ppd)

#########################
# Documentation
#########################

#    Creation d'une instance glpi : glpi = GLPI(....)
#    Affichage d'un ticket : ticket.get_ticket_by_id(2018001501)
#    Suppression d'un ticket : ticket.delete_ticket_by_id(2018001502)
#    Ajout d'un suivi sur un ticket: ticket.add_followup("Ajout d'un suivi test 2 ", numticket)
