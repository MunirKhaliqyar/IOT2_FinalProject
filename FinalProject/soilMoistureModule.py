#!/usr/bin/env python
import ADC
import time

def init():
	ADC.setup()

def loop():
	while True:
		res = ADC.getADC(0)
		moisture = 255 - res
		print ('analog value: %03d  moisture: %d' %(res, moisture))
		time.sleep(0.1)

if __name__ == '__main__':
	init()
	try:
		loop()
	except KeyboardInterrupt: 
		ADC.destroy()
		print ('The end !')