import sys
import asyncio
import temperature
from time import sleep, ticks_ms, ticks_diff  # type: ignore
from machine import Pin, PWM
from config import START, RETURN, END, STATUS_SHUTTING_DOWN, STATUS_READY, STATUS_TURNING, STATUS_WARMING, STATUS_BOOTING, GP_SERVO
from display import Display


class Controller:
    def __init__(self, display: Display):
        self.__status = STATUS_BOOTING
        self.__pwm = PWM(Pin(GP_SERVO))
        self.__pwm.freq(50)
        self.__pwm.duty_ns(START)

        self.__internal_temp = 0
        self.__display = display
        self.__uptime = ticks_ms()
        self.__first_activation_time = None
        self.__latest_activation_time = None

        sleep(2)  # wait for servo to settle
        self.__status = STATUS_READY

    async def sauna_on(self):
        if self.__status not in [STATUS_READY, STATUS_WARMING]:
            return
        self.__status = STATUS_TURNING
        try:
            if not self.__first_activation_time:
                self.__first_activation_time = ticks_ms()
            self.__latest_activation_time = ticks_ms()
            self.__display.write_line("Turning servo", 1)
            self.__pwm.duty_ns(END)
            await asyncio.sleep(3)
            self.__pwm.duty_ns(RETURN)
            self.__status = STATUS_WARMING
            self.__display.write_line("Warming", 1)
        except Exception as e:
            print(e)

    async def check_temperature(self):
        while True:
            try:
                self.__internal_temp = temperature.read_temp()
                self.__display.set_header(f"{self.__internal_temp} C")
                print(self.__internal_temp)
            except Exception as e:
                print("Temp error", e)
            await asyncio.sleep(10)

    async def display_times(self):
        while True:
            hours_mins_uptime = self.__calculate_display_time(
                ticks_diff(ticks_ms(), self.__uptime))
            hours_mins_from_first_activation = ""
            if self.__first_activation_time:
                hours_mins_from_first_activation = self.__calculate_display_time(
                    ticks_diff(ticks_ms(), self.__first_activation_time))
            self.__display.set_footer(
                f"{hours_mins_uptime}      {hours_mins_from_first_activation}")
            await asyncio.sleep(60)

    async def shutdown(self):
        while self.__status == STATUS_TURNING:
            await asyncio.sleep(0)
        self.__status = STATUS_SHUTTING_DOWN
        self.__display.write_line("Shutting down", 5)
        sleep(6)
        self.__display.off()
        sys.exit()

    def __calculate_display_time(self, milliseconds: int, include_seconds: bool = False) -> str:
        seconds = milliseconds // 1000
        minutes = (seconds % 3600) // 60
        hours = seconds // 3600

        # no room for seconds in the display :(
        formatted_string = f"{hours:02d}:{minutes:02d}"
        if include_seconds:
            seconds = seconds % 60
            formatted_string = f"{formatted_string}:{seconds:02d}"
        return formatted_string

    def get_status(self) -> int:
        return self.__status

    def get_uptime(self) -> str:
        diff = ticks_diff(ticks_ms(), self.__uptime)
        return self.__calculate_display_time(diff, True)

    def get_time_from_first_activation(self) -> str:
        if not self.__first_activation_time:
            return "not activated"
        diff = ticks_diff(ticks_ms(), self.__first_activation_time)
        return self.__calculate_display_time(diff, True)

    def get_time_from_latest_activation(self) -> str:
        if not self.__latest_activation_time:
            return "not activated"
        diff = ticks_diff(ticks_ms(), self.__latest_activation_time)
        return self.__calculate_display_time(diff, True)
