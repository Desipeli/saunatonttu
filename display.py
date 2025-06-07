from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# TODO: Maybe a message queue
class Display:
    """
    rows 0-5
    row 0 for temperature
    row 5 for passed time

    """
    def __init__(self) -> None:
        self.display = self.set_up_display()
        self.header = "Hello!"
        self.clear()

    def set_up_display(self) -> SSD1306_I2C:
        WIDTH = 128
        HEIGHT = 64
        i2c = I2C(0, scl = Pin(17), sda = Pin(16), freq=400000)
        display = SSD1306_I2C(WIDTH, HEIGHT, i2c)
        return display
    

    def write_line(self, text: str, line: int, clear:bool = False):
        """ 
        text: 16 char
        line: 1-4
        clear: True = clear before printing
        """
        if clear:
            self.clear()
        # clear the line first
        y = line * 10 + 2
        self.display.fill_rect(0, y, 128, 10, 0)
        self.display.text(text, 0, y)
        self.display.show()

    def clear(self):
        self.display.fill_rect(0,12, 128,40, 0)
        self.display.show()

    def clear_all(self):
        self.display.fill(0)
        self.display.show()

    def set_header(self, header):
        self.display.fill_rect(0,0, 128,12, 0)
        self.display.text(header,0,0)
        self.display.show()

    def set_footer(self, footer):
        self.display.fill_rect(0,52, 128,64, 0)
        self.write_line(footer, 5)
        self.display.show()

    def off(self):
        self.display.poweroff()
    
