#!/usr/bin/python3

import os, fcntl, time

class TSL2561:
    def __init__(self):
        #Set the i2c address
        self.address = 0x39
        self.slave = 0x0703

        #Create an i2c object for read/writing to and from the bus
        self.fd = os.open("/dev/i2c-1", os.O_RDWR)
        fcntl.ioctl(self.fd, self.slave, self.address)

        self.command = 0b10000000

        #Register list
        self.control_reg = 0x00
        self.timing_reg = 0x01
        self.threshlowlow_reg = 0x02
        self.threshlowhigh_reg = 0x03
        self.threshhighlow_reg = 0x04
        self.threshhighhigh_reg = 0x05
        self.interrupt_reg = 0x06

        self.id_reg = 0x0A

        self.data0low_reg = 0x0C
        self.data0high_reg = 0x0D
        self.data1low = 0x0E
        self.data1high = 0x0F

        #Values for scaling raw data to lux values
        self.gain_values = (16, 1)
        self.integration_times = (1/0.034, 1/0.252, 1)


    """
    Function to read *numbytes* bytes from the device starting at
    register *register*.
    """
    def read_reg(self, register, numbytes):
        os.write(self.fd, bytearray([self.command | register]))
        self.data = bytearray(os.read(self.fd, numbytes))
        return self.data

    """
    Function to set the shutdown state of the device.  *mode* must be a boolean.
    """
    def turn_on(self, state):
        #If state == True, turn the device on /write 0x03
        if state == True:
            os.write(self.fd, \
bytearray([self.command | self.control_reg, 0x03]))
        #If state == False, turn the device off /write 0x00
        elif state == False:
            os.write(self.fd, \
bytearray([self.command | self.control_reg, 0x00]))
        else:
            print("Error! turn_on must be given a boolean value.")

    """
    Function to set the gain of the device.  Must be given a value of 0x00
    or 0x01. 0x00 gives low (x1) gain, 0x01 gives high (x16) gain.
    """
    #0x01
    def set_gain(self, gain):
        if (gain == "high") or (gain == "low"):
            self.current_value = self.read_reg(self.timing_reg, 1)[0]
            self.new_value = self.current_value & 0b00001011
            if gain == "high":
                self.new_value = self.new_value | 0x10
            os.write(self.fd, bytearray([self.command | self.timing_reg, \
self.new_value]))
        else:
            print("Error, set_gain must be given 'high' or 'low'.")


    """
    Manually set the integration process.  Writing True starts an integration
    cycle, writing False stops an integration cycle.  NOTE: the \
    integration_cycle must be set to manual for this to do anything.
    """
    def manual_integration(self, mode):
        self.current_value = self.read_reg(self.timing_reg, 1)[0]
        self.new_value = self.current_value & 0b00010111
        if (mode == True):
            self.new_value = self.new_value & 0x08
        os.write(self.fd, bytearray([self.command | self.timing_reg, \
self.new_value]))

    """
    Set the integration time.  Must be given a value from 0 to 3.
    0 =  13.7 ms
    1 = 101   ms
    2 = 402   ms
    3 = manual
    """
    def set_integration_cycle(self, integration_time):
        if (integration_time >= 0) and (integration_time <= 3):
            self.current_value = self.read_reg(self.timing_reg, 1)[0]
            self.new_value = self.current_value & 0b00011000
            self.new_value = self.new_value | integration_time
            os.write(self.fd, bytearray([0b10000001, self.new_value]))
        else:
            print("Error, integration_time must be an int of 0-3.")

    """
    Set the upper and lower thresholds for the interrupt.  must be given an
    integer between 0 and 65535.
    """
    def set_threshold_low(self, threshold):
        if isinstance(threshold, int) and (threshold >= 0) and \
(threshold <= 0xffff):
            self.msb = threshold >> 8
            self.lsb = threshold & 0xff
            os.write(self.fd, bytearray([self.command | self.threshlowlow_reg,\
self.lsb]))
            os.write(self.fd, bytearray([self.command | self.threshlowhigh_reg, \
self.msb]))
        else:
            print("Error, threshold value must be from 0 to 65535.")

    def set_threshold_high(self, threshold):
        if (threshold >= 0) and (threshold <= 0xffff)\
