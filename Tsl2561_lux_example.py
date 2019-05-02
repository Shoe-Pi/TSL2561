#! /usr/bin/python3
import tsl2561
import time

#Create a sensor object
tsl = tsl2561.TSL2561()

#Reset the device
tsl.turn_on(False)
tsl.turn_on(True)

#Set to x16 gain with a 402 ms integration cycle
tsl.set_gain("high")
tsl.set_integration_cycle(2)

try:
    while True:
        print("Lux = "  + str(tsl.lux()))
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting.")
