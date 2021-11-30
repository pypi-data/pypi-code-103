
def MediumMotor_Rotations(Port, Speed, Rotations, BrakeAtEnd):
    if BrakeAtEnd == True:
        BaE = "Brake"
    else:
        BaE = "Coast"
    out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Rotations: "+ Rotations + " | Brake_At_End: " + BaE)

    return out 

def MediumMotor_Degrees(Port, Speed, Degrees, BrakeAtEnd):
    if BrakeAtEnd == True:
        BaE = "Brake"
    else:
        BaE = "Coast"
    out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Degrees: "+ Degrees + " | Brake_At_End: " + BaE)

    return out


def MediumMotor_Time(Port, Speed, Seconds, BrakeAtEnd):
    if BrakeAtEnd == True:
        BaE = "Brake"
    else:
        BaE = "Coast"
    out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Seconds: "+ Seconds + " | Brake_At_End: " + BaE)

    return out


def MediumMotor_Unlimited(Port, Speed):
    out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed)

    return out


def MediumMotor_Stop(Port: str, BrakeAtEnd: bool) -> str:
    if BrakeAtEnd == True:
        BaE = "Brake"
    else:
        BaE = "Coast"

    out = ("MediumMotor.Stop MotorPort: " + Port + " | Brake_At_End: " + BaE)

    return out

