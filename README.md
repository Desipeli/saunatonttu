Raspberry pico W project for controlling sauna stove remotely. Put the controller behind a proxy server if used from outside of the local network!

# Components

- Raspberry pico W ([datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf))
- 4 Ni-MH AA 1.2 V batteries with case.
- FEETECH Standard Servo FS5106B
- Terminal blocks (3 and 5)
- USB cable 2.0 Type-A male to 2 x open wires
- Jumper wires
    - 4 x male to female
    - 3 x male to male

# Diagram

# Setup with vscode

1. Download project
3. Download and flash [micropython](https://micropython.org/download/RPI_PICO_W/) for Pico W 
4. Create `config.py` to root of the project
    - `SSID=<"WIFI_NAME">`
    - `PASSWORD=<"WIFI_PASSWORD">`
6. In vscode
    - install [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension
    - ctrl-shift P
    - search and run MicroPico: Configure project
    - To test, press Run in the bottom of the vscode window
    - To upload the project, ctrl-shift P and run MicroPico: Upload project to Pico

# How to use

1. Navigate to ip address of the Pico with any web browser. Click the button to turn the servo.
