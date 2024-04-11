from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


async def async_setup(hass: HomeAssistant, config: dict):
    hass.services.async_register(DOMAIN, "track_package", async_track_package)


async def async_track_package(call):
    """Service to add a new package tracker."""
    api_key = call.data.get("api_key")
    tracking_number = call.data.get("tracking_number")
    session = async_get_clientsession(hass)
    async with session.post(
            "https://api.ship24.com/public/v1/trackers",
            json={"trackingNumber": tracking_number},
            headers={"Authorization": f"Bearer {api_key}"},
    ) as response:
        response.raise_for_status()
        # Handle response
