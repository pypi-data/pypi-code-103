import logging
from collections import namedtuple
from typing import Union, List, Dict, Optional, Iterable, cast
from .assets_config import AssetsConfig


logger = logging.getLogger(__name__)

SensorTag = namedtuple("SensorTag", ["name", "asset"])

Tag = Union[str, SensorTag]


def load_sensor_tag(
    sensor: Union[Dict, List],
) -> SensorTag:
    # TODO better docstring
    sensor_tag: Union[str, SensorTag]
    if isinstance(sensor, Dict):
        for key in ("name", "asset"):
            if key not in sensor:
                raise SensorTagNormalizationError(
                    "Sensor representation %s does not have '%s'" % (repr(sensor), key)
                )
        return SensorTag(sensor["name"], sensor["asset"])

    elif isinstance(sensor, List):
        if len(sensor) != 2:
            raise SensorTagNormalizationError(
                "Sensor representation list %s does not have enough elements"
                % repr(sensor)
            )
        return SensorTag(sensor[0], sensor[1])

    else:
        raise SensorTagNormalizationError(
            f"Unable to load sensor_tag from {sensor} with type {type(sensor)}"
        )


def normalize_sensor_tag(
    assets_config: AssetsConfig,
    sensor: Union[Dict, List, str, SensorTag],
    asset: str = None,
) -> Union[str, SensorTag]:
    # TODO better docstring
    sensor_tag: Union[str, SensorTag]

    if isinstance(sensor, SensorTag):
        sensor_tag = sensor

    elif isinstance(sensor, Dict) or isinstance(sensor, List):
        sensor_tag = load_sensor_tag(sensor)

    elif isinstance(sensor, str):
        if asset is not None:
            sensor_tag = SensorTag(sensor, asset)
        else:
            sensor_tag = sensor

    else:
        raise SensorTagNormalizationError(
            f"Sensor {sensor} with type {type(sensor)} cannot be converted to a valid "
            f"SensorTag"
        )

    if isinstance(sensor_tag, SensorTag):
        asset_name = assets_config.prepare_asset_name(sensor_tag.asset)
        if sensor_tag.asset != asset_name:
            return SensorTag(sensor_tag.name, asset_name)
    return sensor_tag


def legacy_normalize_sensor_tag(
    assets_config: AssetsConfig,
    storage: str,
    sensor: Union[str, SensorTag],
    asset: Optional[str] = None,
) -> SensorTag:
    # TODO better docstring
    if isinstance(sensor, SensorTag):
        return sensor

    path_specs = assets_config.get_paths(storage, sensor, asset)
    if len(path_specs) == 1:
        path_spec = path_specs[0]
        return SensorTag(sensor, path_spec.asset)

    considered_assets = [path_spec.asset for path_spec in path_specs]
    raise SensorTagNormalizationError(
        "Unable to find exact asset for sensor %s in the assets config. Considered assets: %s"
        % (repr(sensor), ", ".join(repr(asset) for asset in considered_assets))
    )


def to_list_of_strings(sensor_tag_list: List[SensorTag]):
    return [sensor_tag.name for sensor_tag in sensor_tag_list]


def extract_tag_name(tag: Tag) -> str:
    if type(tag) is str:
        return cast(str, tag)
    else:
        return cast(SensorTag, tag).name


def extract_tag_asset(tag: Tag) -> Optional[str]:
    if type(tag) is not str:
        return cast(SensorTag, tag).asset
    return None


def tag_to_json(tag: Tag) -> Union[str, dict]:
    if type(tag) is str:
        return cast(str, tag)
    else:
        sensor_tag = cast(SensorTag, tag)
        return {
            "name": sensor_tag.name,
            "asset": sensor_tag.asset,
        }


def validate_tag_equality(tag1: Tag, tag2: Tag):
    """
    SensorTag should not have a different asset name.
    str and SensorTag should not have the same name.
    """
    type_tag1, type_tag2 = type(tag1), type(tag2)
    if type_tag1 is SensorTag and type_tag2 is SensorTag:
        if cast(SensorTag, tag1).asset != cast(SensorTag, tag2).asset:
            raise ValueError(
                "Tags %s and %s with the same name but different assets"
                % (repr(tag1), repr(tag2))
            )
    for _type in (str, SensorTag):
        if type_tag1 is _type:
            if type_tag2 is not _type:
                tag_name1 = extract_tag_name(tag1)
                tag_name2 = extract_tag_name(tag2)
                if tag_name1 == tag_name2:
                    raise ValueError(
                        "Tags %s and %s has different type but the same name"
                        % (repr(tag1), repr(tag2))
                    )


def unique_tag_names(tags: Iterable[Tag]) -> Dict[str, Tag]:
    """
    Check the uniqueness of the tags

    Parameters
    ----------
    tags: Iterable[Tag]

    Returns
    -------
    Dict[str, Tag]
        Keys here are the unique tag names

    """
    orig_tags: Dict[str, Tag] = {}
    for tag in tags:
        tag_name = extract_tag_name(tag)
        if tag_name in orig_tags:
            validate_tag_equality(tag, orig_tags[tag_name])
        else:
            orig_tags[tag_name] = tag
    return orig_tags


class SensorTagNormalizationError(ValueError):
    """Error indicating that something went wrong normalizing a sensor tag"""

    pass
