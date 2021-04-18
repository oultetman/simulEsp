from machine import *
from wemos import Wemos


def irq_essai(pin: Pin):
    print("bonjour")


def main():
    from esp8266_i2c_lcd import I2cLcd
    from time import time
    out = [Pin(Wemos.d_to_pin(f"D{i}"), Pin.OUT) for i in range(6)]
    a = ADC(0)
    compteur = 0
    PWM(Pin(Wemos.d_to_pin("D6")), freq=1, duty=500)
    enter = Pin(Wemos.d_to_pin("D8"), Pin.IN)
    enter.irq(irq_essai, Pin.IRQ_RISING)
    i2c = I2C(0x38, scl=5, sda=4)
    i2c1 = I2C(0x20, scl=5, sda=4)
    print(i2c.scan())
    lcd = I2cLcd(i2c,0x38,4,20)
    lcd1 = I2cLcd(i2c1,0x20,2,16)
    lcd.backlight_on()
    lcd1.backlight_on()
    print(Board.i2c_datas)
    lcd.move_to(1,0)
    lcd.putstr("Les amis")
    lcd1.move_to(0,0)
    lcd1.putstr("Bonjour")
    # lcd.move_to(1,2)
    # lcd.putchar("C")
    # lcd.move_to(1,3)
    # lcd.putchar("D")
    # sleep_ms(2000)
    # print("fin")
    # lcd.clear()
    # while True:
    #     lcd.move_to(0, 2)
    #     lcd.putstr("{:7d}".format(int(time())))
    #     sleep_ms(1000)
    while True:
        sleep_ms(100)