import RPi.GPIO as GPIO
from time import sleep

# Pins for Motor Driver Inputs 
Motor1A = 26
Motor1B = 20

def setup():
    #GPIO.setwarnings(False)
    #GPIO.setmode(GPIO.BCM)              # GPIO Numbering
    GPIO.setup(Motor1A,GPIO.OUT)  		# All pins as Outputs
    GPIO.setup(Motor1B,GPIO.OUT)
    
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.LOW)
    
def run():
    # Going backwards
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    
def stop():
    # Stop
    GPIO.output(Motor1B,GPIO.LOW)
    #print("Stop")
    
def destroy():  
    GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        run()
        stop()
    except KeyboardInterrupt:
        destroy()