from ..version import __version__


from ..const import INPUT, OFF, ON, RELAY, STATE, SENSOR


def ha_relay_availibilty_message(id: str, name: str, topic: str = "boneio"):
    """Create availability topic for HA."""
    return {
        "availability": [{"topic": f"{topic}/{STATE}"}],
        "command_topic": f"{topic}/relay/{id}/set",
        "device": {
            "identifiers": [topic],
            "manufacturer": "BoneIO",
            "model": "BoneIO Relay Board",
            "name": f"BoneIO {topic}",
            "sw_version": __version__,
        },
        "name": name,
        "payload_off": OFF,
        "payload_on": ON,
        "state_topic": f"{topic}/{RELAY}/{id}",
        "unique_id": f"{topic}{RELAY}{id}",
        "value_template": "{{ value_json.state }}",
    }


def ha_sensor_availibilty_message(id: str, name: str, topic: str = "boneio"):
    """Create availability topic for HA."""
    return {
        "availability": [{"topic": f"{topic}/{STATE}"}],
        "device": {
            "identifiers": [topic],
            "manufacturer": "BoneIO",
            "model": "BoneIO Relay Board",
            "name": f"BoneIO {topic}",
            "sw_version": __version__,
        },
        "icon": "mdi:gesture-double-tap",
        "name": name,
        "state_topic": f"{topic}/{INPUT}/{id}",
        "unique_id": f"{topic}{INPUT}{id}",
    }


def ha_sensor_temp_availibilty_message(id: str, name: str, topic: str = "boneio"):
    """Create availability topic for HA."""
    return {
        "availability": [{"topic": f"{topic}/{STATE}"}],
        "device": {
            "identifiers": [topic],
            "manufacturer": "BoneIO",
            "model": "BoneIO Relay Board",
            "name": f"BoneIO {topic}",
            "sw_version": __version__,
        },
        "name": name,
        "state_topic": f"{topic}/{SENSOR}/{id}",
        "unique_id": f"{topic}{SENSOR}{id}",
        "device_class": "temperature",
        "state_class": "measurement",
        "unit_of_measurement": "°C",
        "value_template": "{{ value_json.state }}",
    }
