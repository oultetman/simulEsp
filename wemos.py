from typing import Tuple
from machine import *
from tkinter import *


class Visu_led:
    def __init__(self, canvas: Canvas, x: int, y: int, largeur: int, hauteur: int):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
        self.led = None
        self.states_color = ['red', 'green', 'gray']
        self.add_canavas()

    def add_canavas(self):
        self.led = self.canvas.create_rectangle(self.x, self.y, self.x + self.largeur, self.y + self.hauteur,
                                                fill='gray')

    def set_Color(self, couleur: Tuple[str, str, str]):
        self.states_color = list(couleur)

    def out(self, niveau: int):
        self.canvas.itemconfig(self.led, fill=self.states_color[niveau])


class BoardLed(Visu_led):
    def __init__(self, canvas: Canvas, x: int, y: int, largeur: int, hauteur: int):
        super().__init__(canvas, x, y, largeur, hauteur)
        self.set_Color(('gray', '#068FFB', 'gray'))


class Wemos:
    pins = [16, 5, 4, 0, 2, 14, 12, 13, 15, 13, 12, 14, 4, 5, 14]

    def __init__(self, canevas: Canvas):
        self.canevas = canevas
        self.leds: List[Visu_led] = [Visu_led(canevas, 324 - i * 14, 7, 10, 10) for i in range(6)]
        self.leds += [Visu_led(canevas, 314 - i * 14, 7, 10, 10) for i in range(6, 16) if i not in [12, 13]]
        self.leds += [BoardLed(canevas, 183, 179, 10, 5)]
        self.leds_board = [BoardLed(canevas, 183, 145, 10, 5), BoardLed(canevas, 343, 201, 5, 10)]

    def add_canevas(self):
        for l in self.leds:
            l.add_canavas()

    def d_to_pin(pin: str):
        if pin[0].upper() == "D":
            try:
                return Wemos.pins[int(pin[1:])]
            except:
                raise ValueError

    def refresh(self):
        for i, p in enumerate(self.pins):
            valeur = Board.value_By_pin(p)
            if valeur == 2:
                self.leds[i].out(2)
            else:
                self.leds[i].out(valeur)
        if Board.run:
            self.leds_board[0].out(1)
        else:
            self.leds_board[0].out(0)
        if Board.wifi:
            self.leds_board[1].out(1)
        else:
            self.leds_board[1].out(0)
        for pwm in Board.pwm_chanel:
            if pwm.maxi > self.canevas.master.pwm.pwm_counter:
                pwm.pin.on()
            else:
                pwm.pin.off()

    def toggle_entry(self, id_pin: int):
        index = Board.search_pin(Board.gpio, id_pin)
        if index != -1:
            if Board.gpio[index].mode() == Pin.IN:
                Board.gpio[index].toggle()
