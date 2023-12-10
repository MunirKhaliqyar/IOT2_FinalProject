#!/usr/bin/env python
import ADC
import time
import RPi.GPIO as GPIO

PIN_LED = 13

def init():
    ADC.setup()
    
    GPIO.setup(PIN_LED, GPIO.OUT)
    

def run():
    res = ADC.getADC(0)
    vol = 3.3/255 * res
    
    if(vol > 1.65):
        print('Light \n')
        GPIO.output(PIN_LED, True)
        return "Light"
    elif(vol < 1.65):
        print('Dark \n')
        GPIO.output(PIN_LED, False)
        return "Dark"

if __name__ == '__main__':
    init()
    try:
        run()
    except KeyboardInterrupt: 
        ADC.destroy()
        print ('The end !')
