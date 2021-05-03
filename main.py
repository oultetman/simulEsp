from machine import *
from wemos import Wemos
from esp8266_i2c_lcd import I2cLcd
from time import time

def irq_essai(pin: Pin):
    print("bonjour")

def main():
    out = [Pin(Wemos.d_to_pin(f"D{i}"), Pin.OUT) for i in range(6)]
    a = ADC(0)
    compteur = 0
    PWM(Pin(Wemos.d_to_pin("D6")), freq=50, duty=500)
    print(Board.pwm_chanel[0].frequence)
    servo = PWM(Pin(Wemos.d_to_pin("D3")), duty=20)
    servo1 = PWM(Pin(Wemos.d_to_pin("D0")), duty=120)
    enter = Pin(Wemos.d_to_pin("D8"), Pin.IN)
    d2 = Pin(Wemos.d_to_pin("d2"),Pin.OUT)
    d2.value(1)
    sleep(3)
    servo.duty(100)
    sleep(3)
    # enter.irq(irq_essai, Pin.IRQ_RISING)
    # i2c = I2C(0x38, scl=5, sda=4)
    # i2c1 = I2C(0x20, scl=5, sda=4)
    # print(i2c.scan())
    # lcd = I2cLcd(i2c,0x38,4,20)
    # lcd1 = I2cLcd(i2c1,0x20,2,16)
    # lcd.backlight_on()
    # lcd1.backlight_on()
    # print(Board.i2c_datas)
    # lcd.move_to(1,0)
    # lcd.putstr("Les amis")
    # lcd1.move_to(0,0)
    # lcd1.putstr("Bonjour")
    # lcd.move_to(1,2)
    # lcd.putchar("C")
    # lcd.move_to(1,3)
    # lcd.putchar("D")
    # sleep_ms(2000)
    # print("fin")
    # lcd.clear()
    while run():
        for i in range(12):
            servo.duty(20+10*i)
            servo1.duty(120-10*i)
            sleep_ms(1000)
    print("fin programme")