import logging
import os

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ATTR_TRANSITION, 
    ATTR_FLASH, FLASH_SHORT, FLASH_LONG,
    SUPPORT_BRIGHTNESS, SUPPORT_RGB_COLOR, SUPPORT_TRANSITION,
    SUPPORT_FLASH,
    Light, PLATFORM_SCHEMA)
from homeassistant.const import  CONF_DEVICES, CONF_NAME,CONF_MAC
import homeassistant.helpers.config_validation as cv

# Home Assistant depends on 3rd party packages for API specific code.

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
DEVICE_SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_MAC): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Optional(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA}, })
	
SUPPORT_MIPOW = (SUPPORT_RGB_COLOR)
	
#_LOGGER.error(CONF_DEVICES)

def setup_platform(hass, config, add_devices, discovery_info=None):

    lights = []
    for id, device_config in config[CONF_DEVICES].items():
        device = {'name': device_config[CONF_NAME], 'id': id, 'mac':device_config[CONF_MAC] }		
        lights.append(MipowLight(device))
    add_devices(lights)
	#_LOGGER.error("Test2")


class MipowLight(Light):
    """Representation of an Mipow Light."""

    def __init__(self, light):
        """Initialize an MipowLight."""
        self._light = light
        self._name = light['name']		
        self._mac = light['mac']
        self._supported_features = SUPPORT_MIPOW
	
    @property
    def available(self) -> bool:
        """Return if bulb is available."""
        message = "gatttool -b " + self._mac + " --char-read -a 0x001b"    
        _LOGGER.debug("available")
        retMsg = self.timeout_command(message,1)
        if retMsg:
            if "Device or resource busy" in retMsg:
                _LOGGER.debug("available  False")
                return False
            else:
                _LOGGER.debug("available True")
                return True
        _LOGGER.debug("available False")
        return False
	
    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Brightness of the light (an integer in the range 1-255).

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        _LOGGER.debug("brightness")
        return None
        return self._brightness
	
    @property
    def rgb_color(self) -> tuple:
        """Return the color property array."""
        message = "gatttool -b " + self._mac + " --char-read -a 0x001b"
        _LOGGER.debug("rgb_color")
        retMsg = self.timeout_command(message,1)
        if retMsg:
            hexString = retMsg.partition("Characteristic value/descriptor: ")[2]
            if hexString:
                _LOGGER.debug("hexstring")
                _LOGGER.debug(hexString)
                hexString = hexString.replace(" ", "").replace('\n','').replace('\t','')
                _LOGGER.debug("stripped hexstring")
                _LOGGER.debug(hexString)
                _LOGGER.debug(hexString[2:])
                rgb = self.hex_to_rgb(hexString[2:])
                _LOGGER.debug(rgb)
                return rgb

    @property
    def is_on(self):
        """Return true if light is on."""
        message = "gatttool -b " + self._mac + " --char-read -a 0x001b"
        _LOGGER.debug("is_on")
        retMsg = self.timeout_command(message,1)
        if retMsg:
            if "00 00 00 00" in retMsg:
                _LOGGER.debug("False")
                return False
            else:
                _LOGGER.debug("True")
                return True
        return False
		
    def set_brightness(self, brightness, duration) -> None:
        """Set bulb brightness."""
        if brightness:
            _LOGGER.debug("Setting brightness: %s", brightness)

    def set_rgb(self, rgb, duration) -> None:
        """Set bulb's color."""
        if rgb and self.supported_features & SUPPORT_RGB_COLOR:
            _LOGGER.debug("Setting RGB: %s", rgb)
        return True

    def set_default(self) -> None:
        """Set current options as default."""
        _LOGGER.debug("Setting default")
        #self._bulb.set_default()

    def set_flash(self, flash) -> None:
        """Activate flash."""
        _LOGGER.debug("Setting flash")

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)
        flash = kwargs.get(ATTR_FLASH)
        hexRGB = "FFFFFFFF"
        if rgb != None:
            hexRGB = self.rgb_to_hex(rgb)
        _LOGGER.debug("turn_on")
        _LOGGER.debug("Brightness %s",brightness)
        _LOGGER.debug("RGB %s",rgb)
        _LOGGER.debug("HexRGB %s",hexRGB)
        _LOGGER.debug("Flash %s",flash)
		        
        message = "gatttool -b " + self._mac + " --char-write -a 0x001b -n "#FFFFFFFF"
        message = message + hexRGB
        self.timeout_command(message,1)
    
    def rgb_to_hex(self, rgb):
        """Return color as #rrggbb for the given color values."""
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        return '%s%02x%02x%02x' % ("00",red, green, blue)
        
    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
        
    def timeout_command(self, command, timeout):
        """call shell-command and either return its output or kill it
        if it doesn't normally exit within timeout seconds and return None"""
        import subprocess, datetime, os, time, signal
        start = datetime.datetime.now()
        process = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _LOGGER.debug("timeout_command")
        _LOGGER.debug(command)
        while process.poll() is None:
            time.sleep(0.1)
            now = datetime.datetime.now()
            seconds = (now - start).seconds
            #_LOGGER.debug('took %02x' % (seconds))
            if seconds > timeout:
                os.kill(process.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                _LOGGER.debug("killed")
                return None
        retVal = process.stdout.read()
        _LOGGER.debug(retVal)
        return retVal.decode("utf-8")


    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""		
        message = "gatttool -b " + self._mac + " --char-write -a 0x001b -n 00000000" 
        self.timeout_command(message,1)

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug("update")