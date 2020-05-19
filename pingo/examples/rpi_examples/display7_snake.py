import pingo
from time import sleep
rpi = pingo.rpi.RaspberryPi()
led_sequence = [13, 11, 7, 15, 26, 24, 21, 15]
pins = [rpi.pins[loc] for loc in led_sequence]
for pin in pins:
	pin.mode = pingo.OUT
	pin.low()
prev_pin = pins[-1]
while True:
	for pin in pins:
		pin.high()
		sleep(0.11)
		prev_pin.low()
		prev_pin = pin