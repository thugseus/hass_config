import logging

import voluptuous as vol

import time
import sys
import RPi.GPIO as GPIO

# Import the device class from the component that you want to support
from homeassistant.components.light import Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_DEVICES, CONF_NAME
import homeassistant.helpers.config_validation as cv


_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema({vol.Optional(CONF_NAME): cv.string, })

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Optional(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA}, })

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Livolo Light platform."""
    lights = []
    for id, device_config in config[CONF_DEVICES].items():
        device = {'name': device_config[CONF_NAME], 'id': id}
        lights.append(LivoloLight(device))

    add_devices(lights)


class LivoloLight(Light):
    """Representation of an Livolo Light."""

    def __init__(self, light):
        """Initialize an LivoloLight."""
        self._light = light
		self._state = False
		
	off =  '1242424352424342424242424242425342524342'
	on  =  '124242435242434242424242424242425243424242'
	TRANSMIT_PIN = 24#pin from 433Mhz Sender
	
	@property
	def unique_id(self):
		"""Return the ID of this light."""
		return "{}.{}".format(self.__class__, self._light.id)

    @property
    def name(self):
        """Return the display name of this light."""
        return self._light.name

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state()

    def turn_on(self, **kwargs):
		"""Turn the specified or all lights on."""
		#exec('transmit_code(on, 150)
		self.transmit_code(on,150)
		self._state = True
		self.update_ha_state()
		##livolo toggle 

    def turn_off(self, **kwargs):
		"""Turn the specified or all lights off."""
		#exec('transmit_code(off, 1000)
		self.transmit_code(off,1000)
		self._state = False
		self.update_ha_state()
		##livolo toggle 

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._light.update()
		
	def transmit_code(code, num_attempts):
		"""Transmit a chosen code string using the GPIO transmitter"""
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(TRANSMIT_PIN, GPIO.OUT)
		for t in range(num_attempts):
			for i in code:
				if i == '1':
					GPIO.output(TRANSMIT_PIN, 1)
					time.sleep(.00055);
					GPIO.output(TRANSMIT_PIN, 0)
				elif i == '2':
					GPIO.output(TRANSMIT_PIN, 0)
					time.sleep(.00011);
					GPIO.output(TRANSMIT_PIN, 1)
				elif i == '3':
					GPIO.output(TRANSMIT_PIN, 0)
					time.sleep(.000303);
					GPIO.output(TRANSMIT_PIN, 1)
				elif i == '4':
					GPIO.output(TRANSMIT_PIN, 1)
					time.sleep(.00011);
					GPIO.output(TRANSMIT_PIN, 0)
				elif i == '5':
					GPIO.output(TRANSMIT_PIN, 1)
					time.sleep(.00029);
					GPIO.output(TRANSMIT_PIN, 0)
				else:
					continue
			GPIO.output(TRANSMIT_PIN, 0)
		GPIO.cleanup()