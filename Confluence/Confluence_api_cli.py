#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json
import sys
import html
import mimetypes
import logging

###########################################################################################
# !! UNDER CONSTRUCTION !! Test only
# Auteur : Stéphane Di Cioccio 
# Objet  : Client pour les API Confluence
# TODO : a transformer en classe
###########################################################################################

requests.packages.urllib3.disable_warnings()
logging.basicConfig(level=logging.WARNING, format='%(levelname)s : %(funcName)s - %(message)s')

# TODO : a optimiser
user = sys.argv[1]
passwd = sys.argv[2]


def upload_file(id_page, filename):
    """
    Upload a File to a page :
    https://stackoverflow.com/questions/35286227/uploading-attachments-to-confluence-rest-api-with-python-requests-gives-415-and
    :param id_page:
    :param filename:
    :return:
    """

    logging.debug("Uploading file {} to page number {}".format(filename, id_page))

    url = f"https://url_api_confluence/rest/api/content/{id_page}/child/attachment"
    headers = {'X-Atlassian-Token': 'no-check'}

    # determine content-type
    content_type, encoding = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = 'multipart/form-data'

    file = {'file': (filename, open(filename, 'rb'), content_type)}

    r = requests.post(url, files=file, headers=headers, auth=(user, passwd))

    print("HTTP Status Code : " + str(r.status_code))


def update_page(html_msg, id_page, title, version_page_before):
    """
    Update a Confluence PAGE
    :param html_msg:
    :param id_page:
    :param title:
    :param version_page_before:
    :return:
    """
    version_page = version_page_before + 1

    logging.debug("Updating page id {} from vers {} to {} ".format(id_page, version_page_before, version_page))

    postdata = {"type": "page",
                "title": title,
                "version": {"number": version_page},
                "body":
                    {"storage": {"value": html_msg, "representation": "storage"}}}

    # Create a new page
    headers = {'Content-Type': 'application/json', 'X-Atlassian-Token': 'no-check'}
    r = requests.put('https://url_api_confluence/rest/api/content/{}'.format(id_page), headers=headers,
                     auth=(user, passwd), data=json.dumps(postdata), verify=False)

    print("HTTP Status Code : " + str(r.status_code))


def create_page(title, html_msg, idparent):

    logging.debug("Creating page title '{}' on parent ID: {}".format(title, idparent))

    postdata = {"type": "page",
                "title": title,
                "ancestors": [{'id': idparent}],
                "space": {"key": "TAPI"},
                "body":
                    {"storage": {"value": html_msg, "representation": "storage"}}}

    # Create a new page
    headers = {'Content-Type': 'application/json', 'X-Atlassian-Token': 'no-check'}
    r = requests.post('https://url_api_confluence/rest/api/content', headers=headers,
                      auth=(user, passwd), data=json.dumps(postdata), verify=False)

    print("HTTP Status Code : " + str(r.status_code))


def format_text_to_html(text_content):

    logging.debug("Forming text message to Html")

    s = str(html.escape(text_content))
    s = s.replace("\n", "<br/>")

    start_html = """ <html><head></head><body> """
    end_html = """ </body> </html> """
    html_msg = start_html + s + end_html
    return html_msg


def check_page_exist(title):
    """
    Check if a given page with title in the specific space exists
    :param title: title of the page
    :return: if exist : tuple (idpage, version)
             if not exist : return false
    """

    url = "https://url_api_confluence/rest/api/content?title={}" \
          "&spaceKey=TAPI&expand=history,version".format(title)

    r = requests.get(url, auth=(user, passwd), verify=False)

    print("HTTP Status Code : {}".format(r.status_code))
    if r.status_code == 200:
        data = json.loads(r.text)
    else:
        print("FATAL HTTP ERROR")
        print(r.content)
        sys.exit(2)
    try:
        id_homepage = data.get('results')[0].get('id')
        vers = data.get('results')[0].get('version').get('number')
        return id_homepage, vers
    except IndexError:
        return False, False


# lancement requete GET pour récupération Homepage
# Requete de récupération de la page contenant MEP dans l'espace TAPI
# url_HOME = 'https://url_api_confluence/rest/api/space/TAPI'
# Récupération de la page d'accueil # résultat => /rest/api/content/64578696
# homepage = data.get('_expandable').get('homepage')
# Récupération d'une page specifique


# Main
if __name__ == '__main__':
    pageparent = "MEP"
    pagetitle = "RELEASE X.Y.Z"

    idparent_page, version = check_page_exist(pageparent)

    if not idparent_page:
        print("[FATAL] : Page parent '{}' inexistance".format(pageparent))
        sys.exit(2)
    else:
        print("ID de la page parent '{}' => '{}'".format(pageparent, idparent_page))

    idpage, version = check_page_exist(pagetitle)

    if not idpage:
        print("La page n'existe pas => Creation")
        with open("html_page", "r", encoding="utf8") as myfile:
            text = myfile.read()
        msg_html = format_text_to_html(text)
        create_page(pagetitle, msg_html, idparent_page)

    else:
        print("La page existe déjà => Update")
        with open("html_page_update", "r", encoding="utf8") as myfile:
            text_update = myfile.read()
        msg_html_update = format_text_to_html(text_update)
        update_page(msg_html_update, idpage, pagetitle, version)
        upload_file(idpage, "upload_file.txt")
