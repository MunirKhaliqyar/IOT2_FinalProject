from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import ADC
import ADC2
import RPi.GPIO as GPIO
import math

# MQTT config (clientID must be unique within the AWS account)
clientID = "d7a57c0a-dbde-420f-a697-58197473f5ce"
endpoint = "a2um1r67n8s74m-ats.iot.us-east-1.amazonaws.com" #Use the endpoint from the settings page in the IoT console
port = 8883
temperatureTopic = "tb/aws/iot/sensors/temperature"
soilMoistureTopic = "tb/aws/iot/sensors/soilMoisture"

# Init MQTT client
mqttc = AWSIoTMQTTClient(clientID)
mqttc.configureEndpoint(endpoint,port)
mqttc.configureCredentials("certs/AmazonRootCA1.pem","certs/private.pem.key","certs/certificate.pem.crt")

#Actuators declaration
ledLight = 13
waterPump = 12
fan = 26

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    ADC.setup()
    ADC2.setup()
    
    GPIO.setup(ledLight,  GPIO.OUT)
    GPIO.setup(waterPump,  GPIO.OUT)
    GPIO.setup(fan,  GPIO.OUT)
    
    
# Send message to the iot topic
def send_data(message):
    mqttc.publish(topic, json.dumps(message), 0)
    print("Message Published")

# Loop until terminated
def loop():
    while True:
        try:
            #Getting the digital result value of the voltage
            thermistorRes = ADC.getADC(1)
            #print("result: " + str(result))
            
            #Converting the digital result to analog value
            thermistorVol = 3.3 * float(thermistorRes) / 255
            #print("VAnalog: " + str(VAnalog))
            
            if thermistorRes != 0 :
                #Calculating the resistance of the thermistor
                Rth = ((10000 * 3.3) / thermistorVol) - 10000
                #print ('Rth : %.2f' %Rth)
                
                #Calculating the temperature in kelvin
                Tk = 1 / (((math.log(Rth/10000))/3455) + (1/(25 + 273.15)))
                #print("Tk: " + str(Tk))
                
                #Calculating the temperature in celsius
                Tc = Tk - 273.15
                #print("Temperature: %.2f" %Tc)
                      
            #photoresistorRes = ADC.getADC(0)
            #photoresistorVol = 3.3/255 * photoresistorRes
            #print("Light: " + str(lightVol))
            #print("Temp: {:.2f}c".format(Tc))
            
            message = {
                "val0": str("loaded"),
                "val1": str("%.2f" %Tc)
                "val2": str("%.2f" %photoresistorVol)
            }

            # Send data to topic
            send_data(message)
            time.sleep(3)
        except RuntimeError as error:     # Errors happen fairly often, DHT's are hard to read, just keep going
               print(error.args[0])

# Main
if __name__ == '__main__':
    print("Starting program...")
    try:
        # Connect
        mqttc.connect()
        print("Connect OK!")

        init()
        # Main loop called
        loop()
    except KeyboardInterrupt:
        mqttc.disconnect()
        exit()