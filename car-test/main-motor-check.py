import time
import RPi.GPIO as GPIO

#main Motor
motor1 =26
motor2=20
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)

GPIO.output(motor1, GPIO.HIGH)
GPIO.output(motor2, GPIO.LOW)
time.sleep(3)
GPIO.output(motor2, GPIO.HIGH)
GPIO.output(motor1, GPIO.LOW)
time.sleep(3)
GPIO.output(motor1, GPIO.LOW)
GPIO.output(motor2, GPIO.LOW)
GPIO.cleanup()