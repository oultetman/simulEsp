from tkinter import Tk, ttk, messagebox
from machine import *
from time import sleep
from threading import Thread


class Sim(Tk):
    def __init__(self):
        super().__init__()
        self.thr = MonThread(self)
        self.thr.start()
        self.geometry("480x360")
        self.title("Simulateur ESP8266")
        self.label = ttk.Label(self, text="bonjour les amis")
        self.label.pack()
        ttk.Button(self, text="Entree", command=self.on).pack()
        ttk.Button(self, text="Run", command=self.thr.continu).pack()
        ttk.Button(self, text="Stop", command=self.thr.pause).pack()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    def refresh(self):
        self.states()
        self.after(100, self.refresh)

    def on(self):
        if Board.gpio[0].value() == 0:
            Board.gpio[0].value(1)
        else:
            Board.gpio[0].value(0)
        self.states()

    def on_close(self):

        # custom close options, here's one example:
        close = messagebox.askokcancel("Close", "Would you like to close the program?")
        if close:
            self.thr.stop()
            self.destroy()

    def boucle(self):
        p = Pin(2, Pin.IN)
        a = ADC(0)
        p1 = Pin(5, Pin.OUT)
        print("cool")
        while self.states():
            if p1.value() == 1:
                p1.value(0)
            else:
                p1.value(1)
            sleep(1)
            print("hello")

    def states(self):
        self.label["text"] = Board.__str__(Board)
        self.update_idletasks()
        return self.thr._etat


class MonThread(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self._etat = True
        self._pause = False
        self.sim = sim

    def run(self):
        self.sim.boucle()

    def stop(self):
        self._etat = False

    def pause(self):
        self._pause = True

    def continu(self):
        self._pause = False


if __name__ == '__main__':
    f = Sim()
    f.mainloop()
