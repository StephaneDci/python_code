# coding:utf8
import socket
import subprocess as sp, sys
import logging
import os
import threading
import datetime
from pathlib import Path

logging.basicConfig(level=logging.WARNING)


class ThreadedTCPServer(object):
    """
    Classe pour un serveur TCP Multithreadé pour executer des commandes systèmes
    Inspiré de :
    https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
    """

    # Constructeur
    def __init__(self, pport, phost):
        self.port = pport
        self.host = phost
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # <= ouverture socket TCP
        self.sock.bind((phost, pport))
        self.thread_local = threading.local()                           # <= stockage pour les threads (cwd) et les connections

    def listen(self):
        """
        Lancement de l'écoute du serveur sur notre socket pour accepter les connections clients
        """
        self.sock.listen(5)
        while True:
            print("[-] Listening on %s:%d" % (self.host, self.port))
            conn, addr = self.sock.accept()
            print("[+] Connection established with : %s %s" % (str(addr[0]), conn.getpeername()))

            # Lancement du Thread : 1 par shell
            # Nb nous sommes obligés en args de passer un tuple
            # ou si un seul argument ie args=(conn,) NB la ',' est importante!
            t = threading.Thread(target=self.threaded_listen_client, args=(conn,))
            t.start()

    # Fonction pour envoyer un message au client
    def send_message(self, message):
        # On code la longueur de la réponse complétée par des '0' pour un total de 16 caractères
        length = str(len(message)).zfill(16)
        # On encode la chaine a envoyer en utf8 formay byte : <longueur_16octet><message>
        bytetosend = (length + message).encode("utf8")
        self.thread_local.conn.send(bytetosend)

    # Fonction de changement de repertoire pour le thread
    def change_directory(self, command):

        # decoupage des parametres de la commande
        splitcommand = command.split()

        if len(splitcommand) == 2:
            # utilisation de os.system qui fonctionne pour les threads (attention cd .. ne fonctionne pas)
            # IL FAUT UTILISER DES CHEMINS ABSOLUS
            # car os.chdir fonctionne au niveau du processus et change le chemin de tous les threads
            # On utilise la librairie pathlib pour la gestion des répertoires
            p = Path(self.thread_local.cwd) / splitcommand[1]
            if p.is_dir():
                newrep = str(p.resolve())
                retourcli = "Repertoire ok."
            else:
                newrep = self.thread_local.cwd
                retourcli = "Chemin non trouve..."
                logging.warning("PATH NOT FOUND => {}".format(newrep))

            self.thread_local.cwd = newrep
            retourcli += " Utilisation repertoire => " + self.thread_local.cwd
        else:
            retourcli = "Erreur la commande cd doit contenir 1 seul parametre"

        self.send_message(retourcli)

    def download_file(self, splitcommand):

        filename = os.path.join(self.thread_local.cwd, splitcommand[1])
        logging.debug("complete filename " + filename)

        if os.path.isfile(filename):
            logging.debug("File {} exist".format(filename))
            filesize = os.path.getsize(filename)
            self.thread_local.conn.send(("EXISTS " + str(filesize)).encode("utf8"))
            logging.debug("envoi au client de l'existence du fichier ok")
            user_response = self.thread_local.conn.recv(1024).decode()
            logging.debug("reception reponse download = " + user_response)

            # Confirmation de telechargement
            if user_response[:2] == 'OK':
                logging.debug("reponse OK")

                # ouverture fichier en lecture binaire
                with open(filename, 'rb') as f:
                    logging.debug("fichier  de{} octets a transferer".format(filesize))

                    t1 = datetime.datetime.utcnow()
                    for data in f:
                        self.thread_local.conn.sendall(data)
                    t2 = datetime.datetime.utcnow()
                    logging.debug("fin envoi en {} ".format(t2-t1))
                    self.thread_local.conn.send("".encode("utf8"))

                    print("Download completed !")

            # Reponse NON au telechargement
            else:
                print("\n Abandon Download par l'utilisateur...")
                return
        else:
            logging.debug("fichier non existant")
            self.thread_local.conn.send("ERR".encode("utf8"))

    # Action a traiter selon les commandes
    def implemented_command(self, command):
        if command == "exit" or command == "quit":
            self.thread_local.close()
            print("[+] Connection Closed Bye!")
            sys.exit(0)

        # Traitement du changement de répertoire
        if str(command).startswith("cd"):
            self.change_directory(command)
            return "skip"

        # Traitement du download
        if str(command).startswith("download"):
            self.download_file(str(command).split())
            logging.debug("Download function terminated")
            return "skip"

        # Commande systeme
        return command

    # Reception de la demande de prompt envoi du chemin pour le et reception de la commande
    def get_command(self):
        logging.debug("Receiving prompt request...")
        self.thread_local.conn.recv(512).decode("utf8")
        # Envoi du chemin pour l'afficher dans le shell du client
        logging.debug("Sending prompt...")
        # self.send_message(self.thread_local.cwd, self.thread_local.conn)
        self.send_message(self.thread_local.cwd)

        # Réception de la commande client
        print("\n[%d]: Waiting to Receive Command from Client...")
        command = self.thread_local.conn.recv(512).decode("utf8")
        print("\t[+] Command Received : %s " % command)

        # Traitement de la commande
        action = self.implemented_command(command)
        logging.debug("action : " + action)
        return action

    # Gestion du chemin local pour les threads
    def init_cwd_for_thread(self, conn):

        # Affichage de l'état des threads
        logging.debug("Etat des Threads: {}".format(threading.enumerate()))

        self.thread_local.conn = conn

        # https://stackoverflow.com/questions/1408171/thread-local-storage-in-python
        # On fixe une variable locale spécifique à chaque Thread pour retenir le path
        current_path = getattr(self.thread_local, 'cwd', None)
        if current_path is None:
            self.thread_local.cwd = os.getcwd()
            logging.debug(
                "Nice to meet you {} : Path: {}".format(threading.current_thread().name, self.thread_local.cwd))
        else:
            logging.debug("Welcome back {} : Path : {}".format(threading.current_thread().name, current_path))

    ####################################################################################
    # Fonction Principale gérant toute l'intéraction du client avec le thread du serveur
    ####################################################################################
    def threaded_listen_client(self, conn):

        # Initialisation du chemin local pour les threads
        self.init_cwd_for_thread(conn)

        # Boucle infinie le temps de la durée de vie du thread (shell client)
        # Boucle jusqu'a deconnexion explicite
        while True:

            # Récupération de la commande client et gestion du prompt
            command = self.get_command()
            if command == "skip":
                continue

            # ouverture d'un shell et execution de la command avec le répertoire courant défini par le thread
            sh = sp.Popen(command, shell=True, cwd=self.thread_local.cwd,
                          stdout=sp.PIPE,
                          stderr=sp.PIPE,
                          stdin=sp.PIPE)
            out, err = sh.communicate()

            # Encodage pour windows : cp850
            result = out.decode("cp850") + err.decode("cp850")

            # on Envoie la transmission : [longueur du message = 16 octets] +  [ reponse x octets]
            print("\t[+] Sending to Client ...")
            print("\t\t Result (truncated): %s (...)" % result[:150])
            self.send_message(result)


if __name__ == "__main__":

    try:
        host = str(sys.argv[1])
        port = int(sys.argv[2])
    except IndexError:
        host = "127.0.0.1"
        port = 5555
        print("Please use arg as <host:string><port:int>")
        print("Using default values : host {} , port {}".format(host, port))

    # On lance le server en tant que processus mais pas en tant que Thread
    server = ThreadedTCPServer(port, host)
    server.listen()
