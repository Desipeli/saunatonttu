import asyncio
import json
from controller import Controller
import temperature

class Server:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.html, self.css = self.load_files()

    def load_files(self):
        with open("index.html", "r") as f:
            html = f.read()
        with open("styles.css", "r") as f:
            css = f.read()
        return html, css

    async def handle_request(self, reader, writer):
        ROUTES = {
            ("GET", "/styles.css"): self.handle_get_styles,
            ("GET", "/api/status"): self.handle_get_status,
            ("GET", "/"): self.handle_get_page,
            ("POST", "/api/shutdown"): self.handle_post_shutdown,
            ("POST", "/api/turn"): self.handle_api_turn,
        }

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
                    return

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

    async def handle_get_styles(self, reader, writer, json_body):
        response = 'HTTP/1.0 200 OK\r\nContent-Type: text/css\r\n\r\n' + self.css
        writer.write(response.encode('utf-8'))
        await writer.drain()
        await writer.wait_closed()

    async def handle_get_status(self, reader, writer, json_body):
        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        data = {
            "internal_temperature": temperature.read_temp(),
            "status": self.controller.status
        }
        json_data = json.dumps(data)
        response += json_data.encode('utf-8')
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()

    async def handle_get_page(self, reader, writer, json_body):
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
        asyncio.create_task(self.controller.shutdown())
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()

    async def handle_api_turn(self, reader, writer, json_body):
        response = b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n'
        asyncio.create_task(self.controller.sauna_on())
        writer.write(response)
        await writer.drain()
        await writer.wait_closed()

    async def start(self):
        server = asyncio.start_server(self.handle_request, '0.0.0.0', 80)
        asyncio.create_task(server) # serve_forever did not work for some reason.

        while True:
            await asyncio.sleep(0)
