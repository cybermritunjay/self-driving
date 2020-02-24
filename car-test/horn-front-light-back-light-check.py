import time
import RPi.GPIO as GPIO

#horn
horn= 27
#front Light
frontLight=15
#backLight
backLight=5

GPIO.setmode(GPIO.BCM)
GPIO.setup(horn, GPIO.OUT)
GPIO.setup(frontLight, GPIO.OUT)
GPIO.setup(backLight, GPIO.OUT)
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

print("Checking Horn")
hornCheck()
print("Checking Front Lights")
frontLightCheck()
print("Checking Back Lights")
backLightCheck()
GPIO.cleanup()