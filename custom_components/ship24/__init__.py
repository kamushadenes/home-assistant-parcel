from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .sensor import Ship24UpdateCoordinator
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # This method should remain fairly minimal, as it sets up the component,
    # and optionally sets up any platforms.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ship24 as a config entry."""
    # Initialize your integration's core here, for example, setting up an update coordinator.
    coordinator = Ship24UpdateCoordinator(hass, entry.data['api_key'])
    await coordinator.async_refresh()

    # Store a reference to the coordinator in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the entry setup to the sensor platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # If your component provides a service, set it up here:
    async def async_track_package(call):
        """Service to add a new package tracker."""
        api_key = entry.data.get("api_key")
        tracking_number = call.data.get("tracking_number")
        session = async_get_clientsession(hass)

        async with session.post(
                "https://api.ship24.com/public/v1/trackers",
                json={"trackingNumber": tracking_number},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json; charset=utf-8",
                },
        ) as response:
            if response.status == 400:
                obj = await response.json()
                _LOGGER.error(obj)
                raise ValueError(obj['errors'][0]['message'])

    # Register your service with Home Assistant.
    hass.services.async_register(DOMAIN, "track_package", async_track_package)

    # Return True to indicate that the entry was successfully set up.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This method should remove all entities and resources set up during async_setup_entry.
    # Typically involves unloading or detaching any platforms.
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    # Unregister services, release resources, etc.
    # For example:
    hass.services.async_remove(DOMAIN, "track_package")
    return True
