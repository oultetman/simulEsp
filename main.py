from typing import List
# class Board:
#     def __init__(self):
#         #Port entrée sortie
#         self.gpio: List[bool] = [False for i in range(16)]
#         # assignation des ports :
#         # 0 in, 1 out, 2 pullUp
#         self.gpio_in_out: List[int] = [0 for i in range(16)]
#
#     def __str__(self):
#         s = "|"
#         for v in self.gpio:
#             if v:
#                 s+="1|"
#             else:
#                 s+="0|"
#         return s


from machine import Pin, ADC, Board, print
from time import sleep

if __name__ == '__main__':
    b = Board()
    p = Pin(2, Pin.IN)
    a = ADC(0)
    p1 = Pin(5, Pin.OUT)
    while True:
        if p1.value() == 1:
            p1.value(0)
        else:
            p1.value(1)
        print(b)
        sleep(1)
