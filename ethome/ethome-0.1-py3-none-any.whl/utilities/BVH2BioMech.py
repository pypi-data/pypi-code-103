import h5py
import numpy as np

from .deSwitch import deSwitch
from .DCMTools import angle2dcm
from .DCMTools import dcm2angle


def BVH2BioMech(suit):

    data = suit["Data"][()]
    dim = data.shape[1]

    r2a = 180 / np.pi #radians to angles
    a2r = np.pi / 180 #angles to radians 

    for k in range(0, 66, 3): # suit dimensions, skip by XYZ to the next 
        if k <= 3 and dim == 66:
            continue
        angles = np.deg2rad(data[:, k:k + 2])
        dcm = angle2dcm(angles[:, 1], angles[:, 2], angles[:, 3], 'ZXY')

        if k == 60:
            ry, rx, rz = dcm2angle(dcm, 'YXZ')
            section = "Neck"
            Flexion = np.rad2deg(rx)
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Abduction = np.rad2deg(rz)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)
            Torsion = np.rad2deg(ry)
            Torsion_source = suit.create_dataset(f"BioMechData/{section}/Torsion", data=Torsion)
            virt_Torsion = h5py.VirtualSource(Torsion_source)

            AllLabels = ["Flexion", "Abduction", "Torsion"]
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Abduction
            layout[:, 2] = virt_Torsion
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)
        
        elif k in [30, 33]:
            rx, rz, ry = dcm2angle(dcm, 'XZY')
            if k == 30:
                section = "MidSpine"
            else:
                section = "UpSpine"

            Flexion = np.rad2deg(rx)
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Abduction = np.rad2deg(rz)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)
            Torsion = np.rad2deg(ry)
            Torsion_source = suit.create_dataset(f"BioMechData/{section}/Torsion", data=Torsion)
            virt_Torsion = h5py.VirtualSource(Torsion_source)

            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            AllLabels = ["Flexion", "Abduction", "Torsion"]
            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Abduction
            layout[:, 2] = virt_Torsion
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [6, 18]:
            rx, rz, ry = dcm2angle(dcm, 'XZY')
            
            Flexion = np.rad2deg(rx)

            if k == 6:
                section = "LeftHip"
                Abduction = np.rad2deg(-rz)
                InternalRot = np.rad2deg(-ry)
            else:
                section = "RightHip"
                Abduction = np.rad2deg(rz)
                InternalRot = np.rad2deg(ry)
            
            AllLabels = ["Flexion", "Abduction", "Internal Rotation"]
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)
            InternalRot_source = suit.create_dataset(f"BioMechData/{section}/InternalRot", data=InternalRot)
            virt_InternalRot = h5py.VirtualSource(InternalRot_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Abduction
            layout[:, 2] = virt_InternalRot
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [9, 21]:
            [rx, rz, ry] = dcm2angle(dcm, 'XZY')
            Flexion = np.rad2deg(rx)

            if k == 9:
                section = "LeftKnee"
                Abduction = np.rad2deg(-rz)
                AxialRot = np.rad2deg(-ry)
            else:
                section = "RightKnee"
                Abduction = np.rad2deg(rz)
                AxialRot = np.rad2deg(ry)

            AllLabels = ["Flexion", "Abduction", "Axial Rotation"]
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)
            AxialRot_source = suit.create_dataset(f"BioMechData/{section}/AxialRot", data=AxialRot)
            virt_AxialRot = h5py.VirtualSource(AxialRot_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Abduction
            layout[:, 2] = virt_AxialRot
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [12, 24]:
            rx, rz, ry = dcm2angle(dcm, 'XZY')
            Flexion = np.rad2deg(rx)

            if k == 12:
                section = "LeftAnkle"
                Inversion = np.rad2deg(-rz)
                InternalRot = np.rad2deg(-ry)
            else:
                section = "RightAnkle"
                Inversion = np.rad2deg(rz)
                InternalRot = np.rad2deg(ry)

            AllLabels = ["Flexion", "Inversion", "Internal Rotation"]
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Inversion_source = suit.create_dataset(f"BioMechData/{section}/Inversion", data=Inversion)
            virt_Inversion = h5py.VirtualSource(Inversion_source)
            InternalRot_source = suit.create_dataset(f"BioMechData/{section}/InternalRot", data=InternalRot)
            virt_InternalRot = h5py.VirtualSource(InternalRot_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Inversion
            layout[:, 2] = virt_InternalRot
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [36, 48]:
            ry, rz, rx = dcm2angle(dcm, 'YZX')

            if k == 36:
                section = "LeftClavicle"
                Protraction = np.rad2deg(-ry)
                Elevation = np.rad2deg(-rz)
            else:
                section = "RightClavicle"
                Protraction = np.rad2deg(ry)
                Elevation = np.rad2deg(rz)

            AxialRot = np.rad2deg(rx)

            AllLabels = ["Protraction", "Elevation", "Axial Rotation"]
            Protraction_source = suit.create_dataset(f"BioMechData/{section}/Protraction", data=Protraction)
            virt_Protraction = h5py.VirtualSource(Protraction_source)
            Elevation_source = suit.create_dataset(f"BioMechData/{section}/Elevation", data=Elevation)
            virt_Elevation = h5py.VirtualSource(Elevation_source)
            AxialRot_source = suit.create_dataset(f"BioMechData/{section}/AxialRot", data=AxialRot)
            virt_AxialRot = h5py.VirtualSource(AxialRot_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Protraction.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Protraction
            layout[:, 1] = virt_Elevation
            layout[:, 2] = virt_AxialRot
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [39, 51]:
            ry1, rz, ry2 = dcm2angle(dcm, 'YZY')
            Direction = np.rad2deg(ry1)
            ix = Direction > 0
            Direction[ix] = Direction[ix] - 180
            ix = ix or Direction == 0
            Direction[not ix] = Direction[not ix] + 180
            Direction = deSwitch(Direction, 'deg')
            Elevation = np.rad2deg(-rz)
            AxialRot = deSwitch((ry1 + ry2) * r2a, 'deg')

            if k == 39:
                section = "LeftShoulder"
                Direction = -(Direction + 180)
                AxialRot = -AxialRot
            else:
                section = "RightShoulder"

            AllLabels = ["Direction", "Elevation", "Axial Rotation"]
            Direction_source = suit.create_dataset(f"BioMechData/{section}/Direction", data=Direction)
            virt_Direction = h5py.VirtualSource(Direction_source)
            Elevation_source = suit.create_dataset(f"BioMechData/{section}/Elevation", data=Elevation)
            virt_Elevation = h5py.VirtualSource(Elevation_source)
            AxialRot_source = suit.create_dataset(f"BioMechData/{section}/AxialRot", data=AxialRot)
            virt_AxialRot = h5py.VirtualSource(AxialRot_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Direction.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Direction
            layout[:, 1] = virt_Elevation
            layout[:, 2] = virt_AxialRot
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [42, 54]:
            rx, rz, ry = dcm2angle(dcm, 'XZY')
            Flexion = np.rad2deg(-rx)

            if k == 42:
                section = "LeftElbow"
                Pronation = np.rad2deg(-ry)
                Abduction = np.rad2deg(-rz)
            else:
                section = "RightElbow"
                Pronation = np.rad2deg(ry)
                Abduction = np.rad2deg(rz)

            AllLabels = ["Flexion", "Pronation", "Abduction (should be 0)"]
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Pronation_source = suit.create_dataset(f"BioMechData/{section}/Pronation", data=Pronation)
            virt_Pronation = h5py.VirtualSource(Pronation_source)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Pronation
            layout[:, 2] = virt_Abduction
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)

        elif k in [45, 57]:
            # NOT WORKING PROPERLY - NEED TO DEFINE ORDER
            rz, rx, ry = dcm2angle(dcm, 'ZXY')

            if k == 45:
                section = "LeftWrist"
                Flexion = np.rad2deg(-rz)
                Abduction = np.rad2deg(rx)
                Pronation = np.rad2deg(-ry)
            else:
                section = "RightWrist"
                Flexion = np.rad2deg(rz)
                Abduction = np.rad2deg(rx)
                Pronation = np.rad2deg(ry)

            AllLabels = ["Flexion", "Abduction", "Pronation (should be 0)"]
            Flexion_source = suit.create_dataset(f"BioMechData/{section}/Flexion", data=Flexion)
            virt_Flexion = h5py.VirtualSource(Flexion_source)
            Abduction_source = suit.create_dataset(f"BioMechData/{section}/Abduction", data=Abduction)
            virt_Abduction = h5py.VirtualSource(Abduction_source)
            Pronation_source = suit.create_dataset(f"BioMechData/{section}/Pronation", data=Pronation)
            virt_Pronation = h5py.VirtualSource(Pronation_source)

            suit.create_dataset(f"BioMechData/{section}/AllLabels", data=np.array(AllLabels, dtype='S'))
            layout = h5py.VirtualLayout(shape=Flexion.shape + (3, ), dtype=np.float)
            layout[:, 0] = virt_Flexion
            layout[:, 1] = virt_Abduction
            layout[:, 2] = virt_Pronation
            suit.create_virtual_dataset(f"BioMechData/{section}/All", layout)
        else:
            ry, rz, rx = dcm2angle(dcm, 'YZX')
