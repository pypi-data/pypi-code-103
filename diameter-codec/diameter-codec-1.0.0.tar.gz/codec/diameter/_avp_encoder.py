import binascii
import logging
import struct
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional, Tuple, NamedTuple
from urllib.parse import ParseResult, urlparse

from codec.diameter._diam_tools import _DiamTools
from codec.diameter.dictionary import DictionaryLayout, AvpDict


class Avp(NamedTuple):
    """Generic Avp data holder."""
    name: str
    data: any


class _AvpEncoder:
    def __init__(self, dictionary_layout: DictionaryLayout):
        """
        Constructor
        :type dictionary_layout: DictionaryLayout
        :param dictionary_layout: diameter dictionary layout
        """
        if not dictionary_layout:
            raise ValueError("dictionary_layout is None.")
        self.dictionary_layout = dictionary_layout

    def __encode_avp_grouped(self, application_id: int, avp_grouped_set: Tuple, buffer: bytes = b'') -> bytes:
        """
        Internal function for 'grouped' encoding
        :param application_id: application id
        :param avp_grouped_set: tuple of Avp
        :param buffer: accumulator used in recursion loop
        :return: grouped encoded as bytes
        """
        for avp_item in avp_grouped_set:  # list of single avp and group's (mix mode)
            is_grouped: bool = avp_item.data is tuple
            if not is_grouped:
                buffer += self.encode_avp(application_id, avp_item)
            else:
                return self.__encode_avp_grouped(application_id, avp_item, buffer)

        return buffer

    def encode_avp(self, application_id: int, avp: Avp) -> Optional[bytes]:
        """
        Converts Avp to bytes before sending to diameter server.
        :param application_id: application id
        :param avp: avp (single or grouped)
        :return: bytes for diameter server
        """
        logging.debug("application_id={application_id}, avp={avp}", application_id=application_id, avp=avp)

        if application_id < 0:
            raise ValueError("application_id must be greater or equal to 0.")

        if not avp:
            raise ValueError("avp object is set to None.")

        if not avp.name:
            raise ValueError("avp.name is empty or None.")

        avp_dict: AvpDict = self.dictionary_layout.find_avp_by_name(application_id, avp.name.strip())
        if avp_dict is None:
            logging.warning("ENCODER: application_id={application_id}, avp name={avp_name} in diameter dictionary not "
                            "found. It will be omitted!", application_id=application_id, avp_name=avp.name.strip())
            return None

        bytes_4_code: bytes = avp_dict.code.to_bytes(4, "big")
        bytes_1_flags: bytes
        bytes_3_length: bytes
        bytes_4_vendor_id: bytes
        bytes_3_data: bytes = b''
        avp_buffer: bytes = b''
        avp_length: int

        if avp_dict.type.lower() == "unsigned32" and isinstance(avp.data, int):
            bytes_3_data = struct.pack(">I", int(avp.data))
        elif avp_dict.type.lower() == "unsigned64" and isinstance(avp.data, int):
            bytes_3_data = struct.pack(">Q", avp.data)
        elif avp_dict.type.lower() == "integer32" and isinstance(avp.data, int):
            bytes_3_data = struct.pack(">i", avp.data)
        elif avp_dict.type.lower() == "integer64" and isinstance(avp.data, int):
            bytes_3_data = struct.pack(">q", avp.data)
        elif avp_dict.type.lower() == "float32" and isinstance(avp.data, float):
            bytes_3_data = struct.pack(">f", avp.data)
        elif avp_dict.type.lower() == "float64" and isinstance(avp.data, float):
            bytes_3_data = struct.pack(">d", avp.data)
        elif avp_dict.type.lower() == "utf8string" and isinstance(avp.data, str):
            bytes_3_data = str(avp.data).encode("utf-8")
        elif avp_dict.type.lower() == "octetstring" and isinstance(avp.data, str):
            bytes_3_data = str(avp.data).encode("utf-8")
        elif avp_dict.type.lower() == "diameteridentity" and isinstance(avp.data, str):
            bytes_3_data = str(avp.data).encode("utf-8")
        elif avp_dict.type.lower() == "grouped" and isinstance(avp.data, tuple):
            bytes_3_data = self.__encode_avp_grouped(application_id, avp.data)
        elif avp_dict.type.lower() == "address" and isinstance(avp.data, (IPv4Address, IPv6Address)):
            bytes_3_data = avp.data.packed
        elif avp_dict.type.lower() == "address" and isinstance(avp.data, str):
            bytes_3_data = ip_address(str(avp.data)).packed
        elif avp_dict.type.lower() == "time" and isinstance(avp.data, int):
            secs_between_1900_and_1970: int = (70 * 365 + 17) * 86400
            timestamp: int = int(avp.data) + secs_between_1900_and_1970
            bytes_3_data = struct.pack(">I", timestamp)
        elif avp_dict.type.lower() == "diameteruri" and isinstance(avp.data, ParseResult):
            bytes_3_data = avp.data.geturl().encode("utf-8")
        elif avp_dict.type.lower() == "diameteruri" and isinstance(avp.data, str):
            bytes_3_data = urlparse(str(avp.data)).geturl().encode("utf-8")
        elif avp_dict.type.lower() == "ipfilterrule" and isinstance(avp.data, str):
            bytes_3_data = str(avp.data).encode("utf-8")
        elif avp_dict.type.lower() == "enumerated" and isinstance(avp.data, str):
            for enum_value, enum_text in avp_dict.enums.items():
                if enum_text.strip() == avp.data.strip():
                    bytes_3_data = struct.pack(">i", enum_value)
                    break

            if not bytes_3_data:
                logging.warning("ENCODER: application_id={application_id}, {avp_dict_name}(code={code}) has "
                                "unknown enumerated text=\'{avp_data}\'",
                                application_id=application_id,
                                avp_dict_name=avp_dict.name,
                                code=avp_dict.code,
                                avp_data=avp.data)

        elif avp.data:  # unknown type, do best effort to encode
            logging.warning("ENCODER: application_id={application_id}, {avp_dict_name}(code={code}) has "
                            "unknown data type=\'{avp_data_type}\'",
                            application_id=application_id,
                            avp_dict_name=avp_dict.name,
                            code=avp_dict.code,
                            avp_data_type=avp_dict.type)

            bytes_3_data = str(avp.data).encode("utf-8")
        else:
            logging.warning("ENCODER: application_id={application_id}, {avp_dict_name}(code={code}) has no data!",
                            application_id=application_id,
                            avp_dict_name=avp_dict.name,
                            code=avp_dict.code)

        has_vendor_id: bool = avp_dict.vendor_id > 0
        bytes_1_flags = _DiamTools.modify_flags_bit(bytes([0]), 7, has_vendor_id)
        bytes_1_flags = _DiamTools.modify_flags_bit(bytes_1_flags, 6, avp_dict.mandatory_flag)

        if has_vendor_id > 0:
            bytes_4_vendor_id = avp_dict.vendor_id.to_bytes(4, "big")
            avp_length = 12 + len(bytes_3_data)
            bytes_3_length = avp_length.to_bytes(3, "big")
            avp_buffer += bytes_4_code + bytes_1_flags + bytes_3_length + bytes_4_vendor_id + bytes_3_data
        else:
            avp_length = 8 + len(bytes_3_data)
            bytes_3_length = avp_length.to_bytes(3, "big")
            avp_buffer += bytes_4_code + bytes_1_flags + bytes_3_length + bytes_3_data

        padding: int = avp_length % 4
        if padding > 0:
            padding = 4 - padding
            avp_buffer += bytes(padding)

        logging.debug("ENCODER: application_id={application_id}, avp_dict={avp_dict}, avp_length={avp_length}, "
                      "padding={padding}, avp_buffer={avp_buffer}",
                      application_id=application_id,
                      avp_dict=avp_dict,
                      avp_length=avp_length,
                      padding=padding,
                      avp_buffer=binascii.hexlify(avp_buffer))

        return avp_buffer
