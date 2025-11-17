"""Config flow for ekopiec integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import CONF_PORT, DEFAULT_PORT, DOMAIN
from .api import ECoalApiClient, AuthenticationError


class EkopiecConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ekopiec."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate by attempting connection
                session = async_get_clientsession(self.hass)
                api = ECoalApiClient(
                    host=user_input[CONF_HOST],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    port=user_input.get(CONF_PORT, DEFAULT_PORT),
                    session=session,
                )
                
                device_info = await api.authenticate()
                
                # Set unique_id and check if already configured
                await self.async_set_unique_id(device_info["device_sn"])
                self._abort_if_unique_id_configured()
                
                # Create entry
                return self.async_create_entry(
                    title=device_info.get("device_name", "ekopiec"),
                    data=user_input,
                )
                
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
        
        # Show form
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
    

