import math
import struct

import asphodel


def find_usb_devices():
    devices_by_serial = {}
    for device in asphodel.find_usb_devices():
        try:
            device.open()
            serial_number = device.get_serial_number()
            devices_by_serial[serial_number] = device
        except asphodel.AsphodelError:
            continue
        finally:
            device.close()
    return devices_by_serial


def find_tcp_devices():
    devices_by_serial = {}
    for device in asphodel.find_tcp_devices():
        adv = device.tcp_get_advertisement()
        serial_number = adv.serial_number
        devices_by_serial[serial_number] = device
    return devices_by_serial


def find_all_devices():
    devices = {}

    if asphodel.nativelib.usb_devices_supported:
        devices.update(find_usb_devices())

    if asphodel.nativelib.tcp_devices_supported:
        devices.update(find_tcp_devices())

    if not (asphodel.nativelib.usb_devices_supported or
            asphodel.nativelib.tcp_devices_supported):
        # no TCP or USB supported by DLL
        raise Exception("Asphodel library does not support USB or TCP devices")

    return devices


def get_choice(options, prompt=None):
    if prompt is None:
        prompt = "Selection: "

    choices = set(k for k, _m in options)
    choices.discard(None)

    d = {c.lower(): c for c in choices}

    choice = None
    while choice not in d:
        choice = input(prompt)
        if choice:
            choice = choice.lower()

    return d[choice]


def print_options(title, options):
    max_length = max(len(k) for k, _m in options if k is not None)

    print("")
    print("--- {} ---".format(title))
    for key, message in options:
        if key is not None:
            print("{}  {}".format(key.ljust(max_length), message))
        else:
            print("")
            print("{}  {}:".format(" " * max_length, message))
    print("")


def do_string_setting(setting_name, initial_str, default_str):
    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial_str))
    print("Default setting: {}".format(default_str))
    value = input("New Value: ")
    return value.encode('UTF-8')


def do_integer_setting(setting_name, initial, default, minimum, maximum):
    if minimum > maximum:
        # they're backwards
        maximum, minimum = minimum, maximum

    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial))
    if default is not None:
        print("Default setting: {}".format(default))
    else:
        print("Default setting: invalid")
    prompt = "New Value (range {} to {}): ".format(minimum, maximum)

    while True:
        value_str = input(prompt)
        if value_str:
            try:
                value = int(value_str)
                if minimum <= value <= maximum:
                    return value
            except ValueError:
                continue


def do_float_setting(setting_name, initial, default, minimum, maximum):
    if minimum > maximum:
        # they're backwards
        maximum, minimum = minimum, maximum

    print("")
    print("--- {} ---".format(setting_name))
    print("")
    print("Initial setting: {}".format(initial))
    if default is not None:
        print("Default setting: {}".format(default))
    else:
        print("Default setting: invalid")
    prompt = "New Value (range {} to {}): ".format(minimum, maximum)

    while True:
        value_str = input(prompt)
        if value_str:
            try:
                value = float(value_str)
                if math.isnan(value):
                    # can't compare to min and max
                    return value
                if minimum <= value <= maximum:
                    return value
            except ValueError:
                continue
    return value


def do_choice_setting(setting_name, initial, default, options):
    print_options(setting_name, options)

    for key, name in options:
        if key == str(initial):
            print("Initial setting: {} ({})".format(name, key))
            break
    else:
        print("Initial setting: unknown ({})".format(initial))

    if default is not None:
        for key, name in options:
            if key == str(default):
                print("Default setting: {} ({})".format(name, key))
                break
        else:
            print("Default setting: unknown ({})".format(default))
    else:
        print("Default setting: invalid")

    choice = get_choice(options, "New Value: ")
    return int(choice)


def parse_byte_setting(nvm, setting, default_bytes):
    s = setting.u.byte_setting
    byte_offset = s.nvm_word * 4 + s.nvm_word_byte
    initial = struct.unpack_from(">B", nvm, byte_offset)[0]
    if len(default_bytes) == 1:
        default = default_bytes[0]
    else:
        default = None
    return initial, default


