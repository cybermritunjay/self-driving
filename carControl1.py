import RPi.GPIO as GPIO
import time
class CarControls:
    def __init__(self):
        self.p=None
        self.servoPIN = 12
        self.currentAngle = 90
        print("initialization Complete")
        self.setup()
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servoPIN, GPIO.OUT)

        self.p = GPIO.PWM(self.servoPIN, 50) # GPIO 17 for PWM with 50Hz
        
        self.p.start(7)
        print("setup Complete")

    def left(self):
        self.currentAngle = self.currentAngle-10 if self.currentAngle > 70 else 70
        print(self.currentAngle)
        self.p.ChangeDutyCycle(2+(self.currentAngle/18))
        time.sleep(1)

    def right(self):
        self.currentAngle = self.currentAngle+10 if self.currentAngle < 110 else 110
        print(self.currentAngle)
        self.p.ChangeDutyCycle(2+(self.currentAngle/18))
        time.sleep(1)
    def reverse(self):
        pass
    def forward(self):
        pass
    def clean(self):
        self.p.stop()
        GPIO.cleanup()