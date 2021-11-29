class BMICalculate:
    def __init__(self,age,weight,height):
        self.age = age
        self.weight = weight
        self.height = height
        self.bmi = 0

    def calculate_bmi(self):
        '''
        Calculate BMI
        :return:
        '''

        self.bmi = self.weight / (self.height/100 * self.height/100) * 0.98

        return self.bmi

    def conclusion(self):
        if self.bmi < 18.5:
            print("You are under weight")
        elif self.bmi < 34.9:
            print("1st Level over weight")
        else:
            print("This is ok")

