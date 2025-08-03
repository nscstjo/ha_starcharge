"""Sensor platform for StarCharge integration."""
from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_CODES
from .coordinator import StarChargeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up StarCharge sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # 从初始数据中获取充电桩ID
    stub_id = coordinator.data.get("stubId", "unknown")
    
    entities = [
        StarChargeVoltageSensor(coordinator, stub_id),
        StarChargeCurrentSensor(coordinator, stub_id),
        StarChargePowerSensor(coordinator, stub_id),
        StarChargeStatusSensor(coordinator, stub_id),
    ]
    
    async_add_entities(entities)


class StarChargeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for StarCharge sensors."""

    def __init__(
        self, 
        coordinator: StarChargeDataUpdateCoordinator,
        stub_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stub_id = stub_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, stub_id)},
            name=f"充电桩{stub_id}",
            manufacturer="StarCharge",
        )


class StarChargeVoltageSensor(StarChargeBaseSensor):
    """Sensor for StarCharge voltage."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = "V"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(
        self, 
        coordinator: StarChargeDataUpdateCoordinator,
        stub_id: str,
    ) -> None:
        """Initialize the voltage sensor."""
        super().__init__(coordinator, stub_id)
        self._attr_unique_id = f"{stub_id}_voltage"
        self._attr_name = f"充电桩{stub_id} 电压"
    
    @property
    def native_value(self) -> StateType:
        """Return the voltage value."""
        if self.coordinator.data and "order" in self.coordinator.data:
            return self.coordinator.data["order"].get("voltage", 0)
        return 0


class StarChargeCurrentSensor(StarChargeBaseSensor):
    """Sensor for StarCharge current."""

    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_native_unit_of_measurement = "A"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(
        self, 
        coordinator: StarChargeDataUpdateCoordinator,
        stub_id: str,
    ) -> None:
        """Initialize the current sensor."""
        super().__init__(coordinator, stub_id)
        self._attr_unique_id = f"{stub_id}_current"
        self._attr_name = f"充电桩{stub_id} 电流"
    
    @property
    def native_value(self) -> StateType:
        """Return the current value."""
        if self.coordinator.data and "order" in self.coordinator.data:
            return self.coordinator.data["order"].get("current", 0)
        return 0


class StarChargePowerSensor(StarChargeBaseSensor):
    """Sensor for StarCharge power."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = "kW"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def __init__(
        self, 
        coordinator: StarChargeDataUpdateCoordinator,
        stub_id: str,
    ) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator, stub_id)
        self._attr_unique_id = f"{stub_id}_power"
        self._attr_name = f"充电桩{stub_id} 功率"
    
    @property
    def native_value(self) -> StateType:
        """Return the power value."""
        if self.coordinator.data and "order" in self.coordinator.data:
            return self.coordinator.data["order"].get("kw", 0)
        return 0


class StarChargeStatusSensor(StarChargeBaseSensor):
    """Sensor for StarCharge status."""
    
    def __init__(
        self, 
        coordinator: StarChargeDataUpdateCoordinator,
        stub_id: str,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator, stub_id)
        self._attr_unique_id = f"{stub_id}_status"
        self._attr_name = f"充电桩{stub_id} 状态"
    
    @property
    def native_value(self) -> str:
        """Return the status value."""
        if self.coordinator.data:
            stub_status = self.coordinator.data.get("stubStatus")
            return STATUS_CODES.get(stub_status, "未知")
        return "未知"