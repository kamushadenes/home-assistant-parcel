import json
import aiohttp
import logging
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, \
    CoordinatorEntity

from .const import DOMAIN, statusCodes

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Ship24 sensors based on a config entry."""
    _LOGGER.warn("Setting up sensors")

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Check if coordinator.data is None or if it doesn't have the expected structure
    if coordinator.data is None or not isinstance(coordinator.data, dict):
        _LOGGER.error("Data not loaded properly or unexpected data structure.")
        return  # Exit setup if data isn't ready

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
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        """Fetch data from Ship24."""
        _LOGGER.warn("Fetching trackers")

        trackers_url = "https://api.ship24.com/public/v1/trackers"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }

        async with self.session.get(trackers_url, headers=headers) as response:
            if response.status != 200:
                raise UpdateFailed("Error fetching trackers")
            trackers = await response.json()

        # Fetch tracking results for each tracker
        tracking_data = {}
        for tracker in trackers.get('data', {}).get('trackers', []):
            _LOGGER.warn(f"Fetching tracking data for {tracker['trackerId']}")
            tracker_id = tracker['trackerId']
            tracking_url = f"https://api.ship24.com/public/v1/trackers/{tracker_id}/results"

            async with self.session.get(tracking_url, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.error(f"Error fetching tracking data for {tracker_id}")
                    continue
                tracking_result = await response.json()
                tracking_data[tracker_id] = tracking_result.get('data', {}).get('trackings', [{}])[0]
                _LOGGER.warn(json.dumps(tracking_data[tracker_id]))

        return tracking_data


class Ship24Sensor(CoordinatorEntity, Entity):
    """Representation of a Ship24 package sensor."""

    def __init__(self, coordinator, tracker_id):
        _LOGGER.warn(f"Creating sensor for {tracker_id}")
        super().__init__(coordinator)
        self.tracker_id = tracker_id
        self.attrs = {}
        self.coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        _LOGGER.warn(f"Getting name for {self.tracker_id}")
        obj = self.coordinator.data.get(self.tracker_id, {})
        tracking_number = obj.get("tracker", {}).get("trackingNumber", self.tracker_id)
        shipment_reference = obj.get("tracker", {}).get("shipmentReference", "")
        if shipment_reference:
            return f"Package {tracking_number} ({shipment_reference})"
        return f"Package {tracking_number}"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:package"

    @property
    def state(self):
        """Return the state of the sensor."""
        tracking_data = self.coordinator.data.get(self.tracker_id, {})
        # You might want to adjust what property you use as the state
        event = "Unknown"
        last_event = None

        # Get last event based on occurrenceDatetime
        for event in tracking_data.get('events', []):
            # parse
            t = datetime.strptime(event['occurrenceDatetime'], '%Y-%m-%dT%H:%M:%S')
            if last_event is None or t > last_event:
                last_event = t
                event = event['statusCode']

        return statusCodes.get(event, event)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        # Return all tracking data or select specific fields
        obj = self.coordinator.data.get(self.tracker_id, {})
        d = {'Tracker ID': obj.get('tracker', {}).get('trackerId', self.tracker_id),
             'Tracking Number': obj.get('tracker', {}).get('trackingNumber', ''),
             'Shipment Reference': obj.get('tracker', {}).get('shipmentReference', ''),
             'Created At': obj.get('tracker', {}).get('createdAt', ''),
             'Shipment ID': obj.get('shipment', {}).get('shipmentId', ''),
             'Status Code': obj.get('shipment', {}).get('statusCode', ''),
             'Status Category': obj.get('shipment', {}).get('statusCategory', ''),
             'Status Milestone': obj.get('shipment', {}).get('statusMilestone', '')}

        return d
