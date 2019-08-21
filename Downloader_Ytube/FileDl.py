# -*- coding: utf-8 -*-

from Downloader_Ytube import BaseDl
from Downloader_Ytube import UtilsDl

import requests
import math
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebsiteDl(BaseDl.BaseDl):
    """
    Classe to download ressources from web site on local disk
    Use beautifulSoup to scrap data.
    """

    # Constructor
    def __init__(self, urltoparse, fileextension, target_directory="", retry_onerrors=True,
                 createdir=True, overwrite=False, proxies={"http": None, "https": None}):
        """
        :param fileextension: str: file extension to filter ressources. Exemple '.mp3'
        """
        # parent constructor
        super().__init__(urltoparse, target_directory, retry_onerrors, createdir, overwrite, proxies)
        # initialised attributes
        self.fileextension = fileextension
        # needed attributes
        self.downloadlist = dict()
        self.totalsize = 0
        self.totalsize_downloaded = 0
        self.initdone = False
        # Initialisation finale
        self.init()

    # Initialisation of the list of files to retrieve
    def get_list(self):
        print(f" [Scanning] - Searching {self.fileextension} in {self.urltoparse} ... \n")
        # Parsing to find a href
        source = requests.get(self.urltoparse, proxies=self.proxies).text
        soup = BeautifulSoup(source, 'lxml')
        all_links = soup.find_all('a', href=True)

        # Creating list when link contains extension
        self.downloadlist = dict()
        list_files = dict()
        for link in all_links:
            # TODO: add regex to add a filter on filename
            if self.fileextension in link['href']:
                list_files[link['href']] = "SIZE_NOT_DEFINED"
        self.downloadlist = list_files

    # Initialise directory name
    def init_dir(self):
        # if directory not defined by user
        if not self.target_directory:
            # Define directory to create based on url
            # ie  for 'http://www.audiolitterature.com/michel-onfray-contre-histoire-de-la-philosophie-volume-1/'
            # dir = michel-onfray-contre-histoire-de-la-philosophie-volume-1
            parsing = urlparse(self.urltoparse)
            self.target_directory = parsing.path[1:-1]

    # Get the header information of the files to download. Total and by files
    def get_headers(self):
        totalsize = 0
        headers = dict()
        for link in self.downloadlist:
            request = requests.head(link.strip(), proxies=self.proxies)
            size = int(request.headers['Content-Length'])
            totalsize += int(size)
            headers['Content-Length'] = size
            headers['Content-Type'] = str(request.headers['Content-Type'])
            self.downloadlist[link] = headers.copy()
        # update total size
        self.totalsize = totalsize//1024

    # Gestion des erreurs et du retry
    def retry_errors(self):
        if self.retry_onerrors:
            print("\n[ RETRY ] Handling errors and retry download...\n")
            for link, path in self.errors.items():
                self.download_unit(link, path)

    # Initialisation of directory and list of ressources
    def init(self):
        if not self.initdone:
            self.init_dir()
            self.get_list()
            self.initdone = True

    def download_unit(self, link, filepath):
        """
        Download and save a ressource to disk with progress bar
        :param link: link of the ressource to download
        :param filepath: path where to save the ressource on disk
        """
        # TODO: add a 200 HTTP verification on ressource access
        r = requests.get(link, stream=True, proxies=self.proxies)
        # parse the filepath to get the filename
        filename = link.rsplit('/', 1)[-1]
        # Total size in bytes.
        file_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        wrote = 0
        # Display
        print(f"  Link: {link}"
              f"\n  Size: {file_size} octets"
              f"\n  Directory: {self.target_directory}"
              f"\n  Filename: {filename}")
        # Write to file
        with open(filepath, 'wb') as f:
            for data in tqdm(r.iter_content(block_size), total=math.ceil(file_size // block_size),
                             unit='KB',
                             unit_scale=True):
                wrote = wrote + len(data)
                f.write(data)
        # Errors
        if file_size != 0 and wrote != file_size:
            print("[ERROR] - something went wrong")
            self.errors[link] = filepath
            # TODO add an option to validate if user want to remove file
            os.remove(filepath)
        # Summary
        print(f"\twritten: {wrote}")
        self.totalsize_downloaded += wrote//1024

    def download(self, limits=None, overwrite=False):
        """
        Process for downloading ressources list from website
        It will then call corresponding download methods from calling class
        :param limits: Defaut None. Otherwise tuple containing start & end index
        :param overwrite: Default False. Otherwise will erase files if already downloaded
        :return:
        """
        download_list = UtilsDl.UtilsDl.get_sublist(self, limits)
        length_list = len(download_list)

        print(f"\nDownloading {length_list} Files...\n")
        for cpt, link in enumerate(download_list):
            link = link.strip()

            # parse the url to get the filename
            name = link.rsplit('/', 1)[-1]

            # Create directory if needed
            UtilsDl.UtilsDl.create_dir(self)

            # The full path to save the file
            filepath = os.path.join(self.target_directory, name)

            # Check file does not exist before download or if overwrite parameter is True
            if not UtilsDl.UtilsDl.check_file_exists(filepath) or overwrite:
                print("\n" + str(cpt + 1) + f"/{length_list} - [Downloading] - " + filepath)
                try:
                    self.download_unit(link, filepath)

                except Exception as inst:
                    print(inst)
                    print('  [ERROR] - Encountered unknown error. Continuing.')
        # Errors handling
        self.retry_errors()

    # Get information on files to download
    def summary(self, verbose=False):
        """
        Get information on what ressources will be downloaded
        """
        desc = super().summary(verbose)
        desc += f"\n[FILE Information]" \
                f"\n\tTotal Size {str(self.totalsize)}"
        if verbose:
            desc += f"\t{len(self.downloadlist)} file(s): " \
                    f"\n\t{self.downloadlist.items()}"
        print(desc)
