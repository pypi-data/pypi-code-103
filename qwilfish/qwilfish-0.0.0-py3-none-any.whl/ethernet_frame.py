# Standard lib imports
import random
import re


# Local imports
from qwilfish.constants import DEFAULT_START_SYMBOL
from qwilfish.grammar import opts

# TODO fuzz by changing endianness of fields and/or bytes
# TODO fuzz by inserting wrong TLVs

HEX_MAP = {"0": "0000", "1": "0001", "2": "0010", "3": "0011",
           "4": "0100", "5": "0101", "6": "0110", "7": "0111",
           "8": "1000", "9": "1001", "A": "1010", "B": "1011",
           "C": "1100", "D": "1101", "E": "1110", "F": "1111"}

def srange(characters):
    return [c for c in characters]

def to_binstr(ethernet_frame, subtree=None):
    symbol, children = subtree

    if children == []:
        if symbol == "x":
            return ("", []) # Turn single x:es into null expansions to remove
        else:
            new_symbol = \
                re.sub("x[0-9a-fA-F]{2}",
                       lambda hex: HEX_MAP[hex.group(0)[1:].upper()[0]] +
                                   HEX_MAP[hex.group(0)[1:].upper()[1]],
                       symbol)
            return (new_symbol, [])
    else:
        if symbol == "<hex>":
            child_symbol, _ = children[0]
            return (symbol, [(HEX_MAP[child_symbol], [])])

    return (symbol, [to_binstr("", c) for c in children if children])

def gen_lv():
    length = random.randint(16, 16) # TODO probability distribution?
    bin_length = ["1" if length & (1 << i) else "0" for i in range(0, 9)]
    bin_value = [repr(random.randint(0,1)) for b in range(0, length*8)]
    return "".join(bin_length) + "".join(bin_value)

ETHERNET_FRAME_GRAMMAR = {
    DEFAULT_START_SYMBOL  : [("<ethernet-frame>", opts(post=to_binstr))],
    "<ethernet-frame>"    : ["<addr><vlan-tags><type-payload>"],
    "<addr>"              : ["<dst><src>"],
    "<dst>"               : ["<byte><byte><byte><byte><byte><byte>",
                             "<mef-multicast>"
                            ],
    "<mef-multicast>"     : ["x01x80xC2x00x00x00", "x01x80xC2x00x00x03",
                             "x01x80xC2x00x00x0E"
                            ],
    "<src>"               : ["<byte><byte><byte><byte><byte><byte>"],
    "<vlan-tags>"         : ["", "<q-tag><vlan-tags>", "<q-tag>"],
    "<q-tag>"             : ["<tpid><pcp><dei><vlan>"],
    "<tpid>"              : ["x81x00", "x88xA8"],
    "<pcp>"               : ["<bit><bit><bit>"],
    "<dei>"               : ["<bit>"],
    "<vlan>"              : ["<byte><bit><bit><bit><bit>"],
    "<type-payload>"      : ["<lldp-ethertype><lldp-payload>"],
    "<byte>"              : ["x<hex><hex>"],
    "<hex>"               : srange("0123456789ABCDEF"),
    "<bit>"               : ["0", "1"],
    "<lldp-ethertype>"    : ["x88xCC"],
    "<lldp-payload>"      : ["<lldp-chassiid-tlv><lldp-portid-tlv>" \
                             "<lldp-ttl-tlv><lldp-opt-tlvs><lldp-end-tlv>"],
    "<lldp-end-tlv>"      : ["x00x00"],
    "<lldp-chassiid-tlv>" : ["0000001<lldp-lv>"],
    "<lldp-portid-tlv>"   : ["0000010<lldp-lv>"],
    "<lldp-ttl-tlv>"      : ["0000011<lldp-lv>"],
    "<lldp-opt-tlvs>"     : ["", "<lldp-opt-tlv>",
                             "<lldp-opt-tlv><lldp-opt-tlvs>"
                            ],
    "<lldp-opt-tlv>"      : ["<lldp-portdesc-tlv>", "<lldp-sysname-tlv>",
                             "<lldp-sysdesc-tlv>", "<lldp-syscap-tlv>",
                             "<lldp-mgmtaddr-tlv>", "<lldp-res-tlv>",
                             "<lldp-custom-tlv>"
                            ],
    "<lldp-portdesc-tlv>" : ["0000100<lldp-lv>"],
    "<lldp-sysname-tlv>"  : ["0000101<lldp-lv>"],
    "<lldp-sysdesc-tlv>"  : ["0000110<lldp-lv>"],
    "<lldp-syscap-tlv>"   : ["0000111<lldp-lv>"],
    "<lldp-mgmtaddr-tlv>" : ["0001000<lldp-lv>"],
    "<lldp-res-tlv>"      : ["<bit><bit><bit><bit><bit><bit><bit><lldp-lv>"],
    "<lldp-custom-tlv>"   : ["1111111<lldp-lv>"],
    "<lldp-lv>"           : [("<byte>", opts(pre=gen_lv))],
}
