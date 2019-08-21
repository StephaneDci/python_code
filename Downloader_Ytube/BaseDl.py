# -*- coding: utf-8 -*-


# Classe principale mere permettant l'heritage aux autres classes
class BaseDl:
    def __init__(self, urltoparse, target_directory="", retry_onerrors=True, createdir=True,
                 overwrite=False, proxies={"http": None, "https": None}):
        """
        :param urltoparse: <str> : the url from we want to download
        :param target_directory: <str> : the path on localhost to save the files
        :param retry_onerrors: <bool> : if we want to retry download for files
        :param createdir: <bool> : if we authorize to create a dir
        :param overwrite: <bool> : il we want to overwrite and download files if already exists
        :param proxies: <dict> : proxy parameters
        """

        self.urltoparse = urltoparse
        self.target_directory = target_directory
        self.retry_onerrors = retry_onerrors
        self.createdir = createdir
        self.overwrite = overwrite
        self.proxies = proxies
        self.nbskipped_files = 0
        self.nberrors_files = 0
        self.nbdownloaded_files = 0
        self.errors = dict()

    def summary(self, verbose=False):
        desc = str(f"\n[Informations]\n"
                   f"Use proxy: {self.proxies}\n"
                   f"Url To parse: {self.urltoparse}\n"
                   f"Request Directory Creation: {self.createdir}\n"
                   f"Directory target: {self.target_directory}\n"
                   f"Overwrite if file exist: {self.overwrite}\n"
                   f"Retry on errors: {self.retry_onerrors}\n"
                   f"Nb Skipped Files: {self.nbskipped_files}\n"
                   f"Nb Errors Files: {self.nberrors_files}\n"
                   f"Nb Downloader Files: {self.nbdownloaded_files}\n"
                   f"Errors/Exception: {self.errors}\n")
        return desc

    def get_list(self):
        raise NotImplementedError()
