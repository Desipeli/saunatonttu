from machine import Pin

MID = 1_500_000
MIN = 1_000_000
MAX = 2_000_000
START = MID
RETURN = MID + 50_000
END = 1_900_000

STATUS_BOOTING = 0
STATUS_SHUTTING_DOWN = -1
STATUS_READY = 1
STATUS_TURNING = 2
STATUS_WARMING = 3

GP_SERVO = Pin(28)

# Display pins for oled should not be changed
# scl = Pin(17)
# sda = Pin(16)
