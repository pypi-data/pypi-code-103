
class MediumMotor():
    def Rotations(Port: str, Speed: float, Rotations: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + str(Speed) + " | Rotations: "+ str(Rotations) + " | Brake_At_End: " + str(BaE))

        return out 

    def Degrees(Port: str, Speed: float, Degrees: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + str(Speed) + " | Degrees: "+ str(Degrees) + " | Brake_At_End: " + str(BaE))

        return out


    def Time(Port: str, Speed: float, Seconds: float, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + str(Speed) + " | Seconds: "+ str(Seconds) + " | Brake_At_End: " + str(BaE))

        return out


    def Unlimited(Port: str, Speed: float) -> str:
        out = ("MediumMotor.Stop MotorPort: " + Port + " | Speed: " + str(Speed))

        return out


    def Stop(Port: str, BrakeAtEnd: bool) -> str:
        if BrakeAtEnd == True:
            BaE = "Brake"
        else:
            BaE = "Coast"

        out = ("MediumMotor.Stop MotorPort: " + Port + " | Brake_At_End: " + str(BaE))

        return out



