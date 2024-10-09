import _thread
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

"""
rows 0-6
0. row for temperature

"""
def locked(method):
    def wrapper(self, *args, **kwargs):
        self.lock.acquire()
        result = method(self, *args, **kwargs)
        self.lock.release()
        return result
    return wrapper

class DisplayMock:
    def __init__(self) -> None:
        self.lock = _thread.allocate_lock()
        self.header = "Hello!"
        self.__clear()
    
    @locked
    def write_line(self, text: str, line: int, clear:bool = False):
        """ 
        text: 16 char
        line: 1-5
        clear: True = clear before printing
        """
        if clear:
            self.__clear()
        print(f"showing: {text}, line: {line}, clear: {clear}")
    
    @locked
    def clear(self):
        self.__clear()

    def __clear(self):
        # Prevents deadlock if locked method needs clear method
        print("Cleared")

    @locked
    def clear_all(self):
        print("Clear all")

    @locked
    def set_header(self, header):
        print(f"header {header}")

    @locked
    def off(self):
        print("off")
    
