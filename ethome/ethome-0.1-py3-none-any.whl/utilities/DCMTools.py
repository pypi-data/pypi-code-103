import numpy as np


def angle2dcm(r1, r2, r3, input_unit='rad', rotation_sequence='zyx'):

    if (len(r1) != len(r2)) or (len(r1) != len(r3)):
        raise ValueError("raise ValueError('Inputs are not of same dimensions')")

    angles = np.concatenate([r1, r2, r3], axis=-1)

    dcm = np.zeros(3, 3, angles.shape[0])
    cang = np.cos(angles)
    sang = np.sin(angles)

    rotation_sequence = rotation_sequence.lower()

    if rotation_sequence == "zyx":
        dcm[1, 1, :] = cang[:, 2] * cang[:, 1]
        dcm[1, 2, :] = cang[:, 2] * sang[:, 1]
        dcm[1, 3, :] = -sang[:, 2]
        dcm[2, 1, :] = sang[:, 3] * sang[:, 2] * cang[:, 1] - cang[:, 3] * sang[:, 1]
        dcm[2, 2, :] = sang[:, 3] * sang[:, 2] * sang[:, 1] + cang[:, 3] * cang[:, 1]
        dcm[2, 3, :] = sang[:, 3] * cang[:, 2]
        dcm[3, 1, :] = cang[:, 3] * sang[:, 2] * cang[:, 1] + sang[:, 3] * sang[:, 1]
        dcm[3, 2, :] = cang[:, 3] * sang[:, 2] * sang[:, 1] - sang[:, 3] * cang[:, 1]
        dcm[3, 3, :] = cang[:, 3] * cang[:, 2]

    elif rotation_sequence == "zyz":
        dcm[1, 1, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]
        dcm[1, 2, :] = sang[:, 1] * cang[:, 3] * cang[:, 2] + cang[:, 1] * sang[:, 3]
        dcm[1, 3, :] = -sang[:, 2] * cang[:, 3]  
        dcm[2, 1, :] = -cang[:, 1] * cang[:, 2] * sang[:, 3] - sang[:, 1] * cang[:, 3]                
        dcm[2, 2, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]
        dcm[2, 3, :] = sang[:, 2] * sang[:, 3]     
        dcm[3, 1, :] = cang[:, 1] * sang[:, 2]
        dcm[3, 2, :] = sang[:, 1] * sang[:, 2]  
        dcm[3, 3, :] = cang[:, 2]

    elif rotation_sequence == "zxy":
        dcm[1, 1, :] = cang[:, 3] * cang[:, 1] - sang[:, 2] * sang[:, 3] * sang[:, 1]
        dcm[1, 2, :] = cang[:, 3] * sang[:, 1] + sang[:, 2] * sang[:, 3] * cang[:, 1]
        dcm[1, 3, :] = -sang[:, 3] * cang[:, 2]
        dcm[2, 1, :] = -cang[:, 2] * sang[:, 1]
        dcm[2, 2, :] = cang[:, 2] * cang[:, 1]
        dcm[2, 3, :] = sang[:, 2]
        dcm[3, 1, :] = sang[:, 3] * cang[:, 1] + sang[:, 2] * cang[:, 3] * sang[:, 1]
        dcm[3, 2, :] = sang[:, 3] * sang[:, 1] - sang[:, 2] * cang[:, 3] * cang[:, 1]
        dcm[3, 3, :] = cang[:, 2] * cang[:, 3]

    elif rotation_sequence == "zxz":
        dcm[1, 1, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]
        dcm[1, 2, :] = cang[:, 1] * cang[:, 2] * sang[:, 3] + sang[:, 1] * cang[:, 3]                
        dcm[1, 3, :] = sang[:, 2] * sang[:, 3]     
        dcm[2, 1, :] = -sang[:, 1] * cang[:, 3] * cang[:, 2] - cang[:, 1] * sang[:, 3]
        dcm[2, 2, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]
        dcm[2, 3, :] = sang[:, 2] * cang[:, 3]  
        dcm[3, 1, :] = sang[:, 1] * sang[:, 2]  
        dcm[3, 2, :] = -cang[:, 1] * sang[:, 2]
        dcm[3, 3, :] = cang[:, 2]

    elif rotation_sequence == "yxz":
        dcm[1, 1, :] = cang[:, 1] * cang[:, 3] + sang[:, 2] * sang[:, 1] * sang[:, 3]
        dcm[1, 2, :] = cang[:, 2] * sang[:, 3]
        dcm[1, 3, :] = -sang[:, 1] * cang[:, 3] + sang[:, 2] * cang[:, 1] * sang[:, 3]
        dcm[2, 1, :] = -cang[:, 1] * sang[:, 3] + sang[:, 2] * sang[:, 1] * cang[:, 3]
        dcm[2, 2, :] = cang[:, 2] * cang[:, 3]
        dcm[2, 3, :] = sang[:, 1] * sang[:, 3] + sang[:, 2] * cang[:, 1] * cang[:, 3]        
        dcm[3, 1, :] = sang[:, 1] * cang[:, 2]
        dcm[3, 2, :] = -sang[:, 2]
        dcm[3, 3, :] = cang[:, 2] * cang[:, 1]

    elif rotation_sequence == "yxy":
        dcm[1, 1, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]
        dcm[1, 2, :] = sang[:, 2] * sang[:, 3]     
        dcm[1, 3, :] = -cang[:, 1] * cang[:, 2] * sang[:, 3] - sang[:, 1] * cang[:, 3]                
        dcm[2, 1, :] = sang[:, 1] * sang[:, 2]  
        dcm[2, 2, :] = cang[:, 2]
        dcm[2, 3, :] = cang[:, 1] * sang[:, 2]
        dcm[3, 1, :] = sang[:, 1] * cang[:, 3] * cang[:, 2] + cang[:, 1] * sang[:, 3]
        dcm[3, 2, :] = -sang[:, 2] * cang[:, 3]  
        dcm[3, 3, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]
            
    elif rotation_sequence == "yzx":
        dcm[1, 1, :] = cang[:, 1] * cang[:, 2]
        dcm[1, 2, :] = sang[:, 2]
        dcm[1, 3, :] = -sang[:, 1] * cang[:, 2]
        dcm[2, 1, :] = -cang[:, 3] * cang[:, 1] * sang[:, 2] + sang[:, 3] * sang[:, 1]
        dcm[2, 2, :] = cang[:, 2] * cang[:, 3]
        dcm[2, 3, :] = cang[:, 3] * sang[:, 1] * sang[:, 2] + sang[:, 3] * cang[:, 1]        
        dcm[3, 1, :] = sang[:, 3] * cang[:, 1] * sang[:, 2] + cang[:, 3] * sang[:, 1]
        dcm[3, 2, :] = -sang[:, 3] * cang[:, 2]
        dcm[3, 3, :] = -sang[:, 3] * sang[:, 1] * sang[:, 2] + cang[:, 3] * cang[:, 1]

    elif rotation_sequence == "yzy":
        dcm[1, 1, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]
        dcm[1, 2, :] = sang[:, 2] * cang[:, 3]  
        dcm[1, 3, :] = -sang[:, 1] * cang[:, 3] * cang[:, 2] - cang[:, 1] * sang[:, 3]
        dcm[2, 1, :] = -cang[:, 1] * sang[:, 2]
        dcm[2, 2, :] = cang[:, 2]
        dcm[2, 3, :] = sang[:, 1] * sang[:, 2]  
        dcm[3, 1, :] = cang[:, 1] * cang[:, 2] * sang[:, 3] + sang[:, 1] * cang[:, 3]                
        dcm[3, 2, :] = sang[:, 2] * sang[:, 3]     
        dcm[3, 3, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]

    elif rotation_sequence == "xyz":
        dcm[1, 1, :] = cang[:, 2] * cang[:, 3]
        dcm[1, 2, :] = sang[:, 1] * sang[:, 2] * cang[:, 3] + cang[:, 1] * sang[:, 3]
        dcm[1, 3, :] = -cang[:, 1] * sang[:, 2] * cang[:, 3] + sang[:, 1] * sang[:, 3]
        dcm[2, 1, :] = -cang[:, 2] * sang[:, 3]
        dcm[2, 2, :] = -sang[:, 1] * sang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]
        dcm[2, 3, :] = cang[:, 1] * sang[:, 2] * sang[:, 3] + sang[:, 1] * cang[:, 3]        
        dcm[3, 1, :] = sang[:, 2]
        dcm[3, 2, :] = -sang[:, 1] * cang[:, 2]
        dcm[3, 3, :] = cang[:, 1] * cang[:, 2]

    elif rotation_sequence == "xyx":
        dcm[1, 1, :] = cang[:, 2]
        dcm[1, 2, :] = sang[:, 1] * sang[:, 2]     
        dcm[1, 3, :] = -cang[:, 1] * sang[:, 2]
        dcm[2, 1, :] = sang[:, 2] * sang[:, 3]        
        dcm[2, 2, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]
        dcm[2, 3, :] = cang[:, 1] * cang[:, 2] * sang[:, 3] + sang[:, 1] * cang[:, 3]                
        dcm[3, 1, :] = sang[:, 2] * cang[:, 3]        
        dcm[3, 2, :] = -sang[:, 1] * cang[:, 3] * cang[:, 2] - cang[:, 1] * sang[:, 3]
        dcm[3, 3, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]

    elif rotation_sequence == "xzy":
        dcm[1, 1, :] = cang[:, 3] * cang[:, 2]
        dcm[1, 2, :] = cang[:, 1] * cang[:, 3] * sang[:, 2] + sang[:, 1] * sang[:, 3]
        dcm[1, 3, :] = sang[:, 1] * cang[:, 3] * sang[:, 2] - cang[:, 1] * sang[:, 3]
        dcm[2, 1, :] = -sang[:, 2]
        dcm[2, 2, :] = cang[:, 1] * cang[:, 2]
        dcm[2, 3, :] = sang[:, 1] * cang[:, 2]        
        dcm[3, 1, :] = sang[:, 3] * cang[:, 2]
        dcm[3, 2, :] = cang[:, 1] * sang[:, 2] * sang[:, 3] - sang[:, 1] * cang[:, 3]                
        dcm[3, 3, :] = sang[:, 1] * sang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]

    elif rotation_sequence == "xzx":
        dcm[1, 1, :] = cang[:, 2]
        dcm[1, 2, :] = cang[:, 1] * sang[:, 2]     
        dcm[1, 3, :] = sang[:, 1] * sang[:, 2]
        dcm[2, 1, :] = -sang[:, 2] * cang[:, 3]        
        dcm[2, 2, :] = cang[:, 1] * cang[:, 3] * cang[:, 2] - sang[:, 1] * sang[:, 3]
        dcm[2, 3, :] = sang[:, 1] * cang[:, 3] * cang[:, 2] + cang[:, 1] * sang[:, 3]
        dcm[3, 1, :] = sang[:, 2] * sang[:, 3]
        dcm[3, 2, :] = -cang[:, 1] * cang[:, 2] * sang[:, 3] - sang[:, 1] * cang[:, 3]                
        dcm[3, 3, :] = -sang[:, 1] * cang[:, 2] * sang[:, 3] + cang[:, 1] * cang[:, 3]

    else:
        raise ValueError("Unknown rotation type")

    return dcm


