# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------------------------------
# Classe IHM permettant le lancement du parsing et l'affichage des logs
# 1 thread pour l'IHM et 1 pour la fonction de parsing
# Auteur : SDI
# Date   : 26/10/2019
# Objectif : educationnal purpose only. Merci de respecter les copyrights
# ------------------------------------------------------------------------------------------------------

import queue
import logging
import signal
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W
import threading

from tkinter import StringVar, BooleanVar, Spinbox, Text
from functools import partial
from camptocamp.processor import Processing
from camptocamp import logger


class ActionsIHMParsing:
    """
    Classe pour les actions lançées depuis l'IHM pour le parsing.
    """
    def __init__(self, urlvoie, mode_maj, backend):
        """
        init de la classe
        :param urlvoie: l'url de la voie
        :param mode_maj: le mode de mise à jour
        :param backend: le backend pour insertion (liste)
        """
        self.urlvoie = urlvoie.get()
        self.mode_maj = mode_maj.get()
        back = backend.get()
        self.backend = list()
        self.backend.append(back)
        # Lancement du parsing dans un nouveau thread pour préserver l'IHM
        threading.Thread(target=self.run).start()

    def run(self):
        """
        Lancement du processing (dans un thread séparé de celui de l'IHM)
        :return:
        """
        processor = Processing(self.urlvoie, backends=self.backend, update=self.mode_maj)
        processor.parse()


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """

    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        """
        Affichage d'un message de log
        :param record: le message
        """
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


class FormUi:

    def __init__(self, frame):
        self.frame = frame
        # Create a combobbox to select the logging level
        values = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        self.level = tk.StringVar()
        ttk.Label(self.frame, text='Level:').grid(column=0, row=0, sticky=W)
        self.combobox = ttk.Combobox(
            self.frame,
            textvariable=self.level,
            width=25,
            state='readonly',
            values=values
        )
        self.combobox.current(0)
        self.combobox.grid(column=1, row=0, sticky=(W, E))
        # Create a text field to enter a message
        self.message = tk.StringVar()
        ttk.Label(self.frame, text='Message:').grid(column=0, row=1, sticky=W)
        ttk.Entry(self.frame, textvariable=self.message, width=25).grid(column=1, row=1, sticky=(W, E))
        # Add a button to log the message
        self.button = ttk.Button(self.frame, text='Submit', command=self.submit_message)
        self.button.grid(column=1, row=2, sticky=W)

    def submit_message(self):
        # Get the logging level numeric value
        lvl = getattr(logging, self.level.get())
        logger.log(lvl, self.message.get())


class ParsingUi:
    """
    UI permettant le lancement du parsing
    """

    def __init__(self, frame):
        self.frame = frame
        stringvar_urlvoie = StringVar(self.frame, value='https://www.camptocamp.org/waypoints/40766/fr/presles-eliane')
        label_urlvoie = ttk.Label(self.frame, text="Entrer l'url d'une voie")
        entry_urlvoie = ttk.Entry(self.frame, textvariable=stringvar_urlvoie, width=80)
        label_mode_maj = ttk.Label(self.frame, text="Forcer la mise à jour")
        booleanvar_mode_maj = BooleanVar(self.frame, "1")
        checkbox_mode_maj = ttk.Checkbutton(self.frame, variable=booleanvar_mode_maj)
        label_spinbox_backend = ttk.Label(self.frame, text="Choix du Stockage")
        spinbox_backend = Spinbox(self.frame, values=['db', 'mongodb', 'pickle', 'aucun'])

        # Bouton de lancement de la classe permettant le parsing
        button = ttk.Button(self.frame, text='Parse',
                            command=partial(ActionsIHMParsing,
                                            stringvar_urlvoie, booleanvar_mode_maj, spinbox_backend))

        # Positionnement des éléments
        label_urlvoie.grid(column=0, row=0)
        entry_urlvoie.grid(column=2, row=0, columnspan=3, padx=20)
        label_mode_maj.grid(column=0, row=1)
        checkbox_mode_maj.grid(column=2, row=1, columnspan=3)
        label_spinbox_backend.grid(column=0, row=2)
        spinbox_backend.grid(column=2, row=2, columnspan=3)
        button.grid(column=0, row=3, columnspan=3)


class App:
    """
    L'application permettant la construction de l'IHM
    """

    def __init__(self, root):
        self.root = root
        root.title('CampToCamp Parser')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        form_frame = ttk.Labelframe(horizontal_pane, text="Debug")
        form_frame.columnconfigure(1, weight=1)
        horizontal_pane.add(form_frame, weight=1)
        console_frame = ttk.Labelframe(horizontal_pane, text="Log Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        third_frame = ttk.Labelframe(vertical_pane, text="Configuration Parsing")
        vertical_pane.add(third_frame, weight=1)

        # Initialize all frames
        self.form = FormUi(form_frame)
        self.console = ConsoleUi(console_frame)
        self.third = ParsingUi(third_frame)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def quit(self, *args):
        self.root.destroy()


def main():
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    app = App(root)
    app.root.mainloop()


if __name__ == '__main__':
    main()
