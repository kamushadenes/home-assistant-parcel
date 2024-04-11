from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""

    async def async_track_package(call: ServiceCall):
        """Service to add a new package tracker."""
        api_key = call.data.get("api_key")
        tracking_number = call.data.get("tracking_number")
        session = async_get_clientsession(hass)

        async with session.post(
                "https://api.ship24.com/public/v1/trackers",
                json={"trackingNumber": tracking_number},
                headers={"Authorization": f"Bearer {api_key}"},
        ) as response:
            # This ensures we raise an exception for non-2xx responses
            # You might want to handle different statuses differently
            response.raise_for_status()

            # Optionally handle the response data
            data = await response.json()
            hass.components.persistent_notification.create(
                title="Package Tracking Added",
                message=f"Tracking number {tracking_number} added successfully.",
            )

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "track_package", async_track_package)

    # Return True to indicate that initialization was successfully.
    return True
