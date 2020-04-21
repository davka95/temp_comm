import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
GPIO.output(25, GPIO.LOW)
time.sleep(2)
GPIO.cleanup()
#while True:
#	print(GPIO.input(24))
#GPIO.output(18, True)
#print("led_on")
#time.sleep(3)
#print("led_off")
#GPIO.output(18, False)
#GPIO.cleanup()
