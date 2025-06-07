import machine
import _thread

temp_lock = _thread.allocate_lock()
sensor_temp = machine.ADC(4)


def read_temp():
    temp_lock.acquire()
    try:
        conversion_factor = 3.23 / (65535)
        reading = sensor_temp.read_u16() * conversion_factor
        temperature = 27 - (reading - 0.706)/0.001721
        formatted_temperature = "{:.1f}".format(temperature)
        string_temperature = str(formatted_temperature)
        return string_temperature
    finally:
        temp_lock.release()
