# -*- coding: utf-8 -*-

import os
from Downloader_Ytube import FileDl
from Downloader_Ytube import YtubeDl


class UtilsDl:
    """
    Class of Utililities containing static methods
    """
    # Handle the creation of directory on local host
    @staticmethod
    def create_dir(download_instance):
        """
        Create a directory on localhost
        :param download_instance: instance of calling class
        """
        # Create the directory if needed
        if not os.path.exists(download_instance.target_directory):
            if download_instance.createdir:
                print(f"\nCreating directory {download_instance.target_directory} \n")
                os.makedirs(download_instance.target_directory)

    # get a sublist from a dictionnary or a list
    @staticmethod
    def get_sublist(download_instance, limits):
        """
        Methods to return a sublist of element to download
        :param download_instance: instance of calling class
        :param limits: <tuple> : containing start and end index
        :return: sublist of link to download
        """
        sublist = list()

        # If limits is defined
        if limits is not None:
            start, end = limits
        else:
            start, end = 0, len(download_instance.downloadlist)

        # If dictionnary we do a conversion to list
        # TODO use isinstance method
        if 'dict' in str(type(download_instance.downloadlist)):
            for key, value in download_instance.downloadlist.items():
                sublist.append(key)
            return sublist[start:end]
        elif 'list' in str(type(download_instance.downloadlist)):
            return download_instance.downloadlist[start:end]

    @staticmethod
    def check_file_exists(filepath):
        """
        Check if a given filepath is a file
        :param filepath: <str> path
        :return: <bool> true if file exists
        """
        # The path to save the file
        if not os.path.isfile(filepath):
            return False
        return True

    @staticmethod
    def build(urltoparse, target_directory="", fileextension=None,
              retry_onerrors=True, createdir=True, overwrite=False,
              proxies={"http": None, "https": None}):
        """
        Static Builder to instanciate a Downloader Class
        :param urltoparse: <str> url to parse
        :param target_directory: <str> directory on localhost to save ressources
        :param fileextension: <str> needed only for WebsiteDl class
        :param retry_onerrors: <bool> to retry to download if errors
        :param createdir: <bool> authorize or not directory creation
        :param overwrite: <bool> download & overwrite if file already exists
        :param proxies: <dict> définition des proxies
        :return: instance of implemented Class
        """

        # TODO remplacement du builder par un modèle plus pythonique
        # Construct the classes
        if 'youtube' in urltoparse:
            return YtubeDl.YTubeDl(urltoparse, target_directory, retry_onerrors,
                                   createdir, overwrite, proxies)
        else:
            return FileDl.WebsiteDl(urltoparse, fileextension, target_directory,
                                    retry_onerrors, createdir, overwrite, proxies)