and isinstance(threshold, int):
            self.msb = threshold >> 8
            self.lsb = threshold & 0xff
            os.write(self.fd, bytearray([self.command | self.threshhighlow_reg,\
self.lsb]))
            os.write(self.fd, bytearray([self.command | self.threshhighhigh_reg,\
self.msb]))
        else:
            print("Error, threshold value must be from 0 to 65536.")

    """
    Function to set how long the ambiend light must exceed the set limits
    before an interrupt is raised.  Must be given an integer of 0-15.
    0 generates an interrupt every cycle
    1-15 generates an interrupt if the value exceeds the threshold for that 
    many cycles.
    """
    def interrupt_persist(self, time):
        if isinstance(time, int) and (time >= 0) and (time <= 15):
            self.current_value = self.read_reg(self.interrupt_reg, 1)[0]
            self.new_value = self.current_value & 0b00110000
            self.new_value = self.new_value | time
            os.write(self.fd, bytearray([self.command | self.interrupt_reg,\
 self.new_value]))
        else:
            print("Error, time must be an int from 0-15.")


    """
    Function to set the interrupt mode of the device.  Must be given an
    integer of 0-3.
    0 = interrupt disabled
    1 = level interrupt (pin high/low)
    2 = SMBAlert (not supported in this library)
    3 = Test mode: sets the interrupts and sets SMBAlert mode.
    """
    def interrupt_mode(self, mode):
        if isinstance(mode, int) and (mode >= 0) and (mode <= 3): 
            self.current_value = self.read_reg(self.interrupt_reg, 1)[0]
            self.new_value = self.current_value & 0b00001111
            self.new_value = self.new_value | (mode << 4)
            os.write(self.fd, bytearray([self.command | self.interrupt_reg, \
self.new_value]))
        else:
            print("Error, interrupt mode must be an integer of 0-3.")
    #0x0A
    def chipid(self):
        os.write(self.fd, bytearray([0b10001010]))
        self.data = bytearray(os.read(self.fd, 1))
        return self.data[0] >> 4

    #0x0C-0x0F
    def read_data(self):
        data = self.read_reg(0x0C, 4)
        self.channel0 = (data[1] << 8) + data[0]
        self.channel1 = (data[3] << 8) + data[2]
        return self.channel0, self.channel1

    #Lux calculator based on an FN package
    def lux(self):
        self.ch0, self.ch1 = self.read_data()
        if self.ch0 == 0:
            return 0
        self.ratio = self.ch1/self.ch0
        if (0 < self.ratio) and (self.ratio <= 0.50):
            self.luxval = 0.0304 * self.ch0 - 0.062 * self.ch0 * self.ratio**1.4
        elif (self.ratio <= 0.61):
            self.luxval =  0.0224 * self.ch0 - 0.031 * self.ch1
        elif (self.ratio <= 0.80):
            self.luxval =  0.0128 * self.ch0 - 0.0153 * self.ch1
        elif (self.ratio <= 1.30):
            self.luxval =  0.00146 * self.ch0 - 0.00112 * self.ch1
        else:
            return(0)

        self.timing_state = self.read_reg(self.timing_reg, 1)[0]
        self.gainval = self.gain_values[self.timing_state >> 4 & 0x01]
        self.integration_time = self.integration_times[self.timing_state & 0x03]

        return self.luxval * self.gainval * self.integration_time

    def clear_interrupt(self):
        os.write(self.fd, bytearray([self.command | 0b11000000]))

if __name__ == "__main__":
    tsl = TSL2561()
    #Reset the device
    tsl.turn_on(True)

    #time.sleep(0.15)
    chan0, chan1 = tsl.read_data()
    tsl.set_integration_cycle(0x02)

    tsl.set_threshold_low(0)
    tsl.set_threshold_high(65535)

    tsl.clear_interrupt()

    while True:
        time.sleep(0.41)
        print("Lux = " + str(tsl.lux()) + "\n")
