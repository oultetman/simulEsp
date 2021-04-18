from typing import Tuple
from tkinter import Tk, ttk, messagebox, Canvas, NW, Menu
from tkinter.font import Font
from machine import *
from time import sleep
from threading import Thread
from PIL import Image, ImageTk
from wemos import Wemos
from main import *


class Screen(Canvas):
    def __init__(self, master, model="1602", color="green", i2c_adress=0x38):
        super().__init__(master)
        if color == "green":
            self.color = '#B4D83B'
            self.color_dark = '#647C12'
            self.color_pen = '#000000'
        else:
            self.color = '#0467E6'
            self.color_dark = '#03295A'
            self.color_pen = '#B2D1F9'
        self.model = model
        self.i2c_address = i2c_adress
        self.nb_ligne = int(self.model[-2:])
        self.nb_col = int(self.model[:2])
        self.x0 = 15
        self.y0 = 35
        self.deltay = 25
        self.deltax = 14
        self.backscreen = self.create_rectangle(self.x0 - self.deltax + 1, self.y0 - self.deltay - 5,
                                                self.x0 + (self.nb_col + 2) * self.deltax,
                                                self.y0 + 5 + (self.nb_ligne - 1) * self.deltay, fill=self.color)
        self.font = Font(family='courier', size=18, weight='bold')
        self.ecran = [
            self.create_text(self.x0, self.y0 + i * self.deltay, text=" " * self.nb_col, font=self.font, anchor='sw',
                             fill=self.color_pen)
            for
            i in range(self.nb_ligne)]
        self.cursor = self.create_line(self.x0 + 1, self.y0 - 9, self.x0 + 13, self.y0 - 9, width=3, state='hidden')
        self.cursor_bloc = self.create_rectangle(self.x0, self.y0 - 23, self.x0 + 12, self.y0 - 9, fill=self.color_dark,
                                                 outline='#C0C2BC', state='hidden')
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_visible = False
        self.cursor_blink = False
        self.back_light = False
        self.backlight(False)
        self.display(False)
        # self.print("Bonjour les amis*")
        self.bind('<Button-1>', self.on_click)
        self._display = False
        d = (self.coords(self.backscreen))
        self.configure(width=d[2], height=d[3])

        self.cursor_repaint()
        self.i2c()

    def display(self, state: bool = True):
        if state:
            etat = 'normal'
        else:
            etat = "hidden"
        for l in self.ecran:
            self.itemconfigure(l, state=etat)
        self._display = state
        self.update_idletasks()

    def on_click(self, event):
        self.backlight(not self.back_light)
        print("bonjour")

    def backlight(self, state: bool = True):
        if state:
            self.itemconfigure(self.backscreen, fill=self.color)
        else:
            self.itemconfigure(self.backscreen, fill=self.color_dark)
        self.back_light = state
        self.update_idletasks()

    def cursor_repaint(self):
        if self.cursor_visible and self._display is True:
            self.coords(self.cursor, self.x0 + 1 + self.cursor_x * 14, self.y0 - 9 + self.cursor_y * self.deltay,
                        self.x0 + 13 + self.cursor_x * 14, self.y0 - 9 + self.cursor_y * self.deltay)
            self.coords(self.cursor_bloc, self.x0 + 1 + self.cursor_x * 14, self.y0 - 23 + self.cursor_y * self.deltay,
                        self.x0 + 13 + self.cursor_x * 14, self.y0 - 11 + self.cursor_y * self.deltay)
            self.itemconfigure(self.cursor, state="normal")
            if self.cursor_blink:
                if self.itemcget(self.cursor_bloc, 'state') == 'hidden':
                    # self.itemconfigure(self.cursor,state="normal")
                    self.itemconfigure(self.cursor_bloc, state="normal")
                else:
                    self.itemconfigure(self.cursor_bloc, state="hidden")
        else:
            self.itemconfigure(self.cursor, state="hidden")

        self.after(1000, self.cursor_repaint)

    def move_to(self, cursor_x: int, cursor_y: int):
        self.cursor_y = cursor_y
        self.cursor_x = cursor_x

    def print(self, chaine: str):
        s = ""
        s1 = ""
        pos = (self.cursor_y * self.nb_col + self.cursor_x) % (self.nb_col * self.nb_ligne)
        for l in self.ecran:
            s += self.itemcget(l, 'text')
        if pos + len(chaine) <= self.nb_col * self.nb_ligne:
            s = s[:pos] + chaine + s[pos + len(chaine):]
            pos = pos + len(chaine) + 1
            self.cursor_x = pos % self.nb_col - 1
            self.cursor_y = pos // self.nb_col
        else:
            s = s[:pos] + chaine
            s1 = s[self.nb_col * self.nb_ligne:]
            s = s[:self.nb_col * self.nb_ligne]
        for i, l in enumerate(self.ecran):
            self.itemconfigure(l, text=s[i * self.nb_col:(i + 1) * self.nb_col])
        if s1 != "":
            self.print(s1)
        self.update_idletasks()

    def clear(self):
        for l in self.ecran:
            self.itemconfigure(l, text=" " * self.nb_col)
        self.update_idletasks()

    def i2c(self):
        if len(Board.i2c_datas) != 0 and Board.i2c_address == 0:
            Board.i2c_address = self.i2c_address
            datas = []
            command = True
            i = 0
            while len(datas) < 2 and i < len(Board.i2c_datas):
                if Board.i2c_datas[i][0] & 0xFE == self.i2c_address:
                    datas.append(Board.i2c_datas.pop(i)[1])
                else:
                    i += 1
            if len(datas) > 0:
                if datas[0] & 0x01 == 0x01:
                    command = False
                if len(datas) == 2:
                    data = (datas[0] & 0xF0) | datas[1] >> 4
                    if command:
                        if data == 0x00:
                            self.backlight(False)
                        elif data & 0xF8 == 0x08:
                            self.cursor_visible = (data & 0x02 == 0x02)
                            self.cursor_blink = (data & 0x01 == 0x01)
                            self.display(data & 0x04 == 0x04)
                        elif data == 0x01:
                            self.clear()
                        elif data == 0x02:
                            self.home()
                        elif data & 0x80 == 0x80:
                            if data & 0x40 == 0x40:
                                self.cursor_x = ((data & 0x7F) - 0x40) % self.nb_col
                                self.cursor_y = ((data & 0x7F) - 0x40) // self.nb_col * 2 + 1
                            else:
                                self.cursor_x = (data & 0x7F) % self.nb_col
                                self.cursor_y = ((data & 0x7F) // self.nb_col) * 2
                    else:
                        self.print(chr(data))
                else:
                    data = datas[0]
                    print(data)
                    if data == 0x00:
                        self.backlight(False)
                    elif data == 0x08:
                        self.backlight(True)
        Board.i2c_address = 0
        self.after(1, self.i2c)

    def home(self):
        self.cursor_x, self.cursor_y = 0, 0


class Chronogramme(Canvas):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=1010, height=100)
        self.create_rectangle(3,3,1010,100)
        for i in range(1,len(self.master.enregistrement.memory)):
            self.create_line(i-1+3, self.map(self.master.enregistrement.memory[i-1][6]), i+3, self.map(self.master.enregistrement.memory[i][6]), width=1)

    def map(self ,value):
        return value*80+10