def dcm2angle(dcm, rotation_sequence="zyx", lim = "default"):

    rotation_sequence = rotation_sequence.lower()

    def threeaxisrot(r11, r12, r21, r31, r32, r11a, r12a):
        r1 = np.arctan2(r11, r12)
        r21[r21 < -1] = -1
        r21[r21 > 1] = 1
        r2 = np.arcsin(r21)
        r3 = np.arctan2(r31, r32)
        if lim == "zeror3":
            for i in np.argwhere(abs(r21) == 1.0):
                r1[i] = np.arctan2(r11a[i], r12a[i])
                r3[i] = 0
        return r1, r2, r3

    def twoaxisrot(r11, r12, r21, r31, r32, r11a, r12a):
        r1 = np.arctan2(r11, r12)
        r21[r21 < -1] = -1
        r21[r21 > 1] = 1
        r2 = np.arccos(r21)
        r3 = np.arctan2(r31, r32)
        if lim == "zeror3":
            for i in np.argwhere(abs(r21) == 1.0):
                r1[i] = np.arctan2(r11a[i], r12a[i])
                r3[i] = 0
        return r1, r2, r3

    if rotation_sequence == "zyx":
        r1, r2, r3 = threeaxisrot(
            dcm[1, 2, :],
            dcm[1, 1, :],
            -dcm[1, 3, :],
            dcm[2, 3, :],
            dcm[3, 3, :],
            -dcm[2, 1, :],
            dcm[2, 2, :]
        )

    elif rotation_sequence == "zyz":
        r1, r2, r3 = twoaxisrot(
            dcm[3, 2, :],
            dcm[3, 1, :],
            dcm[3, 3, :],
            dcm[2, 3, :],
            -dcm[1, 3, :],
            -dcm[2, 1, :],
            dcm[2, 2, :]
        )

    elif rotation_sequence == "zxy":
        r1, r2, r3 = threeaxisrot(
            -dcm[2, 1, :],
            dcm[2, 2, :],
            dcm[2, 3, :],
            -dcm[1, 3, :],
            dcm[3, 3, :],
            dcm[1, 2, :],
            dcm[1, 1, :]
        )

    elif rotation_sequence == "zxz":
        r1, r2, r3 = twoaxisrot(
            dcm[3, 1, :],
            -dcm[3, 2, :],
            dcm[3, 3, :],
            dcm[1, 3, :],
            dcm[2, 3, :],
            dcm[1, 2, :],
            dcm[1, 1, :]
        )

    elif rotation_sequence == "yxz":
        r1, r2, r3 = threeaxisrot(
            dcm[3, 1, :],
            dcm[3, 3, :],
            -dcm[3, 2, :],
            dcm[1, 2, :],
            dcm[2, 2, :],
            -dcm[1, 3, :],
            dcm[1, 1, :]
        )

    elif rotation_sequence == "yxy": 
        r1, r2, r3 = twoaxisrot(
            dcm[2, 1, :],
            dcm[2, 3, :],
            dcm[2, 2, :],
            dcm[1, 2, :],
            -dcm[3, 2, :],
            -dcm[1, 3, :],
            dcm[1, 1, :]
        )

    elif rotation_sequence == "yzx":
        r1, r2, r3 = threeaxisrot(
            -dcm[1, 3, :],
            dcm[1, 1, :],
            dcm[1, 2, :],
            -dcm[3, 2, :],
            dcm[2, 2, :],
            dcm[3, 1, :],
            dcm[3, 3, :]
        )

    elif rotation_sequence == "yzy":
        r1, r2, r3 = twoaxisrot(
            dcm[2, 3, :],
            -dcm[2, 1, :],
            dcm[2, 2, :],
            dcm[3, 2, :],
            dcm[1, 2, :],
            dcm[3, 1, :],
            dcm[3, 3, :]
        )

    elif rotation_sequence == "xyz":
        r1, r2, r3 = threeaxisrot(
            -dcm[3, 2, :],
            dcm[3, 3, :],
            dcm[3, 1, :],
            -dcm[2, 1, :],
            dcm[1, 1, :],
            dcm[2, 3, :],
            dcm[2, 2, :]
        )

    elif rotation_sequence == "xyx":
        r1, r2, r3 = twoaxisrot(
            dcm[1, 2, :],
            -dcm[1, 3, :],
            dcm[1, 1, :],
            dcm[2, 1, :],
            dcm[3, 1, :],
            dcm[2, 3, :],
            dcm[2, 2, :]
        )

    elif rotation_sequence == "xzy":
        r1, r2, r3 = threeaxisrot(
            dcm[2, 3, :],
            dcm[2, 2, :],
            -dcm[2, 1, :],
            dcm[3, 1, :],
            dcm[1, 1, :],
            -dcm[3, 2, :],
            dcm[3, 3, :]
        )

    elif rotation_sequence == "xzx":
        r1, r2, r3 = twoaxisrot(
            dcm[1, 3, :],
            dcm[1, 2, :],
            dcm[1, 1, :],
            dcm[3, 1, :],
            -dcm[2, 1, :],
            -dcm[3, 2, :],
            dcm[3, 3, :]
        )
    else:
        raise ValueError("Unknown rotation")

    return r1, r2, r3
