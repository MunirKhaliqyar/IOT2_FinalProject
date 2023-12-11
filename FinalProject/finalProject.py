from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time
import ADC
import ADC2
import RPi.GPIO as GPIO
import math
import DCMotor
import relay
import soilMoistureModule
import thermistor
import photoresistor
import threading
import smtplib

# MQTT config (clientID must be unique within the AWS account)
clientID = "d7a57c0a-dbde-420f-a697-58197473f5ce"		#Random intergers and strings
endpoint = "a2um1r67n8s74m-ats.iot.us-east-1.amazonaws.com" #Use the endpoint from the settings page in the IoT console
port = 8883
uplinkTopic = "tb/aws/iot/sensors/IOTFinalProjectDevice"
downlinkTopic = "tb/aws/downlink"
# Init MQTT client
mqttc = AWSIoTMQTTClient(clientID)

# Email configuration
email_sender = "kingoftheworld45678@gmail.com"
email_password = "king@888"
email_recipient = "LE2176022@crc-lennox.qc.ca"

# Mutex for synchronization
mutex = threading.Lock()

#Actuators declaration
ledLight = 13
waterPump = 12

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    ADC.setup()
    ADC2.setup()
    DCMotor.setup()
    relay.setup()
    
    
    GPIO.setup(ledLight,  GPIO.OUT)
    GPIO.setup(waterPump,  GPIO.OUT)
    
def initializeMQTT():
    mqttc.configureEndpoint(endpoint,port)
    mqttc.configureCredentials("certs/AmazonRootCA1.pem","certs/private.pem.key","certs/certificate.pem.crt")
    
    # Connect to MQTT
    mqttc.connect()
    print("Connect OK!")
    
    #mqttc.subscribe(downlinkTopic, 1, callback)
    #print("Subscribed to ", downlinkTopic)
    
#Get the threshold values from User
def setThreshold():
    validTemperatureValue = False
    validHumidityValue = False
    
    global temperatureThreshold
    global humidityThreshold
    
    print(" \nWelcome")
    print("")
    while (not validTemperatureValue):
        temperatureThreshold = input("Set a threshold for temperature: ")
        if temperatureThreshold.isnumeric():
            temperatureThreshold = float(temperatureThreshold)
            validTemperatureValue = True
        
    while (not validHumidityValue):
        humidityThreshold = input("Set a threshold for humidity: ")
        if humidityThreshold.isnumeric():
            humidityThreshold = float(humidityThreshold)
            validHumidityValue = True
    print("")
    print("Thank you \n")

#Send email
def sendEmail(sensorType, sensorValue):
    emailSubject = f"Alarm: High {sensorType}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_sender, email_password)

        body = f"Alert: High {sensorType} Detected!\nSensor Value: {sensorValue}"
        emailText = f"Subject: {emailSubject}\n\n{body}"

        server.sendmail(email_sender, email_recipient, emailText)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

#Handle the receiving message
def callback(client, userdata, message):
    print(f"Received message on topic {message.topic}: {message.payload}")

#Getting the digital result value of the thermistor voltage
def getTemperature():
    global temperature 
    
    temperature = checkTemp()
    print('temperature : %.2f\n' %temperature)
              
    with mutex:
        if temperature >= temperatureThreshold:
            sendEmail("Temperature", temperature)  # Send email notification
            print("Temperature email sent.")
            DCMotor.run()
            time.sleep(10)
            DCMotor.stop()
        else:
            DCMotor.stop()
        
def getHumidity():
    global humidity

    humidity= soilMoistureModule.run()
    print("Humidity: %.2f \n" %humidity)
    
    with mutex:
        if humidity < humidityThreshold:
            sendEmail("Humidity", humidity)  # Send email notification
            print("Humidity email sent.")
            relay.motor_on()
            time.sleep(3)
            relay.motor_off()
        else:
            relay.motor_off()
        
#Check the state of light and turn on/off the led light
def getLight():
    global light
    
    light = photoresistor.run()
    
# Send message to the iot topic
def send_data(message):
    mqttc.publish(uplinkTopic, json.dumps(message), 0)
    print("Message Published")

# Loop until terminated
def loop():
    while not stop_event.is_set():
        try:
            
            temperatureThread = threading.Thread(target=getTemperature)
            temperatureThread.start()
            
            humidityThread = threading.Thread(target=getHumidity)
            humidityThread.start()
            
            lightThread = threading.Thread(target=getLight)
            lightThread.start()
            
            time.sleep(0.5)
            
            message = {
                "state": "loaded",
                "temperature": str("%.2f" %temperature),
                "humidity": str("%.2f" %humidity),
                "Photoresistor": str(light)
            }
            
            # Send data to topic
            send_data(message)
            time.sleep(1)
        except RuntimeError as error:     # Errors happen fairly often, DHT's are hard to read, just keep going
               print(error.args[0])

#Check the thermistor state
def checkTemp():
    return thermistor.run()

#Check the humidity
def checkHumidity():
    return soilMoistureModule.run()
    
# Main
if __name__ == '__main__':
    print("Starting program...")
    try:
        #Initialize the sensors and the actuators
        init()
        
        #Setup the MQTT
        initializeMQTT()
        
        #Set the thresholds
        setThreshold()
        
        # Global event to signal threads to stop
        stop_event = threading.Event()
        
        # Main loop called
        loop()
    except KeyboardInterrupt:
        #mqttc.disconnect()
        stop_event.set()
        GPIO.cleanup()
        exit()
    