import RPi.GPIO as GPIO
import time

servoPIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz

p.start(7)

try:
    while True:
	    #angle = float(input("angle between 0-> 108="))
	    #p.ChangeDutyCycle(2+ (angle/18))
        p.ChangeDutyCycle(2)  # turn towards 0 degree
        time.sleep(1) # sleep 1 second
        p.ChangeDutyCycle(12) # turn towards 180 degre
        time.sleep(1)
except KeyboardInterrupt:
    p.stop()
    GPIO.cleanup()