from __future__ import division
import RPi.GPIO as GPIO
import time


class CarControls:
    def __init__(self):
        self.p = None
        self.servoPIN = 12
        self.currentAngle = 90
        self.Forward = 26
        self.Backward =20
        self.sleeptime = 1
        self.frontTrig=17
        self.frontEcho=18
        self.backTrig=22
        self.backEcho=23
        print("initialization Complete")
        self.setup()
        

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.frontEcho, GPIO.OUT)
        GPIO.setup(self.frontTrig, GPIO.IN)
        GPIO.setup(self.backEcho, GPIO.OUT)
        GPIO.setup(self.backTrig, GPIO.IN)
        GPIO.setup(self.servoPIN, GPIO.OUT)
        GPIO.setup(self.Forward, GPIO.OUT)
        GPIO.setup(self.Backward, GPIO.OUT)
        self.p = GPIO.PWM(self.servoPIN, 50)  # GPIO 17 for PWM with 50Hz
        GPIO.output(self.Backward, GPIO.LOW)
        GPIO.output(self.Forward, GPIO.LOW)
        self.p.start(7)
        self.p.ChangeDutyCycle(7)
        time.sleep(2)
        self.p.ChangeDutyCycle(0)

        print("setup Complete")
    def distanceFront(self):
        GPIO.output(self.frontTrig, True)    
        time.sleep(0.00001)
        GPIO.output(self.frontTrig, False)
        StartTime = time.time()
        StopTime = time.time()
        # save StartTime
        while GPIO.input(self.frontEcho) == 0:
            StartTime = time.time()
        while GPIO.input(self.frontEcho) == 1:
            StopTime = time.time()    
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed * 34300) / 2
        return distance
    def distanceBack(self):
        GPIO.output(self.backTrig, True)    
        time.sleep(0.00001)
        GPIO.output(self.backTrig, False)
        StartTime = time.time()
        StopTime = time.time()
        # save StartTime
        while GPIO.input(self.backEcho) == 0:
            StartTime = time.time()
        while GPIO.input(self.backEcho) == 1:
            StopTime = time.time()    
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed * 34300) / 2
        return distance
    def left(self):
        self.currentAngle = self.currentAngle-5 if self.currentAngle >= 70 else 70
        print("currentAngle=",self.currentAngle)
        GPIO.output(self.servoPIN,True)
        self.p.ChangeDutyCycle(2+(self.currentAngle/18))
        time.sleep(0.1)
        GPIO.output(self.servoPIN,False)
        self.p.ChangeDutyCycle(0)

    def right(self):
        self.currentAngle = self.currentAngle+5 if self.currentAngle <= 110 else 110
        print("currentAngle=",self.currentAngle)
        GPIO.output(self.servoPIN,True)
        self.p.ChangeDutyCycle(2+(self.currentAngle/18))
        time.sleep(0.1)
        GPIO.output(self.servoPIN,False)
        self.p.ChangeDutyCycle(0)

    def reverse(self):
        GPIO.output(self.Forward, GPIO.LOW)
        GPIO.output(self.Backward, GPIO.HIGH)
        print("Moving Back")
        time.sleep(2)
        #GPIO.output(self.Backward, GPIO.LOW)

    def forward(self):
        GPIO.output(self.Backward, GPIO.LOW)
        GPIO.output(self.Forward, GPIO.HIGH)
        print("Moving Forward")
        time.sleep(2)
        #GPIO.output(self.Forward, GPIO.LOW)
    def stop(self):
        GPIO.output(self.Forward,GPIO.LOW)
        GPIO.output(self.Backward,GPIO.LOW)
        print("stop")

    def stablizeTurn(self,angle):
        if angle >=70 or angle<=110:
            if abs(self.currentAngle -angle) >=5:  
                self.currentAngle = angle
                print("currentAngle=",self.currentAngle)
                GPIO.output(self.servoPIN,True)
                self.p.ChangeDutyCycle(2+(self.currentAngle/18))
                time.sleep(0.1)
                GPIO.output(self.servoPIN,False)
                self.p.ChangeDutyCycle(0)
    def clean(self):
        self.p.stop()
        GPIO.cleanup()
