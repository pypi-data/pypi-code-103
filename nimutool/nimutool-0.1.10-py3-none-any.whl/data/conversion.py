import math
from nimutool.canbus.can_message import ProcessedCanDataBlock, ParsedCanMessage


def rad2deg(x):
    return x * (180 / math.pi)


def rad2dph(x):
    return (x * (180 / math.pi)) * 3600


def acc2g(x):
    return x / 9.81


def acc2mg(x):
    return x / (9.81 / 1e3)


def acc2ug(x):
    return x / (9.81 / 1e6)


def calculate_rpy_if_possible(processed_block: ProcessedCanDataBlock):
    for nodeid in processed_block.get_nodeids():
        dcm = []
        if processed_block.has_signal(nodeid, "dcm11") and processed_block.has_signal(nodeid, "dcm21") and processed_block.has_signal(nodeid, "dcm31"):
            dcm1 = processed_block.get_message(nodeid, "dcm11").data
            dcm2 = processed_block.get_message(nodeid, "dcm21").data
            dcm3 = processed_block.get_message(nodeid, "dcm31").data
            dcm.append(dcm1)
            dcm.append(dcm2)
            dcm.append(dcm3)
            # Titterton, Strapdown Inertial Navigation Technology
            roll = math.degrees(math.atan2(dcm[2][1], dcm[2][2]))
            pitch = math.degrees(math.asin(-dcm[2][0]))
            yaw = math.degrees(math.atan2(dcm[1][0], dcm[0][0]))
            vals = [roll, pitch, yaw]
            processed_block.add(ParsedCanMessage(nodeid, ['roll', 'pitch', 'yaw'], vals, (f'{v:.4f}' for v in vals)))
            # print(f'roll {roll:4.2f}, pitch {pitch:4.2f}, yaw {yaw:4.2f}')
            # print(f'{dcm[0][0]:6.3f} {dcm[0][1]:6.3f} {dcm[0][2]:6.3f}')
            # print(f'{dcm[1][0]:6.3f} {dcm[1][1]:6.3f} {dcm[1][2]:6.3f}')
            # print(f'{dcm[2][0]:6.3f} {dcm[2][1]:6.3f} {dcm[2][2]:6.3f}')
