class Electric_Car:

    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.battery = Battery()
        
    def describe_car(self):    
        Lists = [self.make, self.model, self.year]
        for list in Lists:
            print(list)

class Battery:
    def __init__(self, battery_size=40):
        # Asegurate de que el nombre sea el mismo en ambos lados
        self.battery_size = battery_size 

    def describe_battery(self):
        # Ahora sí, self.battery_size existe
        print(f"This car has a {self.battery_size}-kwh battery.")

    def upgrade_battery(self):
        if self.battery_size < 65:
            self.battery_size = 65
            print(f"This car has a {self.battery_size}-kwh battery.")
        else:
            print(f"This car has a {self.battery_size}-kwh battery.")

