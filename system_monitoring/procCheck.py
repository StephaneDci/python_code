# -*- coding: utf-8 -*-

"""
##############################################################################################

INFLUXDB Generator pour la surveillance des processus systèmes Linux

Requis    : Python > 3.4
Input     : Fichier Yaml décrivant les processus à surveiller (format spécifique)
Output    : Sortie de résultat au format InfluxDB
Revision  : 2.0 08.07.18 - réecriture complète (SDI)
ChangeLog : - Modification du format Yaml de configuration
          : - Ajout d'un nom unique associé à un processus (survname)
Statut    : 08.07.18 a tester avant MEP
          : 09.07.18 tests via plugin telegraf OK (après modification format sortie InfluxDB)
          :          correction des \x00 : proc_info.replace("\x00", "")
          : 19.07.18 modification dans la sortie sur les tags

Basé sur  : https://github.com/AAbouZaid/proccheck-telegraf-influxdb/blob/master/procCheck.py
###############################################################################################
"""

import os
import sys
import yaml
import logging

# Configuration de loggin pour les tests et debugs
logging.basicConfig(level=logging.WARNING, format='%(levelname)s : %(funcName)s - %(message)s')


"""
##################################
#           Fonctions
##################################
"""


# Ouvre le fichier yaml contenant les processus à surveiller
def open_yaml_file(yaml_file):
    try:
        os.path.isfile(yaml_file)
    except TypeError:
        print("Cannot open YAML file: %s." % yaml_file)
        sys.exit(1)
    with open(yaml_file, 'r') as procsYamlFile:
        try:
            yaml_content = yaml.load(procsYamlFile)
        except yaml.YAMLError as yamlError:
            yaml_content = yamlError
            print(yamlError)
    return yaml_content


# Récuperation des infos dans /proc
def get_system_procs():
    """
    Recupere dictionnaire de tous les processus systemes
    args : arguments de lancement du processus (recupéré via /proc/xx/cmdline)
    name : nom de lancement du processus (recupéré via /proc/xx/comm)
    :return: Dictionnaire des processus du système avec le format suivant:
             { pid: {args: xxx, name: yyyy} }
    """
    allsystem_ps = dict()
    # Loop over pids in /proc.
    pidlist = filter(lambda pidx: pidx.isdigit(), os.listdir('/proc'))

    for pid in pidlist:
        # recherche les arguments (command line) dans le fichier /proc/xx/cmdline
        proc_args = get_proc_info(pid, 'cmdline')
        # recherche du nom de l'exe dans le fichier comm
        proc_bin = get_proc_info(pid, 'comm')
        if proc_args:
            allsystem_ps.update({pid: {"name": proc_bin, "args": proc_args}})
    return allsystem_ps


# Get info from any file inside "/proc/pid/path_name.
# PathName is either comm or cmdline
def get_proc_info(pid, path_name):
    try:
        proc_info = open(os.path.join('/proc', pid, path_name), 'r').read().rstrip('\n')
        proc_info = proc_info.replace("\x00", "")
    except IOError:
        proc_info = "IO ERROR"
        print("IOError")
    return proc_info


