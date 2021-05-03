from typing import List, Union
import math
from tkinter import Canvas, Frame, OptionMenu, StringVar
from machine import Board
from wemos import Wemos


class AllServo(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.servos: List[ServoMoteurFrame] = []

    def add_servo(self):
        self.servos.append(ServoMoteurFrame(self))
        self.servos[-1].pack(side='left')

    def inspect(self, value: Union[bool, None] = None) -> bool:
        if value is None:
            if len(self.servos) == 0:
                return False
            else:
                return self.servos[0].servo.inspect
        if value:
            for s in self.servos:
                if not s.servo.inspect:
                    s.servo.inspect = True
                    s.servo.inspect_pwm()

        else:
            for s in self.servos:
                if s.servo.inspect:
                    s.servo.inspect = False
        return value


class ServoMoteurFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        listeOptions = [f"d{i}" for i in range(9)]
        self.v = StringVar()
        self.v.set(listeOptions[0])
        self.menu_option = OptionMenu(self, self.v, *listeOptions)
        self.menu_option.pack()
        self.servo = ServoMoteur(self, self.v.get())
        self.servo.pack()
        self.v.trace("w", self.callback)

    def callback(self, *args):
        self.servo.set_pwm_pin(self.v.get())


class ServoMoteur(Canvas):
    def __init__(self, master, wemos_pwm_pin="d3"):
        super().__init__(master, bg='grey', width=105, height=105)
        self.pwm_pin = Wemos.d_to_pin(wemos_pwm_pin)
        self.x0, self.y0, self.l = 55, 55, 50
        self.angle = 180
        self.angle_servo = 0
        self.create_oval(self.x0 - self.l, self.y0 - self.l, self.x0 + self.l, self.y0 + self.l)
        self.text = self.create_text(self.x0, self.y0 + 10, text="000")
        self.fleche = self.create_line(self.x0, self.y0,
                                       self.x0 + self.l * math.cos((self.angle_servo - 180) * math.pi / 180),
                                       self.y0 + self.l * math.sin((self.angle_servo - 180) * math.pi / 180),
                                       arrow='last', fill='black')
        self.inspect = False

    def set_pwm_pin(self, wemos_pwm_pin: str):
        self.pwm_pin = Wemos.d_to_pin(wemos_pwm_pin)

    def inspect_pwm(self):

        id = Board.search_pin(Board.pwm_chanel, self.pwm_pin)
        # if id != -1:
        #     print('inspection', id, Board.pwm_chanel[id].freq())
        # else:
        #     print('inspection', id)
        if id != -1:
            self.set_angle(int((Board.pwm_chanel[id].duty() - 20) * 1.8))
        if self.angle == self.angle_servo and self.inspect and self.master.master.master.pwm.get_etat():
            self.after(10, self.inspect_pwm)
        elif id != -1 and Board.pwm_chanel[id].freq() == 50 and self.master.master.master.pwm.get_etat():
            self.positionne()

    def set_angle(self, valeur: int):
        self.angle = min(max(valeur, 0), 180)
        if 0 <= valeur <= 180:
            self.itemconfigure(self.fleche, fill='black')
        else:
            self.itemconfigure(self.fleche, fill='red')

    def positionne(self):
        if self.angle > self.angle_servo:
            self.angle_servo += 1
            self.coords(self.fleche, self.x0, self.y0,
                        self.x0 + self.l * math.cos((self.angle_servo - 180) * math.pi / 180),
                        self.y0 + self.l * math.sin((self.angle_servo - 180) * math.pi / 180))
        elif self.angle < self.angle_servo:
            self.angle_servo -= 1
            self.coords(self.fleche, self.x0, self.y0,
                        self.x0 + self.l * math.cos((self.angle_servo - 180) * math.pi / 180),
                        self.y0 + self.l * math.sin((self.angle_servo - 180) * math.pi / 180))
        if self.angle_servo != self.angle and self.inspect:
            self.itemconfigure(self.text, text=f"{self.angle_servo:>03d}")
            id = Board.search_pin(Board.pwm_chanel, self.pwm_pin)
            if id != -1 and self.master.master.master.pwm.get_etat():
                self.set_angle(int((Board.pwm_chanel[id].duty() - 20) * 1.8))
            # print('positionne')
            self.after(2, self.positionne)
        elif self.master.master.master.pwm.get_etat() and self.inspect:
            self.inspect_pwm()
