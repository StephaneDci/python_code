# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------------------
# Classe de Download de Ressources sur Youtube
# Auteur : SDI
# Date   : 15/02/2020
# Objectif : educationnal purpose only. Merci de respecter les copyrights.
# Python >= 3.8 + modules dans les requirements
# ------------------------------------------------------------------------------------------------------

import re
import requests
import html
from downloader import logger
import urllib.parse as urlparse
from urllib.parse import parse_qs
from tqdm import tqdm
from typing import List
from pytube import YouTube
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Data Classe RessourceFile : Permet de définir une ressource Youtube
# --------------------------------------------------------------------------
@dataclass
class RessourceYT:
    link: str
    yt: YouTube = None
    filepath: str = "NA"
    downloaded: bool = field(default=False)

    @property
    def length(self):
        return self.yt.length if self.yt else None

    @property
    def titre(self):
        return self.yt.title if self.yt else None

    def __eq__(self, other):
        if type(other) is type(self):
            return self.link == other.link
        return False

    def __hash__(self):
        return hash(self.link)

    def __repr__(self):
        return "\n\nRessource: " \
               f"link: {self.link}\n" \
               f"titre: {self.titre}, " \
               f"path: {self.filepath}, " \
               f"length: {self.length}, " \
               f"downloaded: {self.downloaded}"


class Youtube_Dl:

    BASEURL = "https://www.youtube.com/watch?v="

    def __init__(self):
        self.lst_ressources = list()
        self.prefered_resolutions = ["720p", "480p", "360p"]
        self.parent_dir = "YT"

    def get_youtube_vids_on_url(self, url: str, playlist: str, maxvids: int) -> List[RessourceYT]:
        """
        Generate list of youtube links to download by parsing link in the page
        Page in reference should be a playlist but can be any youtube page
        """
        print(f"[Scanning] - Searching youtube links in {url} ... \n")
        page = html.unescape((requests.get(url).text))
        vids = set()
        # Récupération de toutes les vidéos de la playlist
        if playlist != "":
            logger.debug("Playlist Detected!")
            regex = r'watch\?v=([\w\.-]+)&list={}'.format(playlist)
            logger.debug(f"Regex is : {regex}")
            youtubevids = re.findall(regex, page)
            for link in youtubevids:
                vids.add(RessourceYT(Youtube_Dl.BASEURL+link))
        # Pas de playlist : seulement la video
        else:
            vids.add(RessourceYT(Youtube_Dl.BASEURL + url))
        return list(vids)#[:maxvids]

    def set_ytvids_info(self, res: RessourceYT):
        try:
            res.yt = YouTube(res.link)
        except KeyError:
            logger.warning(f"Error when retrieving vids info: {res.link}")

    def download_ressource(self, res: RessourceYT):
        for r in self.prefered_resolutions:
            if st := res.yt.streams.filter(progressive=True, resolution=r):
                logger.debug(f"Trying resolution {r} for {res.titre}")
                res.filepath = st.first().download(output_path=self.parent_dir)
                break

# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------
if __name__ == '__main__':

    yl = Youtube_Dl()
    yt_playlist = "https://www.youtube.com/watch?v=HGp5UnNiLOA&list=PL4OLSC172x8p8Dy-A88_k_zhKRvpPwRgq"

    parsed = urlparse.urlparse(yt_playlist)
    playlist = parse_qs(parsed.query).get('list')[0]

    yt_ressources = yl.get_youtube_vids_on_url(yt_playlist, playlist, 3)
    print(yt_ressources)

    for r in tqdm(yt_ressources):
        yl.set_ytvids_info(r)
        # yl.download_ressource(r)
    
    print(yt_ressources)
