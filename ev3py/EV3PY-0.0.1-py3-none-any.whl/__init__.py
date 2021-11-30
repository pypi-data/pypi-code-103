
class MediumMotor():
    def MediumMotor_Rotations(Port: str, Speed: float, Rotations: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Rotations: "+ Rotations + " | Brake_At_End: " + BaE)

        return out 

    def MediumMotor_Degrees(Port: str, Speed: float, Degrees: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Degrees: "+ Degrees + " | Brake_At_End: " + BaE)

        return out


    def MediumMotor_Time(Port: str, Speed: float, Seconds: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed + " | Seconds: "+ Seconds + " | Brake_At_End: " + BaE)

        return out


    def MediumMotor_Unlimited(Port: str, Speed: float) -> str:
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + Speed)

        return out


    def MediumMotor_Stop(Port: str, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"

        out = ("MediumMotor.Stop MotorPort: " + Port + " | Brake_At_End: " + BaE)

        return out



