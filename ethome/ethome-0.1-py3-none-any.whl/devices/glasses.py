from device import Device


class Glasses(Device):
    """A class for egocentric glasses recordings.

    Arguments:
        Device {[type]} -- [description]
    """

    attrs = [
        'System_Time',
        'Server_Time',
        'Eye_Frame_Number',
        'Scene Frame Number',
        'GazeBasePoint_L_X',
        'GazeBasePoint_L_Y',
        'GazeBasePoint_L_Z',
        'GazeDirection_L_X',
        'GazeDirection_L_Y',
        'GazeDirection_L_Z',
        'PupilDiameter_L_X',
        'PupilDiameter_L_Y',
        'PupilRadius_L',
        'PupilConfidence_L',
        'PointOfRegard_L_X',
        'PointOfRegard_L_Y',
        'GazeBasePoint_R_X',
        'GazeBasePoint_R_Y',
        'GazeBasePoint_R_Z',
        'GazeDirection_R_X',
        'GazeDirection_R_Y',
        'GazeDirection_R_Z',
        'PupilDiameter_R_X',
        'PupilDiameter_R_Y',
        'PupilRadius_R',
        'PupilConfidence_R',
        'PointOfRegard_R_X',
        'PointOfRegard_R_Y',
    ]

    def __init__(self, **kwargs):
        kwargs.update({"labels": self.attrs})
        super().__init__(**kwargs)

    @staticmethod
    def get_3D_gaze(directionL, directionR, L0, R0):
        failed = np.zeros(1, directionL.shape[1])
        w0 = (L0-R0).t
        u = directionL
        v = directionR

        ## Perpendicular distance method

        a = np.dot(u,u)
        b = np.dot(u,v)
        c = np.dot(v,v)
        d = np.dot(u,w0)
        e = np.dot(v,w0)

        t = (a * e - b * d) / (a * c - (b**2))
        s = (b * e - c * d) / (a * c - (b**2))

        P = np.concatenate([s, s, s], axis=-1) * u + L0.t
        Q = np.concatenate([t, t, t], axis=-1) * v + R0.t
        w = P - Q

        check = []
        lengthW = []
        for i in range(1, u.shape[1]):
            lengthW.append(np.linalg.norm(w[:,i]))
            check.append(np.dot(w[:,i]) / np.linalg.norm(w[:,i]), u[:,i])
        
        check = np.asanyarray(check)
        lengthW = np.asanyarray(lengthW)
        
        checkPerp = np.sum(abs(not np.isnan(check))) / np.sum(not np.isnan(check))
        if checkPerp > 1e-5:
            warnings.warn('3D calc failed')
            failed = np.ones(1, meanPQ.shape[1]) 

        meanWLength = np.mean(lengthW[not np.isnan(lengthW)])
        meanPQ = (P + Q) / 2
        return meanPQ, P, Q, failed