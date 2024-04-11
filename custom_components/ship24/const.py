from homeassistant.const import Platform
from typing import Final

DOMAIN: Final = "ship24"
PLATFORMS: Final = [Platform.SENSOR]

DEFAULT_NAME: Final = "Ship24 Tracking"

CONF_API_KEY = "api_key"

ICON = "mdi:box-variant-closed"

statusCodes = {
    # Data
    "data_order_created": "Order created",
    "data_order_cancelled": "Order cancelled",
    "data_delivery_proposed": "Delivery proposed",
    "data_delivery_decided": "Delivery decided",

    # Destination
    "destination_arrival": "Arrived in destination country",

    # Customs
    "customs_received": "Received by customs",
    "customs_exception": "Exception or delay in customs clearance",
    "customs_rejected": "Rejected by customs",
    "customs_cleared": "Cleared by customs",

    # Delivery
    "delivery_available_for_pickup": "Available for pickup",
    "delivery_out_for_delivery": "Out for delivery",
    "delivery_attempted": "Delivery attempted",
    "delivery_exception": "Exception or delay in delivery",
    "delivery_delivered": "Delivered",

    # Exception
    "exception_return": "Shipment undeliverable",
}
