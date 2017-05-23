"""
Support for showing text in the frontend.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/hello_state/
"""
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'hello_state'
DEPENDENCIES = []

CONF_TEXT = 'text'
DEFAULT_TEXT = 'No text!'

def setup(hass, config=None):
    """Setup the Hello State component. """
    _LOGGER.info("The 'hello state' component is ready!")
    # Get the text from the configuration. Use DEFAULT_TEXT if no name is provided.
    text = config[DOMAIN].get(CONF_TEXT, DEFAULT_TEXT)

    # States are in the format DOMAIN.OBJECT_ID
    hass.states.set('hello_state.Hello_State', text)

    return True