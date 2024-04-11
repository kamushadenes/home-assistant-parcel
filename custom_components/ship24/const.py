"""Constants for the Parcel integration."""
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "ship24"
PLATFORMS: Final = [Platform.SENSOR]

DEFAULT_NAME: Final = "Ship24 Tracking"

CONF_API_KEY = "api_key"

ICON = "mdi:box-variant-closed"
CORREIOS_BASE_API = "https://proxyapp.correios.com.br/v1/sro-rastro/{}"
CORREIOS_BASE_URL = "https://proxyapp.correios.com.br"
