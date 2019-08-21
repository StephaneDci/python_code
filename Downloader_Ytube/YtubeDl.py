# -*- coding: utf-8 -*-

"""
Classe pour le Téléchargement de Playlist ou de videos Youtube (Audio ou Video)
Tests OK Novembre 2018
"""

import re
import os
import requests
from Downloader_Ytube import BaseDl
from Downloader_Ytube import UtilsDl
from pytube import YouTube
import sys

"""
https://python-pytube.readthedocs.io/en/latest/

To quick start download
yt = YouTube(link)
yt.streams.all() or yt.streams.filter(only_audio=True).order_by("bitrate").all()
yt.streams.get_by_itag(<int>).download()

NB To get Best quality (Be careful for video it will exclude audio)
   yt.streams.filter(only_video=True).order_by("bitrate").last()
or yt.streams.filter(only_audio=True).order_by("bitrate").last()
"""


class YTubeDl(BaseDl.BaseDl):

    # Errors code
    CODE_SKIPPING = 'SKIPPING'
    CODE_ERROR = 'ERROR'

    # TODO add a param to choose between video or audio
    def __init__(self, urltoparse, target_directory="", retry_onerrors=True,
                 createdir=True, overwrite=False, proxies={"http": None, "https": None}):
        """
        Youtube Videos/Audio Downloader
        :param urltoparse: url of playlist to download from
        :param target_directory: where to save the files on the local host
        :param retry_onerrors:
        :param createdir: Autorisation to create directory to save files. default True.
        :param overwrite: If existing files must be overwritten (if value True) or skipped (value False). Default False
        :param proxies: Proxies Parameter
        """
        # parent constructor
        super().__init__(urltoparse, target_directory, retry_onerrors, createdir, overwrite, proxies)
        # needed attributes
        self.downloadlist = dict()      # will contain {link:filename}

    @staticmethod
    def get_vids_name(link):
        """
        Get the youtube video name
        :param link: <str> link of the video
        :return: <str> title of the videos
        """
        try:
            yt = YouTube(link)
            # CHECK audio bcps plus lent que videos
            # stream = yt.streams.filter(only_audio=True).first()
            stream = yt.streams.first()
            title = stream.default_filename
            # print(f"\nTitle found : {title}")
            return title
        except Exception as ex:
            # Regex error correction see : https://github.com/nficano/pytube/pull/313
            # regex pattern (yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*c\s*&&\s*d\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\() had zero matches
            print(f"Exception occured : {ex}")
            return 'Title not found error'

    # TODO add a param to choose quality
    def download_unit(self, link):
        """
        Download a single resource (videos / or audio) from youtube
        :param link: <str> link of the ressource to download from youtube
        :return : download the file on localhost at self.directory/title
        """
        try:
            yt = YouTube(link)

            # Display a download progress bar
            # https://github.com/nficano/pytube/issues/295
            def show_progress_bar(stream, _chunk, _file_handle, bytes_remaining):
                current = ((stream.filesize - bytes_remaining) / stream.filesize)
                percent = '{0:.1f}'.format(current * 100)
                progress = int(50 * current)
                status = '█' * progress + '-' * (50 - progress)
                sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
                sys.stdout.flush()
            yt.register_on_progress_callback(show_progress_bar)

            # accessing audio streams of YouTube obj.(first one, more available)
            # downloading a video would be: stream = yt.streams.first()
            # TODO check slow download for audio: https://github.com/nficano/pytube/issues/247
            # stream = yt.streams.filter(only_audio=True).first()
            stream = yt.streams.first()
            infos = dict()
            infos['title'] = stream.default_filename
            infos['mime_type'] = stream.mime_type
            infos['audio_codec'] = stream.audio_codec
            infos['abr'] = stream.abr
            infos['size'] = str(stream.filesize // 1024 // 1024) + "Mo"
            print(f"Link: {link}")
            print(infos)

            # TODO : check: skip_file_exists in download method
            # https://github.com/nficano/pytube/pull/271/commits/8d3a6031091f20caea13eb55836124bf736a0c55
            # NB stem only so os.path.splitext is used
            stream.download(self.target_directory, os.path.splitext(stream.default_filename)[0])
            print(f"=> Download complete !")
            self.nbdownloaded_files += 1
            infos['Statut'] = "Download OK"
            self.downloadlist[link] = infos.copy()

        except Exception as inst:
            self.handle_errors(link, self.CODE_ERROR, "[ERROR] - Encountered unknown error: {}".format(inst))

    def download_list(self, limits=None, overwrite=False):
        """
        Process for downloading and construct a list of ressources from youtube
        It will then call corresponding download methods from calling class
        :param limits: Defaut None. Otherwise tuple containing start & end index
        :param overwrite: Default False. Otherwise will erase files if already downloaded
        """
        self.create_download_list()
        download_list = UtilsDl.UtilsDl.get_sublist(self, limits)
        length_list = len(download_list)

        print(f"[Processing] - Found Files . Downloading {length_list} Files...")
        for cpt, link in enumerate(download_list):
            link = link.strip()

            # Retrieve filename from stream
            filename = self.get_vids_name(link)

            # Add the name to the dict
            self.downloadlist[link] = filename

            # Create directory if needed
            UtilsDl.UtilsDl.create_dir(self)

            # The full path to save the file
            filepath = os.path.join(self.target_directory, filename)

            # Check file does not exist before download or if overwrite parameter is True
            if not UtilsDl.UtilsDl.check_file_exists(filepath) or overwrite:
                print("\n" + str(cpt + 1) + f"/{length_list} - [Downloading] - " + filepath)
                try:
                    self.download_unit(link)

                except Exception as inst:
                    self.handle_errors(link, self.CODE_ERROR, "[ERROR] - Encountered unknown error: {}".format(inst))
            else:
                self.handle_errors(link, self.CODE_SKIPPING, "File Already Exists: {}".format(filename))

    def handle_errors(self, link, code, message):
        """
        Handling errors,exception and skipped files in downloading
        :param link: <str> link of the ressources
        :param code: <str> code cf class attribute
        :param message: <str> message of the errors / exception
        :return: update the dict self.errors providing {code: 'xxx', message: 'xxx'}
        """
        print(message)
        if str(code) == self.CODE_SKIPPING:
            self.nbskipped_files += 1
        elif str(code) == self.CODE_ERROR:
            self.nberrors_files += 1
        # add in dict of errors
        addict = dict()
        addict['code'] = code
        addict['message'] = message
        self.errors[link] = addict.copy()

    def create_download_list(self):
        """
        Generate list of youtube links to download by parsing link in the page
        Page in reference should be a playlist but can be any youtube page
        :return: <dict> self.downloadlist {fulllink : vidsname}
        vidsname initialized with 'nonameyet' performance issue and will be update when downloading
        """
        print(f"[Scanning] - Searching youtube links in {self.urltoparse} ... \n")
        page = requests.get(self.urltoparse).text
        dictvids = dict()
        youtubevids = re.findall(r'watch\?v=([\w\.-]+)', page)
        for link in youtubevids:
            full_link = "https://www.youtube.com/watch?v=" + link
            if full_link not in dictvids:
                # videoname = self.get_vids_name(full_link)
                dictvids[full_link] = 'nonameyet'
        self.downloadlist = dictvids
        return dictvids

    def summary(self, verbose=False):
        """
        Get information on files to download
        :param verbose:
        :return:
        """
        desc = super().summary()
        desc += f"\n[YOUTUBE Information]" \
                f"\nFiles downloaded : {self.nbdownloaded_files}"
        if verbose:
            desc += f"\t{len(self.downloadlist)} Tube(s): \n {self.downloadlist}"

        print(desc)

        # ecriture dans un fichier
        with open(self.target_directory+"\Readme.txt", "a") as f:
            f.write(desc+"\n")

    def get_list(self):
        print(self.downloadlist)
