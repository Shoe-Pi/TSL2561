# TSL2561

A library for running Adafruit's TSL2561 Lux sensor board on the Raspberry Pi.

This is a neat little light sensor which measures the light hitting the sensor, and the values it provides can be converted into a lux value, a standard measurement of light.  

The TSL2561 actually has two light sensors:  channel 0 detects both visible and infra-red light, and channel 1 detects only infra-red light.  From these you can calculate the visible light in lux.  There's also an interrupt pin which will go low whenever the value on channel 0 goes below or above thresholds which the user can set.  This allows you to trigger a pin on the Pi to react to the light exceeding the user-set threshold.

# Using the library

Begin by importing the TSL2561 library and create an instance of the device.  The new sensor object needs to be given an i2c address: if you didn't hook the address pin on the board up to anything this should be `0x39`.

```
import tsl2561
tsl = tsl2561.TSL2561(0x39)
```

Then turn the device on:
```
tsl.turn_on(True)
```

Finally, print the amount of light in Lux:
```
print(tsl.lux())
```

# The interrupt pin

One of the pins on the board is labelled `Int`, and this is the interrupt pin.  This pin is usually held high but will drop low under certain circumstances which the user can control.  It will then stay low until the user resets it.

The `high` threshold which the light must rise above before the interrupt is triggered is set by `set_threshold_high(value)`, and the value which the light must drop below before the interrupt is triggered is set by `set_threshold_low(value)`.  The amount of time which these limits must be exceeded for before the interrupt is asserted is set by `interrupt_persist(time)`, measured in the number of integration cycles which must pass.  See the `integration_cycle()` function to see how long the integration cycle lasts.

**It's important to remember that the threshold values are compared to the value coming out of channel 0, _not_ the Lux values**.  Channel 0  is usually a little lower than the Lux value, so you may need to use the first value returned by `data_read()` to tweak this.

When triggered the interrupt pin goes low.  To measure this you can either use it as the ground pin for an LED (so the LED goes high when the interrupt is triggered) or you can connect it to one of the Pi's GPIO pins set up as an input with a pull up resistor set, so that the pin will read low when the interrupt is triggered.

# Function reference

* **turn_on(state)**

This function sets the shutdown register.  Must be passed a boolean: `True` turns the device on, `False` turns the device off.

* **lux()**

Returns a float which describes the quantity of visible light in Lux.

* **read_data()**

This returns a list of two values.  The first is the amount of light detected by channel 0, the second is the amount of light detected by channel 1.  These can be used to calculate the amount of light in the visible spectrum using a formula in the datasheet, but the `lux()` function will do this for you automatically.

* **set_gain(gain)**

The device can run with different gain levels, essentially multiplying the readings to pick up lower levels of light.  This must be given a string of either `high` (16x gain) or `low` (1x gain).

* **integration_cycle(integration_time)**

This sets the integration cycle, the amount of time which the device measures light over before returning a result.  Must be given an integer from 0-3, inclusive.
  
  0 =  13.7 milliseconds
  
  1 = 101 milliseconds
  
  2 = 402 milliseconds
  
  3 - manual

A value of `3` - manual - requires you to start and stop integration periods using the `manual_integration` function.

* **manual_integration(mode)**

This function is only useful when the `integration_cycle` is set to manual (mode `3`).  Must be given a boolean for `mode`: a value of `True` starts an integration cycle, `False` stops one.

* **interrupt_mode(mode)**

The TSL2561 has an interrupt pin, normally held high, which will go low when certain conditions are met.  This function controls how the interrupt process works.

  0 = Interrupts disabled.
  
  1 = Level interrupt (uses the pin on the board).
  
  2 = SMBAlert.  This is not supported in this library.
  
  3 = Test mode: sets the interrupt pin and also the SMBAlert.
 
 * **interrupt_persist(time)**
 
 You can control how long it takes to activate the interrupt using this register.  `time` must be an integer from 0-15 inclusive.  `0` means that the interrupt is asserted after every integration cycle.  Values of 1-15 mean that the interrupt won't be asserted until the light level exceeds the thresholds for that many integration cycles.  E.g. for an `integration_cycle` of `2` (402 milliseconds) a value of `5` will mean the light levels have to exceed the thresholds for 5 x 402 = 2010 milliseconds (just over 2 seconds) before the interrupt is asserted.
 
 * **set_threshold_high(threshold)**
 
This is the value which the channel 0 reading must exceed before the interrupt is asserted.  Must be given an integer of 0-65535.
 
 * **set_threshold_low(threshold)**
 
This is the value which the channel 0 reading must drop below before the interrupt is asserted.  Must be given an integer of 0-65535.

* **clear_interrupt()**

This resets the interrupt, and will return the interrupt pin to high.

