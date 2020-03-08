from __future__ import division
import time
import RPi.GPIO as GPIO

class CarControls:
    def __init__(self):
        self.blockControls=False
        self.currentAngle = 90
        self.forwardSpeed = 0
        self.backwardSpeed = 0
        self.lightsOn = False
        self.servo = None
        self.forward = None
        self.backward = None
        self.speed50 = False

        self.servoPIN = 13

        self.forwardPin = 26
        self.backwardPin = 20

        self.frontTrig = 18
        self.frontEcho = 17

        self.backTrig = 23
        self.backEcho = 22

        self.horn = 27
        self.frontLights = 15
        self.backLights = 5
        print("initialization Complete")

        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.frontEcho, GPIO.OUT)
        GPIO.setup(self.frontTrig, GPIO.IN)
        self.distanceFront()
        print("Front Ultrasonic Setup Successfull")
        GPIO.setup(self.backEcho, GPIO.OUT)
        GPIO.setup(self.backTrig, GPIO.IN)
        self.distanceBack()
        print("Back Ultrasonic Setup Successfull")

        GPIO.setup(self.forwardPin, GPIO.OUT)
        self.forward = GPIO.PWM(self.forwardPin, 100)
        self.forward.start(0)

        GPIO.setup(self.backwardPin, GPIO.OUT)
        self.backward = GPIO.PWM(self.backwardPin, 100)
        self.backward.start(0)
        self.stop()
        print("Main Motor Setup Successfull")

        self.servo.start(7)
        self.servo.ChangeDutyCycle(7)
        time.sleep(2)
        self.servo.ChangeDutyCycle(0)
        print("Servo Setup Successfull")

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

    def right(self):
        if self.blockControls:
            return  
        if self.currentAngle > 60:
            self.blockControls = True
            self.currentAngle -= -5
            print("currentAngle=", self.currentAngle)

            GPIO.output(self.servoPIN, True)
            self.servo.ChangeDutyCycle(2+(self.currentAngle/18))

            time.sleep(0.1)

            GPIO.output(self.servoPIN, False)
            self.servo.ChangeDutyCycle(0)
            self.blockControls = False

    def left(self):
        if self.blockControls:
            return
        if self.currentAngle < 120:
            self.blockControls = True
            self.currentAngle += 5
            print("currentAngle=", self.currentAngle)

            GPIO.output(self.servoPIN, True)
            self.servo.ChangeDutyCycle(2+(self.currentAngle/18))

            time.sleep(0.1)

            GPIO.output(self.servoPIN, False)
            self.servo.ChangeDutyCycle(0)
            self.blockControls = False

    def reverse(self):
        if self.blockControls:
            return
        self.backwardSpeed = self.backwardSpeed + \
            25 if self.backwardSpeed < 100 else 100
        self.forwardSpeed = 0

        GPIO.output(self.forwardPin, GPIO.LOW)
        self.forward.ChangeDutyCycle(self.forwardSpeed)

        GPIO.output(self.backwardPin, GPIO.HIGH)
        self.backward.ChangeDutyCycle(self.backwardSpeed)

        print("Moving Back")

    def goForward(self):
        if self.blockControls:
            return
        self.forwardSpeed = self.forwardSpeed+25 if self.forwardSpeed < 100 else 100
        self.backwardSpeed = 0
        if self.speed50:
            self.forwardSpeed = 50
        GPIO.output(self.backwardPin, GPIO.LOW)
        self.backward.ChangeDutyCycle(self.backwardSpeed)

        GPIO.output(self.forwardPin, GPIO.HIGH)
        self.forward.ChangeDutyCycle(self.forwardSpeed)

        print("Moving Forward")

    def stop(self):
        self.backwardSpeed = 0
        self.forwardSpeed = 0

        self.backward.ChangeDutyCycle(self.backwardSpeed)
        GPIO.output(self.backwardPin, GPIO.LOW)

        self.forward.ChangeDutyCycle(self.forwardSpeed)
        GPIO.output(self.forwardPin, GPIO.LOW)

        print("stop")

    def blowHorn(self):
        GPIO.output(self.horn, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.horn, GPIO.LOW)
        print("Horn")

    def lights(self):
        if not self.lightsOn:
            GPIO.output(self.frontLights, GPIO.HIGH)
            GPIO.output(self.backLights, GPIO.HIGH)
            self.lightsOn = True
        else:
            GPIO.output(self.frontLights, GPIO.LOW)
            GPIO.output(self.backLights, GPIO.LOW)
            self.lightsOn = False

    def stablizeTurn(self, angle):
        if self.blockControls:
            return
        if angle > 60 or angle < 120:
            if abs(self.currentAngle - angle) >= 5:
                self.blockControls = True
                self.currentAngle = angle
                print("currentAngle=", self.currentAngle)
                GPIO.output(self.servoPIN, True)
                self.servo.ChangeDutyCycle(2+(self.currentAngle/18))
                time.sleep(0.1)
                GPIO.output(self.servoPIN, False)
                self.servo.ChangeDutyCycle(0)
                self.blockControls = False

    def clean(self):
        self.servo.stop()
        self.forward.stop()
        self.backward.stop()
        GPIO.cleanup()

    def uTurn(self):
        pass
        """Turn full Left Then Stright """