# Retourne un dictionnaire des processus trouvé
def found_matching_ps(allprocessrunning, listprocesstowatch):
    """
    Recherche des process présents sur la machines à partir d'une configuration Yaml.
    La recherche se fait via 2 méthodes décrites dans la configuration

    Attention risque d'erreur si la configuration renvoit plusieurs fois le même processus

    I - par nom de process dans /proc/XX/comm

    byProcName:                                         <= search_method
        sshd1:                                          <= survname (nom unique)
          label : "sshd-process"                        <= label (pour affichage / commentaire)
          psname : "sshd"                               <= psname (nom a rechercher)

    II - par nom de process dans /proc/XX/comm ET de presence d'un motif de cmdline dans /proc/XX/cmdline

    byProcNameAndCmdline:                               <= search_method
        evolution-addre1:                               <= survname (nom unique)
          label : "evolution-address"                   <= label (pour affichage / commentaire)
          psname : "evolution-addre"                    <= psname (nom a rechercher)
          psargs: "--own-path/org/gnome/evolution"      <= required_cmdline (partie de cmdline a rechercher)


    :param allprocessrunning:   Dictionnaire de Tous les processus systèmes actifs via parcourt de /proc/XX
    :param listprocesstowatch:  Dictionnaire du Fichier yaml contenant les processus a surveiller
    :return:                    Dictionnaire contenant les processus trouvés
                format du Dictionnaire de retour:
                {survname:{search:<search-method>,string:<"" | "required_cmdline">, label:<label>, PID:<pid >}
    """

    # Declaration du dictionnaire final
    dict_founds_matching_process = dict()

    # Parcourt des méthodes de recherches
    for search_method in ('byProcName', 'byProcNameAndCmdline'):
        # Parcourt du dictionnaire du fichier yaml
        for survname, args in listprocesstowatch[search_method].items():

            # Extraction des elements de recherches souhaites depuis le fichier yaml
            label = args.get("label")
            required_psname = args.get("psname")

            # Extraction ligne de commande si méthode recherche byProcNameAndCmdline
            search_cmdline = True if search_method == "byProcNameAndCmdline" else False
            required_cmdline = str(args.get("psargs")) if search_cmdline else ""

            # Parcourt du dictionnaire des processus présents
            for pid, dict_procargs in allprocessrunning.items():
                temporarydict = dict()

                # Si l'on trouve le nom du process correspondant dans notre fichier (required_psname)
                if dict_procargs['name'] == required_psname:

                    # Si l'on trouve les bons argumants si recherche par byProcNameAndCmdline
                    # OU si recherche par ProcessusName uniquement
                    if (search_cmdline and dict_procargs['args'].find(required_cmdline) > 0) or (not search_cmdline):
                        # Constitution du dictionnaire
                        dict_procargs['search'] = search_method
                        dict_procargs['string'] = required_cmdline
                        dict_procargs['label'] = label
                        dict_procargs['PID'] = pid
                        # Super important !! Bien penser a faire une copy du dictionnaire !! (.copy)
                        # sinon les deux dictionnaires sont équivalents et erreurs dans les libellés possible
                        temporarydict[survname] = dict_procargs.copy()
                        # Ajout au dictionnaire final
                        dict_founds_matching_process.update(temporarydict)

    return dict_founds_matching_process


# Cherche les processus manquants qui n'ont pas été trouvés
def find_missing_ps(matched_ps, requiredps):
    """
    Methode permettant de trouver les processus non présents que l'on souhaiter superviser
    :param matched_ps: Les processus trouvés correspondant aux critères
    :param requiredps: La liste complète des processus à surveiller
    :return: Dictionnaire des processus manquants
             format du Dictionnaire de retour:
             {survname:{search:<search-method>,string:<"" | "required_cmdline">, label:<label>, PID:<00000>}
    """
    dict_missing = dict()
    # Parcourt des différentes méthodes
    for search_method in ('byProcName', 'byProcNameAndCmdline'):
        # Parcourt du dictionnaire des processus souhaités
        for key in requiredps.get(search_method):
            temp_dict = dict()
            # Si on ne trouve pas la Clé qui est le nom de la surveillance
            # On ajoute les éléments au dictionnaire avec un PID = 00000
            if matched_ps.get(key) is None:
                logging.debug("Missing surv: {}".format(key))
                temp_dict['search'] = search_method
                temp_dict['string'] = "" if search_method == "byProcName" \
                                         else requiredps.get(search_method).get(key).get('psargs')
                temp_dict['label'] = requiredps.get(search_method).get(key).get('label')
                temp_dict['name'] = requiredps.get(search_method).get(key).get('psname')
                temp_dict['PID'] = "00000"
                dict_missing[key] = temp_dict
    return dict_missing


