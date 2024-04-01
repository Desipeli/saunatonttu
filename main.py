import json
#import microcontroller
import network
import socket
from config import SSID, PASSWORD
from machine import Pin, PWM, ADC
from time import sleep

### temp
adc = ADC(4)
# https://electrocredible.com/raspberry-pi-pico-temperature-sensor-tutorial/

### Network
ssid = SSID
password = PASSWORD

page = open("index.html", "r")
html = page.read()
page.close()

page = open("styles.css", "r")
css = page.read()
page.close()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

sta_if = network.WLAN(network.STA_IF)
host_ip = sta_if.ifconfig()[0]
print(host_ip)
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

### components
print("components")
led = Pin("LED", Pin.OUT)
MID = 1_500_000
MIN = 1_000_000
MAX = 2_000_000
START = 1_200_000
RETURN = 1_100_000
END = 1_900_000

pwm = PWM(Pin(28))
pwm.freq(50)
pwm.duty_ns(START)

state = 0

while True:
    print("STATE", state)
    #print("TEMP", microcontroller.cpu.temperature)
    cl, addr = s.accept()
    req = cl.recv(1024)
    print()
    print(req)
    reqstr = str(req)
    splitted_req = reqstr.split(" ")

    ### POST ###

    if splitted_req[0] == "b'POST":
        body = req.splitlines()
        content = str(body[-1])[2:-1]
        content = json.loads(content)
        if "servo" in content:
            if content["servo"] == "turn":
                state = 1
                print("Käännetään")
                pwm.duty_ns(END)
                print("nukutaan 3")
                sleep(3)
                print("käännetään takaisin")
                pwm.duty_ns(RETURN)
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            elif content["servo"] == "get":
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + str(state))

    ### GET ###
    if splitted_req[0] == "b'GET":

        f_css = reqstr.find("/styles.css")

        if f_css == 6:
            cl.send(css)
        else:
            response = html % ("Kiukaankäynnistin")
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)

    cl.close()
