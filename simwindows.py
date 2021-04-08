from tkinter import Tk, ttk, messagebox,Canvas, NW
from machine import *
from time import sleep
from threading import Thread
from PIL import Image, ImageTk


class Sim(Tk):
    def __init__(self):
        super().__init__()
        self.thr = None
        self.geometry("480x360")
        self.title("Simulateur ESP8266")
        photo = ImageTk.PhotoImage(file="esp8266.jpg")  # Nécessaire pour travailler avec différents types d'images
        canevas = Canvas(self, width=photo.width(), height=photo.height())
        canevas.config(height=photo.height(),
                       width=photo.width())  # Règle la taille du canvas par rapport à la taille de l'image
        canevas.create_image(0, 0, anchor=NW,
                             image=photo)  # Règle l'emplacement du milieu de l'image, ici dans le coin Nord Ouest (NW) de la fenetre
        canevas.pack()
        self.label = ttk.Label(self, text="bonjour les amis")
        self.label.pack()
        ttk.Button(self, text="Entree", command=self.on).pack()
        ttk.Button(self, text="Run", command=self.start).pack()
        ttk.Button(self, text="Stop", command=self.stop).pack()



        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    def refresh(self):
        self.label["text"] = Board.__str__(Board)
        self.update_idletasks()
        self.after(500, self.refresh)

    def start(self):
        self.thr = MonThread(self)
        self.thr.start()

    def stop(self):
        self.thr.stop()

    def on(self):
        if len(Board.gpio)>0:
            if Board.gpio[0].value() == 0:
                Board.gpio[0].value(1)
            else:
                Board.gpio[0].value(0)
            self.states()

    def on_close(self):

        # custom close options, here's one example:
        close = messagebox.askokcancel("Close", "Would you like to close the program?")
        if close:
            if self.thr is not None:
                self.thr.stop()
            self.destroy()

    def boucle(self):
        p = Pin(2, Pin.IN)
        a = ADC(0)
        p1 = Pin(5, Pin.OUT)
        while self.states():
            if p1.value() == 1:
                p1.value(0)
            else:
                p1.value(1)
            sleep(1)

    def states(self):
        return self.thr._etat


class MonThread(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self._etat = True
        self.sim = sim

    def run(self):
        print("depart")
        self.sim.boucle()


    def stop(self):
        self._etat = False


if __name__ == '__main__':
    f = Sim()
    f.mainloop()
