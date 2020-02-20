from carControl1 import CarControls

car = CarControls()

try:
    while True:
        inp = int(input("inter Move"))
        if inp == 3:
            print(inp)
            car.left()
        elif inp == 4:
            print(inp)
            car.right()
except KeyboardInterrupt:
    car.clean()