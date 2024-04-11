import aiohttp
import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, \
    CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Ship24 sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [Ship24Sensor(coordinator, tracker_id) for tracker_id in coordinator.data.keys()]
    async_add_entities(sensors, update_before_add=True)


class Ship24UpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ship24 tracking data."""

    def __init__(self, hass, api_key):
        """Initialize."""
        self.api_key = api_key
        self.session = aiohttp.ClientSession()
        super().__init__(
            hass,
            _LOGGER,
            name="ship24_tracker",
            update_interval=timedelta(minutes=15),  # Adjust the interval as needed
        )

    async def _async_update_data(self):
        """Fetch data from Ship24."""
        trackers_url = "https://api.ship24.com/public/v1/trackers"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with self.session.get(trackers_url, headers=headers) as response:
            if response.status != 200:
                raise UpdateFailed("Error fetching trackers")
            trackers = await response.json()

        # Fetch tracking results for each tracker
        tracking_data = {}
        for tracker in trackers.get('data', []):
            tracker_id = tracker['trackerId']
            tracking_url = f"https://api.ship24.com/public/v1/trackers/{tracker_id}"

            async with self.session.get(tracking_url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error(f"Error fetching tracking data for {tracker_id}")
                    continue
                tracking_result = await response.json()
                tracking_data[tracker_id] = tracking_result

        return tracking_data


class Ship24Sensor(CoordinatorEntity, Entity):
    """Representation of a Ship24 package sensor."""

    def __init__(self, coordinator, tracker_id):
        super().__init__(coordinator)
        self.tracker_id = tracker_id
        self.attrs = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Package {self.tracker_id}"

    @property
    def state(self):
        """Return the state of the sensor."""
        tracking_data = self.coordinator.data.get(self.tracker_id, {})
        # You might want to adjust what property you use as the state
        return tracking_data.get('status', 'unknown')

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        # Return all tracking data or select specific fields
        return self.coordinator.data.get(self.tracker_id, {})
