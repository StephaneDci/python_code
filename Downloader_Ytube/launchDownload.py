# -*- coding: utf-8 -*-

from Downloader_Ytube import UtilsDl as Utils

"""
Script principale pour le lancement du téléchargement
"""

if __name__ == '__main__':

    urlfile = 'http://www.audiolitterature.com/michel-onfray-nietzsche-en-quatre-questions/'
    urlytbe = 'https://www.youtube.com/watch?v=RM8wFcbNJPc'

    """
    dlf = utils.UtilsDl.build(urltoparse=urlfile,
                              fileextension='.mp3',
                              retry_onerrors=True,
                              proxies={"http": "127.0.0.1:3128", "https": "127.0.0.1:3128"} )
   """
    dly = Utils.UtilsDl.build(urltoparse=urlytbe,
                              target_directory='Chihiro',
                              retry_onerrors=True)

    # download à partir d'une liste
    dly.download_list()
    # download unitaire
    # dly.download_unit(urlytbe)

    # Affichage du résumé
    dly.summary(verbose=True)

    print("Fin du traitement")

