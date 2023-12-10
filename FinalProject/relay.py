import RPi.GPIO as GPIO
import time

channel = 16

def setup():
    # GPIO setup
    #GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)

def motor_on():
    GPIO.output(channel, GPIO.HIGH)  # Turn motor on


def motor_off():
    GPIO.output(channel, GPIO.LOW)  # Turn motor off


if __name__ == '__main__':
    try:
        setup()
        motor_on()
        time.sleep(1)
        motor_off()
        time.sleep(1)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()