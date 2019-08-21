# coding:utf8

import socket
import sys
import logging

logging.basicConfig(level=logging.WARNING)


class TCPClient(object):
    """
    Classe pour Client TCP
    """

    # Constructeur Client
    def __init__(self, pport, phost):
        self.port = pport
        self.host = phost
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # <= connection socket TCP

    # download fichier
    def download(self, command):
        logging.debug("download function starting...")
        splitcommand = command.split()

        if len(splitcommand) != 2:
            print("ERROR in Download command needs 1 arg : download <file>")
            return

        filename = splitcommand[1]
        data_exist_and_size = self.sock.recv(1024).decode("utf8")
        # Le fichier existe
        if data_exist_and_size[:6] == "EXISTS":
            logging.debug("server says file exist")
            filesize = int(data_exist_and_size[6:])
            message = input("File Exists, " + str(filesize) + "Bytes, download? (Y/N)? -> ")

            # Attention ici plus de deodage des reponses du sockets car nous ouvrons le fichier en binaire
            # L'utilisateur confirme le download
            if message == "Y":
                logging.debug("server ask for confirmation to download")
                self.sock.send("OK".encode("utf8"))

                f = open('new_' + filename, 'wb')
                logging.debug("fichier  : {} octets a recevoir".format(filesize))

                while filesize > 0:
                    logging.debug("Reste à download {} octets".format(filesize))
                    if filesize < 4096:
                        data = self.sock.recv(filesize)
                    else:
                        data = self.sock.recv(4096)
                    logging.debug("reception {} octets".format(len(data)))
                    f.write(data)
                    filesize = filesize - len(data)

                print("OK Download Complete!")

            else:
                self.sock.send("CANCEL".encode("utf8"))
                logging.debug("Reponse N au download")
                return
        else:
            print("File does not exist!")

    def get_command(self, prompt):
        command = ""

        while command == "":
            command = input(prompt)

        # si l'utilisateur demande de sortir du programme
        if command in ["exit", "quit", "stop", "logout"]:
            self.sock.send("exit".encode())
            self.sock.close()
            print("[+] Connection Closed ... Exiting program")
            sys.exit(0)

        if command.startswith("download"):
            splittedcommand = command.split()
            if len(splittedcommand) == 2:
                logging.debug("download command detected...")
                self.sock.send(command.encode("utf8"))
                logging.debug("download request sent...")
                self.download(command)
                logging.debug("download completed...")
                return "skip"
            else:
                print("Erreur dans la commande download : download <file>")
                return "echo Erreur dans la commande download : download <file>"

        # Si commande on la renvoie
        else:
            return command

    def connect(self):
        # Connection à la socket server
        self.sock.connect((self.host, self.port))
        print("Connected to %s on %s" % (host, port))

        while True:

            # 1er reception : répertoire courant
            logging.debug("Sending ASK_PROMPT.. ")
            self.sock.send("ASK_PROMPT".encode("utf8"))
            logging.debug("Retrieving prompt.. ")
            prompt = self.receive_message() + "> "
            logging.debug("PROMPT received: " + prompt)
            command = self.get_command(prompt)

            if command == "skip":
                logging.debug("Skipping command...")
                continue

            # Envoi de la commande au serveur
            logging.debug("Commande to send to server: " + command)
            self.sock.send(command.encode("utf8"))

            # on affiche le message de retour de la commande
            logging.debug("Retrieving message.. ")
            print(self.receive_message())
            logging.debug("END retrieving message.. ")

    def receive_message(self):

        # 1ere connection : récupération de la longueur du message 16 octets uniquement
        # 2eme et nieme connection : récupération du message par morceau de 1024 octets
        result = self.sock.recv(16).decode("utf8")

        # les 16 premiers caracteres de la réponse correspondent à la longeurs de la rep
        # ce formattage est défini par l'application coté serveur
        total_size = int(result[:16])
        logging.debug("Longueur message: {} octets".format(total_size))

        # les résultats de la commandes se trouvent donc à partir du 17eme caracteres
        result = result[16:]

        # Tant que la longeur total de la réponse est supérieure à ce que l'on à déjà reçu on continue de boucler
        while total_size > len(result):
            remain = total_size - len(result)
            logging.debug("Message en cours il reste {} octets".format(remain))

            # Si il reste plus de 1024 octets on télécharge par paquet de 1024
            if remain > 1024:
                data = self.sock.recv(1024).decode("utf8")
            # Sinon on prend juste ce qu'il reste
            else:
                data = self.sock.recv(remain).decode("utf8")

            result += data
        return result


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
    client = TCPClient(port, host)
    client.connect()



"""
# Test implémentation boucle de reception
# Attention pour fonctionner necessite la fermeture du socket 
# https://stackoverflow.com/questions/47436349/transferring-file-between-client-and-server-socket-error-and-attribute-error
with open('new_' + filename, 'wb') as f:
    while True:
        data = self.sock.recv(2048)
        if not data:
            logging.debug("fin boucle")
            break
        logging.debug("ecriture fichier")
        f.write(data)
f.close()
logging.debug("sortie boucle ecriture fichier")
"""
