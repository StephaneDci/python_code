# coding:utf8

import socket
import sys
import chardet


try:
    host = str(sys.argv[1])
    port = int(sys.argv[2])
except IndexError:
    host = "127.0.0.1"
    port = 5555
    print("Please use arg as <host:string><port:int>, will use ip: {} and port: {}".format(host, port))


# Connection à la socket server
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, port))
print("Connected to %s on %s" % (host, port))

while 1:
    command = input("Shell > ")
    print("COMMANDE : " + command)

    # commande pour sortir du programme
    if command in ["exit", "quit", "stop", "logout"]:
        conn.send("exit".encode())
        print("[+] Asking to Close Connection ")
        break

    # Si commande vide (utilisateur appuie sur return) on recommance la boucle
    elif command == "":
        continue

    # Sinon si l'utilisateur tape une commande => On envoie la commande au server
    conn.send(command.encode("utf8"))

    # 1ere connection : récupération de 1024 octets
    # 2eme et nieme connection : récupération du message par morceau de 1024 octets
    result = conn.recv(1024)
    print(chardet.detect(result)['encoding'])
    result = result.decode("utf8")

    # les 16 premiers caracteres de la réponse correspondent à la longeurs de la rep
    # ce formattage est défini par l'application coté serveur
    total_size = int(result[:16])
    print("total size received: ", total_size)
    # les résultats de la commandes se trouvent donc à partir du 17eme caracteres
    result = result[16:]

    # Tant que la longeur total de la réponse est supérieure à ce que l'on à déjà reçu on continue de boucler
    while total_size > len(result):
        data = conn.recv(1024).decode("utf8")
        result += data

    print("Resultat Commande: \n")
    print(result)


conn.close()
print("[+] Connection Closed ")
