#!/usr/bin/env python
import ADC
import time
import math
import DCMotor

def init():
  ADC.setup()
  DCMotor.setup()

def run():
    temperature = 0.0
    
    #Getting the digital result value of the voltage
    result = ADC.getADC(1)
    #print("result: " + str(result))
    
    #Converting the digital result to analog value
    VAnalog = 3.3 * float(result) / 255
    #print("VAnalog: " + str(VAnalog))
    
    if result != 0 :
        #Calculating the resistance of the thermistor
        Rth = ((10000 * 3.3) / VAnalog) - 10000
        #print ('Rth : %.2f' %Rth)
        
        #Calculating the temperature in kelvin
        Tk = 1 / (((math.log(Rth/10000))/3455) + (1/(25 + 273.15)))
        #print("Tk: " + str(Tk))
        
        #Calculating the temperature in celsius
        temperature = Tk - 273.15
        #print("Tc: " + str(temperature))
            
    return temperature
    
if __name__ == '__main__':
    init()
    try:
        run()
        #setThreshold(20)
    except KeyboardInterrupt: 
        ADC.destroy()
        DCMotot.stop()
        print ('The end !')
