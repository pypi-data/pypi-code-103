import field_codecs
import msgpack
from crccheck.crc import Crc8SaeJ1850, Crc32Iscsi
from bitstring import Bits, ConstBitStream
from copy import copy
import operator
from std_msgs.msg import Header
import rospy

class RosMessageCodec(object):
    def __init__(self, ros_type, fields_dict: dict = None, checksum=None):
        self.ros_type = ros_type
        self.packet_codec = None
        self.checksum = checksum
        
        if fields_dict:
            self.metadata_decoder_fields = {}
            self.metadata_encoder_fields = {}

            for field_name, field_params in fields_dict.items():
                # We only support a few metadata fields for encoding
                codec_name = field_params.get('codec', 'auto')
                if codec_name in (field_codecs.metadata_decoders.keys()):
                    self.metadata_decoder_fields[field_name] = codec_name

            for field_name, field_params in fields_dict.items():
                # We only support a few metadata fields for encoding
                codec_name = field_params.get('codec', 'auto')
                if codec_name in (field_codecs.metadata_encoders.keys()):
                    self.metadata_encoder_fields[field_name] = codec_name
        else:
            self.metadata_decoder_fields = None
            self.metadata_encoder_fields = None

        self.root_field_codec = field_codecs.RosMsgFieldCodec(ros_type=ros_type, fields=fields_dict)
        
    def encode(self, ros_msg):
        encoded_bits, encoded_dict = self.root_field_codec.encode(ros_msg)

        if self.checksum:
            msgpack_bytes = msgpack.packb(encoded_dict)
            if self.checksum == 'crc8':
                calculated_crc = Crc8SaeJ1850.calc(msgpack_bytes)
                encoded_bits.append(Bits(uint=calculated_crc, length=8))
            elif self.checksum == 'crc32':
                calculated_crc = Crc32Iscsi.calc(msgpack_bytes)
                encoded_bits.append(Bits(uint=calculated_crc, length=32))
            #print("Encoded CRC: {}".format(hex(calculated_crc)))

        metadata_dict = self._encode_metadata(ros_msg)

        return encoded_bits, metadata_dict

    def decode(self, bits_to_decode: ConstBitStream, received_packet = None):
        rospy.loginfo("Decoding ROS message {}".format(self.ros_type))
        # Now, check CRC, if required.
        if self.checksum:
            # We need to decode this as a dict separately, so we need a new copy of the received bitstream.
            bits_copy = copy(bits_to_decode)
            bits_copy.pos = bits_to_decode.pos
            decoded_dict = self.root_field_codec.decode_as_dict(bits_copy)

        ros_msg = self.root_field_codec.decode(bits_to_decode)

        if self.checksum:
            msgpack_bytes = msgpack.packb(decoded_dict)
            # print("Msgpack length: {} bytes".format(len(msgpack_bytes)))
            if self.checksum == 'crc8':
                calculated_crc = Crc8SaeJ1850.calc(msgpack_bytes)
                # Next 8 bits of message are CRC
                received_crc = bits_to_decode.read('uint:8')
            elif self.checksum == 'crc32':
                calculated_crc = Crc32Iscsi.calc(msgpack_bytes)
                received_crc = bits_to_decode.read('uint:32')

            #print("Received CRC: {}".format(hex(received_crc)))
            if calculated_crc != received_crc:
                raise ValueError("Message CRC Mismatch")

        # Append metadata
        if received_packet:
            self._decode_metadata(ros_msg, received_packet)

        rospy.loginfo("ROS Message: {}".format(ros_msg))
        return ros_msg

    def _decode_metadata(self, ros_msg, received_packet):
        # This will decode metadata fields into the ros msg.
        # it only works on fields of te base ROS message, not any nested ROS messages (for now)
        if self.metadata_decoder_fields:
            for field_name, codec in self.metadata_decoder_fields.items():
                metadata_attribute = field_codecs.metadata_decoders[codec]
                value = operator.attrgetter(metadata_attribute)(received_packet)
                setattr(ros_msg, field_name, value)

    def _encode_metadata(self, ros_msg):
        # Look through the fields dict for one of the magic keywords specified in field_codecs.py
        if self.metadata_encoder_fields:
            metadata_dict = {}
            for field_name, codec in self.metadata_encoder_fields.items():
                metadata_dict[field_name] = getattr(ros_msg, codec)
            return metadata_dict
        else:
            return None

    @property
    def max_length_bits(self):
        if self.checksum == 'crc8':
            checksum_len = 8
        elif self.checksum == 'crc32': 
            checksum_len = 32
        else:
            checksum_len = 0
        return self.root_field_codec.max_length_bits + checksum_len

    @property
    def min_length_bits(self):
        if self.checksum == 'crc8':
            checksum_len = 8
        elif self.checksum == 'crc32':
            checksum_len = 32
        else:
            checksum_len = 0
        return self.root_field_codec.min_length_bits + checksum_len
