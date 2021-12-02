"""Creates vehicle classes"""
# Parent Class
class Vehicle:
    """Creates a vehicle class"""
    # static attribute
    wheels = 4

    # Constructor - defines user supplied attributes
    # 3 required attributes, 2 optional, 1 static (wheels)
    def __init__(self, make, model, color, year=2021, mileage=0):
        self.make= make
        self.model = model
        self.color = color
        self.year = year
        self.mileage = mileage

    def honk(self):
        """Prints honk"""
        print('HOOONK!')

    def drive(self, miles_driven):
        """Prints vroom"""
        print("VROOOM!")
        self.mileage = self.mileage + miles_driven


# Child Class, is more specific and inherits attributes and methods from the parent class
class Car(Vehicle):
    """Creates specific class of car"""
    def __init__(self, make, model, color, style, year=2021, mileage=0):
        # super() will inherit from the parent class
        super().__init__(make, model, color, year, mileage)

        #self.style is the only unique attribute
        self.style = style

# detect if the file is being imported in REPL or ran as a script

print('Running in a REPL or script')

# This condition will only be true if being ran as a script
if __name__ == '__main__':
    print("Running as a SCRIPT")
    