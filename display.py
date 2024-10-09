from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

"""
rows 0-6
0. row for temperature

"""
class Display:
    def __init__(self) -> None:
        self.display = self.set_up_display()
        self.header = "Hello!"
        self.__clear()

    def set_up_display(self) -> SSD1306_I2C:
        WIDTH = 128
        HEIGHT = 64
        i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq=400000)
        display = SSD1306_I2C(WIDTH, HEIGHT, i2c)
        return display
    

    def write_line(self, text: str, line: int, clear:bool = False):
        """ 
        text: 16 char
        line: 1-5
        clear: True = clear before printing
        """
        if clear:
            self.__clear()
        self.display.text(text, 0, line * 10 + 2)
        self.display.show()
    

    def clear(self):
        self.__clear()

    def __clear(self):
        # Prevents deadlock if locked method needs clear method
        self.display.fill_rect(0,12, 128,64, 0)
        self.display.show()

    def clear_all(self):
        self.display.fill(0)
        self.display.show()

    def set_header(self, header):
        self.display.fill_rect(0,0, 128,12, 0)
        self.display.text(header,0,0)
        self.display.show()

    def off(self):
        self.display.poweroff()
    
