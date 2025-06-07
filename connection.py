import network
from time import sleep
from display import Display

class Connection:
    def __init__(self, ssid: str, password: str, display: Display) -> None:
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.display = display

    def connect_wlan(self) -> bool:
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)

        self.display.write_line("Connecting to",1)
        self.display.write_line(self.ssid,2)
        tries = 5
        while not self.wlan.isconnected():
            # self.display.write_line(f"tries left {tries}", 4, True)
            sleep(2)
            print(self.wlan.status())
            tries -= 1
            if tries == 0:
                self.display.clear()
                self.display.write_line("connection to", 1)
                self.display.write_line(self.ssid,2)
                self.display.write_line("failed", 3)
                return False

        self.ip = self.wlan.ifconfig()[0]
        self.display.clear_all()
        self.display.write_line(self.ip,1)
        return True