""""
------NAME----------PIN-----PHY------RPi
 1.)Servo Motor---> 5V   => x________x
                    GND  => 34_______GND
                    DATA => 33_______12
 2.)Main Motor ---> Pin1 => 37_______26
                    Pin2 => 38_______20
                    GND  => 39_______GND
 3.)Front Light---> DATA => 10_______15
                    GND  => 9________GND
 4.)Back Lightc---> DATA => 29_______5
                    GND  => 30_______GND
 5.)Horn----------> DATA => 13_______27
                    GND  => 14_______GND
 6.)Ultrasonic F--> VCC  => 1________5V
                    TRIG => 15_______22
                    ECHO => 16_______23
                    GND  => 20_______GND
 7.)Ultrasonic B--> VCC  => 2________5V
                    TRIG => 11_______17
                    ECHO => 12_______18
                    GND  => 6________GND

"""
import time
import RPi.GPIO as GPIO

#horn
horn= 27
#front Light
frontLight=15
#backLight
backLight=5
#front Ultrasonic
usFrontTrig=22
usFrontEcho =23
#back Ultrasonic 
usBackTrig=17
usBackEcho =18
#main Motor
motor1 =26
motor2=20
#servo
servo =12

GPIO.setmode(GPIO.BCM)
GPIO.setup(usBackTrig, GPIO.IN)
GPIO.setup(usBackEcho, GPIO.OUT)
GPIO.setup(usFrontTrig, GPIO.IN)
GPIO.setup(usFrontEcho, GPIO.OUT)
GPIO.setup(horn, GPIO.OUT)
GPIO.setup(frontLight, GPIO.OUT)
GPIO.setup(backLight, GPIO.OUT)
GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)
GPIO.setup(servo, GPIO.OUT)
p = GPIO.PWM(servo, 50) 
p.start(7)

def hornCheck():
    GPIO.output(horn, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(horn, GPIO.LOW)

def frontLightCheck():
    GPIO.output(frontLight, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(frontLight, GPIO.LOW)

def backLightCheck():
    GPIO.output(backLight, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(backLight, GPIO.LOW)

def usFrontCheck():
    GPIO.output(usFrontTrig, True)    
    time.sleep(0.00001)
    GPIO.output(usFrontTrig, False)
    StartTime = time.time()
    StopTime = time.time()
        # save StartTime
    while GPIO.input(usFrontEcho) == 0:
        StartTime = time.time()
    while GPIO.input(usFrontEcho) == 1:
        StopTime = time.time()    
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    print("distance Front= ",distance)

def usBackCheck():
    GPIO.output(usBackTrig, True)    
    time.sleep(0.00001)
    GPIO.output(usBackTrig, False)
    StartTime = time.time()
    StopTime = time.time()
        # save StartTime
    while GPIO.input(usBackEcho) == 0:
        StartTime = time.time()
    while GPIO.input(usBackEcho) == 1:
        StopTime = time.time()    
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    print("distance Back= ",distance)

def motorCheck():
    GPIO.output(motor1, GPIO.HIGH)
    GPIO.output(motor2, GPIO.LOW)
    time.sleep(3)
    GPIO.output(motor2, GPIO.HIGH)
    GPIO.output(motor1, GPIO.LOW)
    time.sleep(3)
    GPIO.output(motor1, GPIO.LOW)
    GPIO.output(motor2, GPIO.LOW)

def servoCheck():
    GPIO.output(servo,True)
    p.ChangeDutyCycle(2)
    time.sleep(0.1)
    p.ChangeDutyCycle(12)
    time.sleep(0.1)
    GPIO.output(servo,False)

try:
    choice = int(input("Press 1 to run Automated Test or 2 for manual test"))
    if choice == 1:
        print("Checking Horn")
        hornCheck()
        print("Checking Front Lights")
        frontLightCheck()
        print("Checking Back Lights")
        backLightCheck()
        print("Checking Main Motor")
        motorCheck()
        print("Checking Servo")
        servoCheck()
        print("Checking Front Ultrasonic")
        usFrontCheck()
        time.sleep(0.5)
        usFrontCheck()
        time.sleep(0.5)
        usFrontCheck()
        time.sleep(0.5)
        usFrontCheck()
        time.sleep(0.5)
        usFrontCheck()
        print("Checking Back Ultrasonic")
        usBackCheck()
        time.sleep(0.5)
        usBackCheck()
        time.sleep(0.5)
        usBackCheck()
        time.sleep(0.5)
        usBackCheck()
        time.sleep(0.5)
        usBackCheck()
        time.sleep(0.5)
    elif choice == 2:
        while True:
            inp = int(input('Enter 1 for Horn \n Enter 2 for Front Lights \nEnter 3 for Back Lights \nEnter 4 for Motor \nEnter 5 For Servo \nEnter 6 for Front Ultrasonic \nEnter 7 for Back Ultersonic'))
            if inp ==1:
                print("Checking Horn")
                hornCheck()
            elif inp ==2:
                print("Checking front Lights")
                frontLightCheck()
            elif inp ==3:
                print("Checking back Lights")
                backLightCheck()
            elif inp == 4:
                print("Checking Main Motor")
                motorCheck()
            elif inp == 5:
                print("Checking Servo Motor")
                servoCheck()
            elif inp == 6:
                print("Checking Front Ultersonic")
                usFrontCheck()
                time.sleep(0.5)
                usFrontCheck()
                time.sleep(0.5)
                usFrontCheck()
                time.sleep(0.5)
                usFrontCheck()
                time.sleep(0.5)
                usFrontCheck()
                time.sleep(0.5)
            elif inp == 7:
                print("Checking Back Ultersonic")
                usBackCheck()
                time.sleep(0.5)
                usBackCheck()
                time.sleep(0.5)
                usBackCheck()
                time.sleep(0.5)
                usBackCheck()
                time.sleep(0.5)
                usBackCheck()
                time.sleep(0.5)
except:
    p.stop()
    GPIO.cleanup()