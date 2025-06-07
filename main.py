import uasyncio
import json
import sys
import temperature
from machine import Pin, PWM
from time import sleep
from connection import Connection
from credentials import SSID, PASSWORD
from display import Display
from config import START, RETURN, END, STATUS_SHUTTING_DOWN, STATUS_READY, STATUS_TURNING, STATUS_WARMING, STATUS_BOOTING, GP_SERVO

GP_SERVO=Pin(28)


class Main:

    def __init__(self) -> None:
        self.pwm = PWM(Pin(GP_SERVO))
        self.pwm.freq(50)
        self.pwm.duty_ns(START)

        self.internal_temp = 0
        self.temp = 0

        self.status = STATUS_BOOTING
        self.display = Display()
        self.ip = None
        self.html, self.css = self.load_files()
        if not Connection(SSID, PASSWORD, self.display).connect_wlan():
            return
        

    async def run(self):
        server = uasyncio.start_server(self.handle_request, '0.0.0.0', 80)
        uasyncio.create_task(server)
        uasyncio.create_task(self.check_temperature())
        self.status = STATUS_READY
        self.display.write_line("Ready", 1, True)
        self.display.write_line(str(self.ip), 2)
        while True:
            await uasyncio.sleep(0)
            

    async def check_temperature(self):
        while True:
            try:
                # Temperature is always really high, why?
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

    async def sauna_on(self):
        if self.status not in [STATUS_READY, STATUS_WARMING]: return
        self.status = STATUS_TURNING
        try:
            self.display.write_line("Turning servo", 1, True)
            self.pwm.duty_ns(END)
            await uasyncio.sleep_ms(3000)
            self.pwm.duty_ns(RETURN)
            self.status = STATUS_WARMING
            self.display.write_line("Warming", 1, True)
        except Exception as e:
            print(e)

    async def handle_get_styles(self, reader, writer, json_body):
        print("GET /styles.css")
        response = 'HTTP/1.0 200 OK\r\nContent-Type: text/css\r\n\r\n' + self.css
        writer.write(response.encode('utf-8'))
        await writer.drain()
        await writer.wait_closed()

    async def handle_get_status(self, reader, writer, json_body):
        print("GET /status")
        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        data = {
            "internal_temperature": temperature.read_temp(),
            "status": self.status
        }
        json_data = json.dumps(data)
        response += json_data.encode('utf-8')
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()
    
    async def handle_get_page(self, reader, writer, json_body):
        print("GET /")
        response = 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n' + self.html
        writer.write(response.encode('utf-8'))
        await writer.drain()
        await writer.wait_closed()

    async def handle_post_shutdown(self, reader, writer, json_body):
        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        data = {
            "status": "shutting down"
            }
        json_data = json.dumps(data)
        response += json_data.encode('utf-8')
        uasyncio.create_task(self.shutdown())
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()

    async def handle_api_turn(self, reader, writer, json_body):
        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        # data = {
        #     "status": "turning"
        #     }
        # json_data = json.dumps(data)
        # response += json_data.encode('utf-8')
        uasyncio.create_task(self.sauna_on())
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()



    async def handle_request(self, reader, writer):

        ROUTES = {
            ("GET", "/styles.css"): self.handle_get_styles,
            ("GET", "/api/status"): self.handle_get_status,
            ("GET", "/"): self.handle_get_page,
            ("POST", "/api/shutdown"): self.handle_post_shutdown,
            ("POST", "/api/turn"): self.handle_api_turn,
        }

        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        try:
            raw_request = await reader.read(2048)
            request_line = raw_request.split(b'\r\n')[0]
            method, path, _ = request_line.decode().split()
            headers_end = raw_request.find(b'\r\n\r\n')
            body = raw_request[headers_end + 4:] if headers_end != -1 else b''

            json_body = None
            if method == "POST" and body:
                try:
                    json_body = json.loads(body.decode('utf-8'))
                except Exception as e:
                    print("Invalid JSON:", e)
                    response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request'
                    writer.write(response.encode('utf-8'))
                    await writer.drain()
                    await writer.wait_closed()

            handler = ROUTES.get((method, path))
            if handler:
                await handler(reader, writer, json_body)
            else:
                response = 'HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found'
                writer.write(response.encode('utf-8'))
                await writer.drain()
                await writer.wait_closed()

        except Exception as e:
            print(e)
            response = 'HTTP/1.0 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nInternal Server Error'
            writer.write(response.encode('utf-8'))
            await writer.drain()
            await writer.wait_closed()

    async def shutdown(self):
        while self.status == STATUS_TURNING:
            await uasyncio.sleep(0)
        self.status = STATUS_SHUTTING_DOWN
        self.display.write_line("Shutting down",5)
        sleep(6)
        self.display.off()
        sys.exit()

if __name__ == "__main__":
    app = Main()
    try:
        uasyncio.run(app.run())
    except Exception as e:
        print(e)
        app.shutdown()
    finally:
        uasyncio.new_event_loop()