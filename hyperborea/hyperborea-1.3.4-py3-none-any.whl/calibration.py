import math
import struct

import asphodel


def get_channel_setting_values(settings, cal, unit_type, scale, offset):
    unit_settings = {cal.base_setting_index: unit_type}
    float_settings = {cal.base_setting_index + 1: scale,
                      cal.base_setting_index + 2: offset}

    if math.isfinite(cal.minimum):
        minimum = cal.minimum * scale + offset
        float_settings[cal.base_setting_index + 3] = minimum

    if math.isfinite(cal.maximum):
        maximum = cal.maximum * scale + offset
        float_settings[cal.base_setting_index + 4] = maximum

    if cal.resolution_setting_index < len(settings):
        float_settings[cal.resolution_setting_index] = scale

    return unit_settings, float_settings


def update_nvm(nvm, settings, unit_settings, float_settings, logger):
    nvm = bytearray(nvm)

    for setting_index, value in unit_settings.items():
        setting = settings[setting_index]
        if setting.setting_type != asphodel.SETTING_TYPE_UNIT_TYPE:
            msg = "Setting {} is not a unit type".format(setting_index)
            logger.error(msg)
        s = setting.u.byte_setting
        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        struct.pack_into(">B", nvm, byte_offset, value)

    for setting_index, value in float_settings.items():
        setting = settings[setting_index]
        if setting.setting_type == asphodel.SETTING_TYPE_INT32_SCALED:
            s = setting.u.int32_scaled_setting
            unscaled_value = int(round((value - s.offset) / s.scale))
            unscaled_value = max(unscaled_value, s.minimum)
            unscaled_value = min(unscaled_value, s.maximum)
            struct.pack_into(">i", nvm, s.nvm_word * 4, unscaled_value)
        elif setting.setting_type == asphodel.SETTING_TYPE_FLOAT:
            s = setting.u.float_setting
            unscaled_value = (value - s.offset) / s.scale
            unscaled_value = max(unscaled_value, s.minimum)
            unscaled_value = min(unscaled_value, s.maximum)
            struct.pack_into(">f", nvm, s.nvm_word * 4, unscaled_value)
        else:
            msg = "Setting {} is not a float type".format(setting_index)
            logger.error(msg)

    return nvm
