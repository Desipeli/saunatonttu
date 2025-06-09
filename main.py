import asyncio
from connection import Connection
from controller import Controller
from credentials import SSID, PASSWORD
from display import Display
from server import Server


async def main():
    display = Display()
    connection = Connection(SSID, PASSWORD, display)
    if not connection.connect_wlan():
        print("Failed to connect to Wi-Fi")
        await asyncio.sleep(5)
        display.off()
        return

    controller = Controller(display)
    server = Server(controller)

    await asyncio.gather(
        server.start(),
        controller.display_temperature(),
        controller.display_times()
    )

    display.write_line("main ended", 6)
    display.off()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("Error:", e)
