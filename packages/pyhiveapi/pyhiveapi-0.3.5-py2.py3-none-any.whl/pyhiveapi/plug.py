"""Hive Switch Module."""

from .helper.const import HIVETOHA


class Plug:
    """Hive Switch Code."""

    plugType = "Switch"

    def __init__(self, session):
        """Initialise plug."""
        self.session = session

    def get_plug(self, device):
        """Get smart plug data."""
        self.session.log.log(
            device["hiveID"], self.plugType, "Getting switch data."
        )
        device["deviceData"].update(
            {"online": self.session.attr.online_offline(device["device_id"])}
        )
        dev_data = {}

        if device["deviceData"]["online"]:
            self.helper.deviceRecovered(device["device_id"])
            data = self.session.data.devices[device["device_id"]]
            dev_data = {
                "hiveID": device["hiveID"],
                "hiveName": device["hiveName"],
                "hiveType": device["hiveType"],
                "haName": device["haName"],
                "haType": device["haType"],
                "device_id": device["device_id"],
                "device_name": device["device_name"],
                "status": {
                    "state": self.get_state(device),
                    "power_usage": self.get_power_usage(device),
                },
                "deviceData": data.get("props", None),
                "parentDevice": data.get("parent", None),
                "custom": device.get("custom", None),
                "attributes": self.session.attr.state_attributes(
                    device["device_id"], device["hiveType"]
                ),
            }

            self.session.log.log(
                device["hiveID"],
                self.plugType,
                "Device update {0}",
                info=[dev_data["status"]],
            )
            self.session.devices.update({device["hiveID"]: dev_data})
            return self.session.devices[device["hiveID"]]
        else:
            self.session.log.error_check(
                device["device_id"], "ERROR", device["deviceData"]["online"]
            )
            return device

    def get_state(self, device):
        """Get plug current state."""
        state = None
        final = None

        try:
            data = self.session.data.products[device["hiveID"]]
            state = data["state"]["status"]
            final = HIVETOHA["Switch"].get(state, state)
        except KeyError as e:
            self.session.log.error(e)

        return final

    def get_power_usage(self, device):
        """Get smart plug current power usage."""
        state = None

        try:
            data = self.session.data.products[device["hiveID"]]
            state = data["props"]["powerConsumption"]
        except KeyError as e:
            self.session.log.error(e)

        return state

    def turn_on(self, device):
        """Set smart plug to turn on."""
        final = False

        if (
            device["hiveID"] in self.session.data.products
            and device["deviceData"]["online"]
        ):
            self.session.hiveRefreshTokens()
            data = self.session.data.products[device["hiveID"]]
            resp = self.session.api.setState(
                data["type"], data["id"], status="ON"
            )
            if resp["original"] == 200:
                final = True
                self.session.getDevices(device["hiveID"])

        return final

    def turn_off(self, device):
        """Set smart plug to turn off."""
        final = False

        if (
            device["hiveID"] in self.session.data.products
            and device["deviceData"]["online"]
        ):
            self.session.hiveRefreshTokens()
            data = self.session.data.products[device["hiveID"]]
            resp = self.session.api.setState(
                data["type"], data["id"], status="OFF"
            )
            if resp["original"] == 200:
                final = True
                self.session.getDevices(device["hiveID"])

        return final
