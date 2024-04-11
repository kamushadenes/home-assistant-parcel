from homeassistant.const import Platform
from typing import Final

DOMAIN: Final = "ship24"
PLATFORMS: Final = [Platform.SENSOR]

DEFAULT_NAME: Final = "Ship24 Tracking"

CONF_API_KEY = "api_key"

ICON = "mdi:box-variant-closed"