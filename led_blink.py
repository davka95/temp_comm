import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.LOW)
#time.sleep(2)
GPIO.cleanup()

#while True:
#	print(GPIO.input(22))
#GPIO.setup(23, GPIO
#GPIO.output(23, 1)
#print("led_on")
#time.sleep(3)
#print("led_off")
#GPIO.output(18, False)
#GPIO.cleanup()

