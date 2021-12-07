# Standard lib imports
import random
import re


# Local imports
from qwilfish.constants import DEFAULT_START_SYMBOL
from qwilfish.grammar import opts
from qwilfish.derivation_tree import all_terminals

# TODO fuzz by changing endianness of fields and/or bytes
# TODO fuzz by inserting wrong TLVs

HEX_MAP = {"0": "0000", "1": "0001", "2": "0010", "3": "0011",
           "4": "0100", "5": "0101", "6": "0110", "7": "0111",
           "8": "1000", "9": "1001", "A": "1010", "B": "1011",
           "C": "1100", "D": "1101", "E": "1110", "F": "1111"}

def srange(characters):
    return [c for c in characters]

def to_binstr(subtree, *args):
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

    return (symbol, [to_binstr(c, "") for c in children if children])

def fix_length(subtree, *args): # TODO make cleaner, avoid all_terminals
    symbol, children = subtree
    n_bits = len(all_terminals(subtree)) - 16 # 16 bits for type+length

    assert n_bits % 8 == 0

    length = int(n_bits/8)
    bin_length = ["1" if length & (1 << i) else "0" for i in range(8, -1, -1)]

    for i, c in enumerate(children):
        if c[0] == "<tlv-len>":
            children[i] = (children[i][0],
                           [("".join(bin_length), [])])

    return (symbol, children)

def gen_random_data():
    max_size = 255
    length = random.randint(1,255)*8
    bin_data = [str(random.randint(0,1)) for i in range(0, length)]

    return "".join(bin_data)

ETHERNET_FRAME_GRAMMAR = {
    DEFAULT_START_SYMBOL  : [("<ethernet-frame>", opts(post=to_binstr))],
    "<ethernet-frame>"    : ["<addr><vlan-tags><type-payload>"],
    "<addr>"              : ["<dst><src>"],
    "<dst>"               : [("<byte><byte><byte><byte><byte><byte>",
                              opts(prob=0.1)),
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
    "<random-data>"       : [("", opts(pre=gen_random_data))],
    "<lldp-ethertype>"    : ["x88xCC"],
    "<lldp-payload>"      : ["<lldp-tlv-chassiid><lldp-tlv-portid>" \
                             "<lldp-tlv-ttl><lldp-opt-tlvs><lldp-tlv-end>"],
    "<lldp-opt-tlvs>"     : ["", "<lldp-opt-tlv>",
                             "<lldp-opt-tlv><lldp-opt-tlvs>"
                            ],
    "<lldp-opt-tlv>"      : ["<lldp-tlv-portdesc>", "<lldp-tlv-sysname>",
                             "<lldp-tlv-sysdesc>", "<lldp-tlv-syscap>",
                             "<lldp-tlv-mgmtaddr>", "<lldp-tlv-custom>"
                            ],
    "<tlv-len>"           : ["<bit><byte>"],
    "<lldp-tlv-end>"      : ["x00x00"],
    "<lldp-tlv-chassiid>" : [("0000001<tlv-len><chassiid-subtype>"
                             "<chassiid-data>", opts(post=fix_length))],
    "<chassiid-subtype>"  : ["00000001", "00000010", "00000011", "00000100",
                             "00000101", "00000110", "00000111"],
    "<chassiid-data>"     : ["<random-data>"],
    "<lldp-tlv-portid>"   : [("0000010<tlv-len><portid-subtype><portid-data>",
                              opts(post=fix_length))],
    "<portid-subtype>"    : ["00000001", "00000010", "00000011", "00000100",
                             "00000101", "00000110", "00000111"],
    "<portid-data>"       : ["<random-data>"],
    "<lldp-tlv-ttl>"      : [("0000011<tlv-len><byte><byte>",
                              opts(post=fix_length))],
    #"<lldp-tlv-portdesc>" : [("0000100<tlv-len><chassiid-subtype><chassiid-data>", opts(post=fix_length))],
    #"<lldp-tlv-sysname>"  : [("0000101<tlv-len><chassiid-subtype><chassiid-data>", opts(post=fix_length))],
    #"<lldp-tlv-sysdesc>"  : [("0000110<tlv-len><chassiid-subtype><chassiid-data>", opts(post=fix_length))],
    #"<lldp-tlv-syscap>"   : [("0000111<tlv-len>", opts(post=fix_length))],
    #"<lldp-tlv-mgmtaddr>" : [("0001000<tlv-len>", opts(post=fix_length))],
    #"<lldp-tlv-custom>"   : [("1111111<tlv-len>", opts(post=fix_length))]
    "<lldp-tlv-portdesc>" : [""],
    "<lldp-tlv-sysname>"  : [""],
    "<lldp-tlv-sysdesc>"  : [""],
    "<lldp-tlv-syscap>"   : [""],
    "<lldp-tlv-mgmtaddr>" : [""],
    "<lldp-tlv-custom>"   : [""]
}