# Generate influx DB output
def generate_influxdb_out(dict_procs):
    """
    Permet de générer une sortie au format Influx DB
    ATTENTION format capricieux => <serie> cle=val,cle2=val2 timestamp
    https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/

    Les espaces sont obligatoires , les string doivent être mises sous quotes ""
                                    les int ne doivent pas etre mis sous quotes
    NB le timestamp et les tags sont ajoutés automatiquement

    :param dict_procs: Dictionnaire formatté à mettre au format influxDB
    :return: sortie exemple

    NB pattern is set to "none" when search  is byProcName

    Sortie via appel du script en direct :
    *) python3.4 procCheck4.py
        ProcCheck2b pid=1515,survname="sshd1",exe="sshd",label="sshd-process",search="byProcName",pattern="none"
        ProcCheck2b pid=2772,survname="logmagent",exe="java",label="logmagent",search="byProcNameAndCmdline",pattern="logmagent.jar"

    Sortie via plugin Telegraf:
    (...)
        [[inputs.exec]]
        commands = ["/bin/python3.4 /etc/telegraf/telegraf.d/procCheck.py -f /etc/telegraf/telegraf.d/procList.yml"]
    *) telegraf -test -config /etc/telegraf/telegraf.conf -config-directory /etc/telegraf/telegraf.d
        > ProcCheck2b,environnement=SINT,host=logm-sint-alrt1,projet=ALRT,role=ALRT pattern="none",pid=28490,survname="sshd1",exe="sshd",label="sshd-process",search="byProcName" 1531127361000000000
        > ProcCheck2b,environnement=SINT,host=logm-sint-alrt1,projet=ALRT,role=ALRT search="byProcName",pattern="none",pid=36819,survname="crond",exe="crond",label="crond_process" 1531127361000000000
        > ProcCheck2b,environnement=SINT,host=logm-sint-alrt1,projet=ALRT,role=ALRT exe="telegraf",label="Telegraf_metrics",search="byProcName",pattern="none",pid=46514,survname="telegraf1" 1531127361000000000


    """

    for survname, procInfo in dict_procs.items():
        pattern = procInfo["string"] if len(procInfo["string"]) > 0 else "none"

        output_values = {
            'pluginName': "procCheck2f",
            'pid': procInfo["PID"],
            'psname': procInfo["name"],
            'pattern_cmdline': pattern,
            'search_by': procInfo["search"],
            'labelname': procInfo["label"],
            'survname': survname
        }

        # Evolution du 19.07 : modification des tags
        output_keys = ('%(pluginName)s,processus=%(psname)s,pid=%(pid)s' % output_values)
        output_data = ('psname="%(psname)s",survname="%(survname)s",pid=%(pid)s,'
                       'pattern_cmdline="%(pattern_cmdline)s",search_by="%(search_by)s",labelname="%(labelname)s"' % output_values)

        # In InfluxDB format, first group is tags names, and second group is values.
        print("%s %s" % (output_keys, output_data))


# Permet de fusionner deux dictionnaires Pour les version de Python < 3.5
def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


"""
##################################
#        Programme Main
##################################
"""

# ouvre le fichier d'entrée yaml sous forme de dictionnaire
# procList_yml = open_yaml_file("procList.yml")  <= pour les tests locaux
procList_yml = open_yaml_file("/etc/telegraf/telegraf.d/procList.yml")

# recupère l'ensemble des infos des processus dans /procs pour le systeme
# TODO remplacer si besoin pour les tests locaux :
runningSystemProcs = get_system_procs()
#runningSystemProcs = open_yaml_file("runningProcs.yml")    # <= pour les tests locaux

# trouve dans les processus sur le systeme ceux de la liste byName
dick_matching_ps = found_matching_ps(runningSystemProcs, procList_yml)
logging.debug(dick_matching_ps)

# Cheche les processus manquant dans notre list
dict_missing_ps = find_missing_ps(dick_matching_ps, procList_yml)
logging.debug(dict_missing_ps)

# Final Dictionnary (missing ps and matching process)
# To merge dict : https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
# This method needs Python >= 3.5 :  dict_final_ps = {**dick_matching_ps, **dict_missing_ps}
dict_final_ps = merge_two_dicts(dick_matching_ps, dict_missing_ps)
logging.debug(dict_final_ps)

# Generation de la sortie au format influxDB
generate_influxdb_out(dict_final_ps)
