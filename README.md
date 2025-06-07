# Saunatonttu

Raspberry pico W project for controlling sauna stove remotely.

# Components

- Raspberry pico W ([datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf))
- 4 Ni-MH AA 1.2 V batteries connected in series with case.
- FEETECH Standard Servo FS5106B
- Terminal blocks (3 and 5)
- Jumper wires
    - 3 female to female
    - 4 x male to female
    - 2 x male to male

# Connections

- VSYS: Power supply ~5V
- GP16: OLED SDA
- GP17: OLED SCL
- GP28: Servo control signal
- All components and Pico W share a common ground
- Do NOT power components from the Pico’s 3.3V or 5V pins!


# Setup with vscode

1. Download project
3. Download and flash [micropython](https://micropython.org/download/RPI_PICO_W/) for Pico W 
4. Create `credentials.py` to root of the project
    - `SSID=<"WIFI_NAME">`
    - `PASSWORD=<"WIFI_PASSWORD">`
6. In vscode
    - install [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension
    - ctrl-shift P
    - search and run MicroPico: Initialize MicroPico Project
    - To test, press Run in the bottom of the vscode window
    - To upload the project, ctrl-shift P and run MicroPico: Upload project to Pico

# How to use

1. Navigate to ip address of the Pico with any web browser. Click the button to turn the servo.

# How to boot pico w if bootsel is broken

connect TP6 surface to ground