def write_byte_setting(nvm, setting, value):
    s = setting.u.byte_setting
    byte_offset = s.nvm_word * 4 + s.nvm_word_byte
    struct.pack_into(">B", nvm, byte_offset, value)


def do_setting(nvm, setting, custom_enums):
    length = setting.default_bytes_length
    default_bytes = bytes(setting.default_bytes[0:length])
    setting_name = setting.name.decode("UTF-8")

    if setting.setting_type == asphodel.SETTING_TYPE_BYTE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        value = do_integer_setting(setting_name, initial, default, 0, 255)
        write_byte_setting(nvm, setting, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_BOOLEAN:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = [("0", "False"),
                   ("1", "True")]
        if initial > 1:
            options.append((str(initial), "unknown"))
        value = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_UNIT_TYPE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = []
        for i, name in enumerate(asphodel.unit_type_names):
            options.append((str(i), name))
        if initial >= len(options):
            options.append((str(initial), "unknown"))
        value = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_CHANNEL_TYPE:
        initial, default = parse_byte_setting(nvm, setting, default_bytes)
        options = []
        for i, name in enumerate(asphodel.channel_type_names):
            options.append((str(i), name))
        if initial >= len(options):
            options.append((str(initial), "unknown"))
        value = do_choice_setting(setting_name, initial, default, options)
        write_byte_setting(nvm, setting, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_STRING:
        s = setting.u.string_setting
        fmt = ">{}s".format(s.maximum_length)
        raw = struct.unpack_from(fmt, nvm, s.nvm_word * 4)[0]
        raw = raw.split(b'\x00', 1)[0]
        raw = raw.split(b'\xff', 1)[0]
        try:
            initial_str = raw.decode("UTF-8")
        except UnicodeDecodeError:
            initial_str = "<ERROR>"
        try:
            default_str = default_bytes.decode("UTF-8")
        except UnicodeDecodeError:
            default_str = "unknown"
        value = do_string_setting(setting_name, initial_str, default_str)
        struct.pack_into(fmt, nvm, s.nvm_word * 4, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_INT32:
        s = setting.u.int32_setting
        initial = struct.unpack_from(">i", nvm, s.nvm_word * 4)[0]
        if len(default_bytes) == 4:
            default = struct.unpack_from(">i", default_bytes, 0)[0]
        else:
            default = None
        value = do_integer_setting(setting_name, initial, default,
                                   s.minimum, s.maximum)
        struct.pack_into(">i", nvm, s.nvm_word * 4, value)
    elif setting.setting_type == asphodel.SETTING_TYPE_INT32_SCALED:
        s = setting.u.int32_scaled_setting
        scaled_min = s.minimum * s.scale + s.offset
        scaled_max = s.maximum * s.scale + s.offset
        initial = struct.unpack_from(">i", nvm, s.nvm_word * 4)[0]
        initial = initial * s.scale + s.offset
        if len(default_bytes) == 4:
            default = struct.unpack_from(">i", default_bytes, 0)[0]
            default = default * s.scale + s.offset
        else:
            default = None
        value = do_float_setting(setting_name, initial, default,
                                 scaled_min, scaled_max)
        unscaled_value = int(round((value - s.offset) / s.scale))
        unscaled_value = max(unscaled_value, s.minimum)
        unscaled_value = min(unscaled_value, s.maximum)
        struct.pack_into(">i", nvm, s.nvm_word * 4, unscaled_value)
    elif setting.setting_type == asphodel.SETTING_TYPE_FLOAT:
        s = setting.u.float_setting
        scaled_min = s.minimum * s.scale + s.offset
        scaled_max = s.maximum * s.scale + s.offset
        initial = struct.unpack_from(">f", nvm, s.nvm_word * 4)[0]
        initial = initial * s.scale + s.offset
        if len(default_bytes) == 4:
            default = struct.unpack_from(">f", default_bytes, 0)[0]
            default = default * s.scale + s.offset
        else:
            default = None
        value = do_float_setting(setting_name, initial, default,
                                 scaled_min, scaled_max)
        unscaled_value = (value - s.offset) / s.scale
        struct.pack_into(">f", nvm, s.nvm_word * 4, unscaled_value)
    elif setting.setting_type == asphodel.SETTING_TYPE_CUSTOM_ENUM:
        s = setting.u.custom_enum_setting
        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">B", nvm, byte_offset)[0]
        if len(default_bytes) == 1:
            default = default_bytes[0]
        else:
            default = None
        if s.custom_enum_index >= len(custom_enums):
            # invalid index
            value = do_integer_setting(setting_name, initial, default, 0, 255)
        else:
            options = []
            for i, name in enumerate(custom_enums[s.custom_enum_index]):
                options.append((str(i), name))
            if initial >= len(options):
                options.append((str(initial), "unknown"))
            value = do_choice_setting(setting_name, initial, default, options)
        struct.pack_into(">B", nvm, byte_offset, value)
    else:
        # Note SETTING_TYPE_BYTE_ARRAY and SETTING_TYPE_FLOAT_ARRAY are not
        # supported by this utility as they're not actually used in any devices
        # at the time of this writing
        print("Unsupported setting type!")


def reset_and_reconnect(device):
    device.reset()
    device.reconnect()


def do_device_menu(device):
    device.open()
    sn = device.get_serial_number()
    title = "{} Menu".format(sn)

    setting_count = device.get_setting_count()
    settings = [device.get_setting(i) for i in range(setting_count)]
    unassigned_setting_ids = set(range(setting_count))

    setting_category_count = device.get_setting_category_count()
    setting_categories = []
    for i in range(setting_category_count):
        name = device.get_setting_category_name(i)
        category_settings = device.get_setting_category_settings(i)
        setting_categories.append((name, category_settings))
        for setting_id in category_settings:
            unassigned_setting_ids.discard(setting_id)

    custom_enum_counts = device.get_custom_enum_counts()
    custom_enums = {}
    for i, count in enumerate(custom_enum_counts):
        custom_enums[i] = [device.get_custom_enum_value_name(i, v)
                           for v in range(count)]

    nvm_size = device.get_nvm_size()
    nvm = bytearray(device.read_nvm_section(0, nvm_size))

    options = [('p', "Print NVM"),
               ('w', "Write NVM and reset device"),
               ('a', "Abort without saving")]

    if (unassigned_setting_ids):
        options.append((None, "Device Settings"))
        for setting_id in sorted(unassigned_setting_ids):
            setting_name = settings[setting_id].name.decode("UTF-8")
            options.append((str(setting_id), setting_name))
    for category_name, category_settings in setting_categories:
        options.append((None, category_name))
        for setting_id in category_settings:
            setting_name = settings[setting_id].name.decode("UTF-8")
            options.append((str(setting_id), setting_name))

    while True:
        print_options(title, options)
        choice = get_choice(options)

        if choice == 'p':
            print("")
            for line in asphodel.format_nvm_data(nvm):
                print(line)
        elif choice == 'a':
            device.close()
            return
        elif choice == 'w':
            device.erase_nvm()
            device.write_nvm_section(0, nvm)
            reset_and_reconnect(device)
            device.close()
            return
        else:
            setting_id = int(choice)
            do_setting(nvm, settings[setting_id], custom_enums)


def do_main_menu(devices):
    while True:
        options = [('r', "Rescan devices"),
                   ('q', "Quit")]

        if not devices:
            options.append((None, "No Devices"))
        else:
            options.append((None, "Devices"))
            for sn in devices.keys():
                options.append((sn, "Edit device {}".format(sn)))

        print_options("Main Menu", options)
        choice = get_choice(options)

        if choice == 'r':
            devices = find_all_devices()
        elif choice == 'q':
            return
        else:
            do_device_menu(devices[choice])


def main():
    devices = find_all_devices()
    do_main_menu(devices)


if __name__ == "__main__":
    main()
