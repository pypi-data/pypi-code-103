import binascii
import io
import json
import lzma
import os.path

import asphodel


def get_default_file(device_info, base_dir=None):
    if not base_dir:
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../"))

    try:
        import firmutil.repo_info
        boardname, boardrev = device_info['board_info']
        repo = firmutil.repo_info.get_repo_from_board(boardname, boardrev)
    except ImportError:
        repo = None

    if not repo:
        repo = device_info['repo_name']

    if not repo:
        # couldn't figure it out
        return ("", "")

    file_dir = os.path.abspath(
        os.path.join(base_dir, f"{repo}/firmware/build"))

    if not os.path.exists(file_dir):
        return ("", "")

    for file_name in os.listdir(file_dir):
        if os.path.splitext(file_name)[1] == ".firmware":
            return (file_dir, file_name)

    return ("", "")


def decode_firm_file(firm_file):
    with lzma.LZMAFile(firm_file) as lzma_file:
        with io.TextIOWrapper(lzma_file) as f:
            return json.load(f)


def decode_firm_bytes(firm_bytes):
    json_str = lzma.decompress(firm_bytes).decode()
    return json.loads(json_str)


def is_board_supported(firm_data, device_info):
    if firm_data['chip'] != device_info['chip_model']:
        return False

    # NOTE: board_info tuple is swapped from firm_data
    for rev, board_name in firm_data['board']:
        if (rev == device_info['board_info'][1] and
                board_name == device_info['board_info'][0]):
            return True
    return False


def already_programmed(firm_data, device_info):
    if device_info['supports_bootloader']:
        # don't assume anything if it's in the bootloader
        return False

    # make sure the data matches
    if firm_data.get('build_info') != device_info['build_info']:
        return False
    if firm_data.get('build_date') != device_info['build_date']:
        return False

    if firm_data.get('application', False) is not True:
        # firmware isn't for the application, abort
        return False

    if firm_data.get('bootloader', False) is not False:
        # firmware also contains the bootloader, abort
        return False

    # if we've made it to this point then the firmware contains the application
    # and only the application and it matches the build info strings already
    # present on the running application
    return True


def do_bootload_page(device, done_bytes, page_data, block_sizes,
                     progress_pipe):
    index = 0
    remaining = len(page_data)
    while remaining > 0:
        block_size = max(x for x in block_sizes if x <= remaining)
        device.write_bootloader_code_block(page_data[index:index + block_size])
        index += block_size
        remaining -= block_size

        progress_pipe.send(done_bytes + index)


def do_bootload_pass(device, firm_data, block_sizes, verify_size,
                     progress_pipe):
    done_bytes = 0

    for page_info in firm_data['data']:
        page_number = page_info[0]
        nonce = binascii.a2b_hex(page_info[1])
        page_data = binascii.a2b_hex(page_info[2])
        digest = binascii.a2b_hex(page_info[3])

        progress_pipe.send("Writing Page {}".format(page_number))

        # see if the page needs to be written
        device.start_bootloader_page(page_number, nonce)
        try:
            device.verify_bootloader_page(digest)
            different = False
        except asphodel.AsphodelError as e:
            if e.args[1] == "ERROR_CODE_INVALID_DATA":
                different = True
            else:
                raise

        if different:
            device.start_bootloader_page(page_number, nonce)
            do_bootload_page(device, done_bytes, page_data, block_sizes,
                             progress_pipe)
            device.finish_bootloader_page(digest)

        done_bytes += len(page_data)
        progress_pipe.send(done_bytes)

    for page_info in firm_data['data']:
        page_number = page_info[0]
        nonce = binascii.a2b_hex(page_info[1])
        digest = binascii.a2b_hex(page_info[3])

        progress_pipe.send("Verifying Page {}".format(page_number))

        device.start_bootloader_page(page_number, nonce)
        device.verify_bootloader_page(digest)

        done_bytes += verify_size
        progress_pipe.send(done_bytes)


def do_bootload(device, firm_data, progress_pipe):
    tries = 10
    block_sizes = None

    # figure out how many bytes need to be written
    write_bytes = sum(len(binascii.a2b_hex(p[2])) for p in firm_data['data'])

    # start the bootloader
    progress_pipe.send("Switching to bootloader...")
    if not device.supports_bootloader_commands():
        device.bootloader_jump()
        while True:
            try:
                device.reconnect(bootloader=True)
            except asphodel.AsphodelError:
                tries -= 1
                if tries == 0:
                    raise
                else:
                    # connect to application
                    device.reconnect(application=True)
                    device.bootloader_jump()

                    # try again
                    continue
            break  # exit the loop

    while True:
        try:
            if block_sizes is None:
                block_sizes = device.get_bootloader_block_sizes()

                # assume a page verify takes the same amount of time as writing
                #  the largest block size
                verify_size = max(block_sizes)
                verify_bytes = verify_size * len(firm_data['data'])

                total_bytes = write_bytes + verify_bytes
                progress_pipe.send((0, total_bytes))

            do_bootload_pass(device, firm_data, block_sizes, verify_size,
                             progress_pipe)
        except asphodel.AsphodelError:
            tries -= 1
            if tries == 0:
                raise
            else:
                # connect to bootloader
                device.reconnect(bootloader=True)

                # try again
                continue
        break  # exit the loop

    # start the application
    progress_pipe.send("Switching to main app...")
    device.bootloader_start_program()

    while True:
        try:
            device.reconnect(application=True)
        except asphodel.AsphodelError:
            tries -= 1
            if tries == 0:
                raise
            else:
                # connect to bootloader
                device.reconnect(bootloader=True)
                device.bootloader_start_program()

                # try again
                continue
        break  # exit the loop

    progress_pipe.send("Finished")
    progress_pipe.close()


def force_bootloader(device):
    # start bootloader
    device.bootloader_jump()

    # connect to bootloader
    device.reconnect(bootloader=True)


def force_application(device):
    # start the application
    device.bootloader_start_program()

    # connect to the application
    device.reconnect(application=True)
