import uasyncio
import json
import micropython
import network
import socket
import sys
import temperature
from machine import Pin, PWM
from time import sleep
from config import SSID, PASSWORD, SECRET
from display import Display
from display_mock import DisplayMock
from Dht11 import DHT11

MID = 1_500_000
MIN = 1_000_000
MAX = 2_000_000
START = MID
RETURN = MID + 50_000
END = 1_900_000

SHUTTING_DOWN = -1
READY = 1
TURNING = 2
WARMING = 3

class Main:

    def __init__(self) -> None:
        self.pwm = PWM(Pin(28))
        self.pwm.freq(50)
        self.pwm.duty_ns(START)

        self.internal_temp = 0
        self.temp = 0

        self.wlan = network.WLAN(network.STA_IF)
        self.status = 0 #-1: shutting down 1: ready, 2: turning, 3: turned
        self.display = Display()
        self.html, self.css = self.load_files()
        self.ip = None
        self.html, self.css = self.load_files()
        self.connect_wlan()

    async def run(self):
        server = uasyncio.start_server(self.handle_request, '0.0.0.0', 80)
        uasyncio.create_task(server)
        uasyncio.create_task(self.check_temperature())
        self.status = READY
        self.display.write_line("Ready", 1, True)
        self.display.write_line(str(self.ip), 2)
        while True:
            await uasyncio.sleep(0)
            

    async def check_temperature(self):
        while True:
            try:
                self.internal_temp = temperature.read_temp()
            except Exception as e:
                print("Temp error", e)
            try:
                self.display.set_header(f"{self.temp} C   {self.internal_temp} C")
                print(self.temp, self.internal_temp)
            except Exception as e:
                print(e)
            await uasyncio.sleep_ms(10000)

    def load_files(self) -> tuple:
        page = open("index.html", "r")
        html = page.read()
        page.close()

        page = open("styles.css", "r")
        css = page.read()
        page.close()
        return html, css

    def connect_wlan(self) -> None:
        
        self.wlan.active(True)
        self.wlan.connect(SSID, PASSWORD)

        self.display.write_line("Connecting to",1)
        self.display.write_line(SSID,2)
        tries = 5
        while not self.wlan.isconnected():
            sleep(2)
            print(self.wlan.status())
            tries -= 1
            if tries == 0:
                self.display.clear()
                self.display.write_line("connection to", 1)
                self.display.write_line(SSID,2)
                self.display.write_line("failed", 3)

        self.ip = self.wlan.ifconfig()[0]
        print("connected, ip:", self.ip)

    async def sauna_on(self):
        if self.status not in [READY, WARMING]: return
        self.status = TURNING
        try:
            self.display.write_line("Turning servo", 1, True)
            self.pwm.duty_ns(END)
            await uasyncio.sleep_ms(3000)
            self.pwm.duty_ns(RETURN)
            self.status = WARMING
            self.display.write_line("Warming", 1, True)
        except Exception as e:
            print(e)

    async def handle_request(self, reader, writer):

        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        try:
            raw_request = await reader.read(2048)
            if b'GET /styles.css' in raw_request:
                print("GET /styles.css")
                response = 'HTTP/1.0 200 OK\r\nContent-Type: text/css\r\n\r\n' + self.css
                response = response.encode('utf-8')

            elif b'GET /status' in raw_request:
                print("GET /status")
                data = {
                    "internal_temperature": temperature.read_temp(),
                    "status": self.status
                }
                json_data = json.dumps(data)
                response += json_data.encode('utf-8')
            
            elif b'GET /' in raw_request:
                print("GET /")
                response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n' + self.html
                response = response.encode('utf-8')

    
            elif b'POST' in raw_request:
                double_newline_index = raw_request.find(b'\r\n\r\n')
                body = raw_request[double_newline_index + 4:]
                content = json.loads(body.decode('utf-8'))

                if "secret" not in content or content["secret"] != SECRET:
                    response = b'HTTP/1.0 401 Unauthorized\r\nContent-Type: application/json\r\n\r\n'
                    data = {
                        "error": "Unauthorized"
                    }
                    data = json.dumps(data)
                    response += data.encode('utf-8')

                elif "shutdown" in content:
                    if content["shutdown"] == "now":
                        data = {
                            "status": "shutting down"
                        }
                        json_data = json.dumps(data)

                        
                        response += json_data.encode('utf-8')
                        uasyncio.create_task(self.shutdown())

                elif "servo" in content:
                    if content["servo"] == "turn":
                        uasyncio.create_task(self.sauna_on())
                else:
                    response = b'HTTP/1.0 400 Bad Request\r\nContent-Type: application/json\r\n\r\n'
                    data = {
                        "error": "Invalid command"
                    }
                    json_data = json.dumps(data)
                    response += json_data.encode('utf-8')


            writer.write(response)
            await writer.drain()
            await writer.wait_closed()

        except Exception as e:
            print(e)

    async def shutdown(self):
        while self.status == TURNING:
            await uasyncio.sleep(0)
        self.status = SHUTTING_DOWN
        self.display.write_line("Shutting down",5)
        sleep(6)
        self.display.off()
        sys.exit()

if __name__ == "__main__":
    main = Main()
    try:
        uasyncio.run(main.run())
    except Exception as e:
        print(e)
        main.shutdown()
    finally:
        uasyncio.new_event_loop()