class Enregistreur:
    def __init__(self, delta_time_ms: int, taille: int, type_board="esp8266"):
        self.memory: List[List[int]] = [[] for i in range(taille)]
        self.taille = taille
        self.delta_time_ms = delta_time_ms
        self.role = False
        self.index = 0
        self._run = False

    def is_run(self):
        return self._run is True

    def add(self):
        if self.is_run():
            self.memory[self.index] = [pin.value() for pin in Board.gpio]
            self.index += 1
            if self.index == self.taille:
                if self.role:
                    self.reset()
                else:
                    self.stop()

    def reset(self):
        self.index = 0

    def run(self):
        self.reset()
        self._run = True

    def stop(self):
        self._run = False
        print(self)

    def __str__(self):
        s = ""
        for e in self.memory:
            s += str(e) + "\n"
        return s


class Sim(Tk):
    def __init__(self):
        super().__init__()
        menubar = Menu(self)
        self.config(menu=menubar)
        ajouter = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajouter", menu=ajouter)
        ajouter_ecran = Menu(menubar, tearoff=0)
        ajouter.add_cascade(label='Ecran i2c', menu=ajouter_ecran)
        ajouter_ecran.add_command(label="Ecran 2004 0x38", command=self.ajouter_ecran_2004)
        ajouter_ecran.add_command(label="Ecran 1602 0x20", command=self.ajouter_ecran_1602)
        ajouter.add_cascade(label='Ajouter Rich Field')
        ajouter.add_cascade(label='servo moteur')
        ajouter.add_cascade(label='gbf')
        ajouter.add_cascade(label='chronogrammes', command=lambda: Chronogramme(self).pack())
        self.thr = None
        self.pwm = None
        self.irq = None
        # self.geometry("512x500")
        self.title("Simulateur ESP8266")

        # self.label = ttk.Label(self, text="bonjour les amis")
        # self.label.pack()
        # ttk.Button(self, text="Entree", command=self.on).pack()
        ttk.Button(self, text="Run", command=self.start).pack()
        ttk.Button(self, text="Stop", command=self.stop).pack()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.photo = ImageTk.PhotoImage(Image.open("esp8266wemos.png"))
        self.canevas = Canvas(self, width=self.photo.width(), height=self.photo.height())
        self.canevas.create_image(0, 0, anchor=NW, image=self.photo)
        self.w = Wemos(self.canevas)
        self.canevas.pack()
        # self.ecran1 = Screen(self, "1602", "green", 0x20)
        # self.ecran1.pack()
        self.canevas.bind('<Button-1>', self.on_click_bp1)
        self.enregistrement = Enregistreur(10, 1000)
        self.refresh()

    def ajouter_ecran_2004(self):
        Screen(self, "2004", "blue", 0x38).pack()

    def ajouter_ecran_1602(self):
        Screen(self, "1602", "green", 0x20).pack()

    def on_click_bp1(self, event):
        # print("Mouse position: ({} {})".format(event.x, event.y))
        pin = self.canevas.find_closest(event.x, event.y)[0] - 2
        # print(pin)
        self.w.toggle_entry(self.w.pins[pin])

    def refresh(self):
        self.w.refresh()
        self.after(1, self.refresh)

    def enregistre(self):
        self.enregistrement.add()
        if self.enregistrement.is_run():
            self.after(self.enregistrement.delta_time_ms, self.enregistre)

    def start(self):
        self.thr = MonThread()
        self.pwm = Pwm()
        self.irq = IrqDetect()
        self.thr.start()
        self.pwm.start()
        self.irq.start()
        self.enregistrement.run()
        sleep(1)
        self.enregistre()

    def stop(self):
        self.thr.stop()
        self.pwm.stop()
        self.irq.stop()
        self.enregistrement.stop()

    def on_close(self):

        # custom close options, here's one example:
        close = messagebox.askokcancel("Close", "Would you like to close the program?")
        if close:
            if self.thr is not None:
                self.thr.stop()
                self.pwm.stop()
            self.destroy()

    def states(self):
        return self.thr._etat


class MonThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._etat = True

    def run(self):
        print("depart esp")
        Board.run = True
        main()
        print("arret esp")

    def stop(self):
        self._etat = False
        Board.run = False


class Pwm(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._etat = True
        self.pwm_counter = 0

    def run(self):
        print("depart pwm")
        while self._etat:
            self.pwm_counter += 1
            sleep(1 / 10000)
            if self.pwm_counter >= 10000 / PWM.frequence:
                self.pwm_counter = 0

        print("arret pwm")

    def stop(self):
        self._etat = False
        Board.pwm = False


class IrqDetect(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._etat = True

    def run(self):
        print("depart irq")
        sleep(1)
        while self._etat and Board.irq:
            for pin in Board.gpio:
                if pin.irq_enable:
                    if pin.front == pin.trigger:
                        pin.handler(pin)
                        pin.front = -1
            sleep(1 / 1000)
        print("arret irq")

    def stop(self):
        self._etat = False
        Board.pwm = False


if __name__ == '__main__':
    f = Sim()
    f.mainloop()
