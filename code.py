import board
import busio
import digitalio
import analogio
import time
from random import randint
import neopixel
import adafruit_dht

import os

from adafruit_wiznet5k.adafruit_wiznet5k import *
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket

from adafruit_io.adafruit_io import IO_MQTT
import adafruit_minimqtt.adafruit_minimqtt as MQTT

secrets = {
    'aio_username' : '******',   ### Wirte Username here ###
    'aio_key' : '*******************'  ### Write Active Key here ###
    }

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

#SPI
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

#Reset
W5x00_RSTn = board.GP20

#DHT11
dhtDevice = adafruit_dht.DHT11(board.GP0)

# Activate the Pixel pins
pixel_pin = board.GP2
num_pixels = 12 #open how many leds in the Pixel

print("Wiznet5k Adafruit Up&Down Link Test (DHCP)")
# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)
IP_ADDRESS = (192, 168, 1, 100)
SUBNET_MASK = (255, 255, 255, 0)
GATEWAY_ADDRESS = (192, 168, 1, 1)
DNS_SERVER = (8, 8, 8, 8)

relay = digitalio.DigitalInOut(board.GP1)
relay.direction = digitalio.Direction.OUTPUT

ethernetRst = digitalio.DigitalInOut(W5x00_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

# Set A0 for receving data from the soil hudmidity module
soil = analogio.AnalogIn(board.A0)

# Set A1 for receving data from the light sensor module
light = analogio.AnalogIn(board.A1)

# For Adafruit Ethernet FeatherWing
cs = digitalio.DigitalInOut(SPI0_CSn)
# For Particle Ethernet FeatherWing
# cs = digitalio.DigitalInOut(board.D5)

spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

# Reset W5x00 first
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# # Initialize ethernet interface without DHCP
# eth = WIZNET5K(spi_bus, cs, is_dhcp=False, mac=MY_MAC, debug=False)
# # Set network configuration
# eth.ifconfig = (IP_ADDRESS, SUBNET_MASK, GATEWAY_ ADDRESS, DNS_SERVER)

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)

print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

### Topic Setup ###
# Adafruit IO-style Topic
# Use this topic if you'd like to connect to io.adafruit.com
# mqtt_topic = secrets["aio_username"] + '/feeds/test'

### Code ###
# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(clinet):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO!")
    
    # Subscribe to Group
    io.subscribe(group_key=group_name)

def disconnected(clinet):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from Adafruit IO!")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))
    
def message(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

def on_relay_msg(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    global relay_flag
    print("New message on topic {0}: {1}".format(topic, message))
    if message == "on":
        relay.value = True
        relay_flag = 0
    elif message == "off":
        relay.value = False
        relay_flag = 1
    else:
        print("Unexpected message on relay feed")

def on_led_onoff(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    global light_onoff
    print("New message on topic {0}: {1}".format(topic, message))
    if message == "on":
        light_onoff = 1
        pixels.brightness = 0.1
        pixels.show() #Turn ON
    elif message == "off":
        light_onoff = 0
        pixels.brightness = 0
        pixels.show() #Turn OFF
    else:
        print("Unexpected message on LED feed")

def on_sensor_onoff(client, topic, message): 
    # Method callled when a client's subscribed feed has a new value.
    global sensor_onoff 
    print("New message on topic {0}: {1}".format(topic, message))
    if message == "on": # turn on the light sensor 
        sensor_onoff = 1
    elif message == "off": #turn off the light sensor
        sensor_onoff = 0
    else:
        print("Unexpected message on LED feed / the led is off")


#Set the soil moisture precentage range
class Soil_range_set:

# Waiting time for changing to collecting dry value
    def delay(self,condition):
        for i in range(10):
            print("Please change to collect {} value...{}\r\n".format(condition,i+1))
            time.sleep(1)

# Collecting value 
    def average(self,condition):
        counter = 0
        collected = 0
        for i in range(100):
            collected= soil.value + collected
            counter = counter + 1
            time.sleep(0.1)
            print("{} value counting...{}\r\n".format(condition, counter))
        average = collected / counter 
        return average

# Read all data from files
def read_files():
    #read soil moisture setting range
    tempfile = open("settings.txt","r")
    tempdata = tempfile.read()
    tempfile.close()
    #find soil moisture setting range
    if tempdata.find(",") != -1:
            record = tempdata.split(",",2)
            dry = int(record[0])
            wet= int(record[1])
            relays = int(record[2])
    else:
        Soil_setting.delay("dry")
        dry= int(Soil_setting.average("dry"))
        Soil_setting.delay("wet")
        wet = int(Soil_setting.average("wet"))
        relays = 1 #if no record for the relay flag, back to default ("off")
    
    #read light setting range
    tempfile1 = open('light_settings.txt', 'r')
    tempdata1 = tempfile1.read()
    tempfile1.close()
    
    #find light setting range
    if tempdata1.find(",") != -1:
        split_data= tempdata1.split(",", 2)
        light1 = int(split_data[0])
        sensor1 = int(split_data[2])
        #determine the light's on/off
        if light1 == 0: #light is off
            bright1 = 0 #turn off the light 
        else:
            bright1 = float(split_data[1]) #use the previous brightness setting
        
    else:
        bright1 = 0
        sensor1 = 0
    
    return dry, wet, relays, light1 ,bright1, sensor1
# Initialize MQTT interface with the ethernet interface
MQTT.set_socket(socket, eth)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    is_ssl=False,
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Setup the callback methods above
io.on_connect = connected
io.on_disconnect = disconnected
io.on_message = message
io.on_subscribe = subscribe

# Set up a callback for the led feed
io.add_feed_callback("relay", on_relay_msg)
io.add_feed_callback("led-onoff", on_led_onoff)
io.add_feed_callback("sensor-onoff", on_sensor_onoff)
# Group name
group_name = "weatherstation"

# Feeds within the group
temp_feed = "weatherstation.temperature"
humid_feed = "weatherstation.humidity"
soil_feed = "weatherstation.soil"

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()

# # Subscribe to all messages on the led feed
io.subscribe("relay")
io.subscribe("led-onoff")
io.subscribe("sensor-onoff")
print("Connected to Adafruit !!")

#activate the soil_range_settings
Soil_setting = Soil_range_set()
#delay the collecting time
delay_counter = 0 #int
#control variables
light_onoff = 0 #int
sensor_onoff = 0 #int
brightness = 0 #float
relay_flag = 1 #int
dry_average = 0
wet_average = 0
value = 0

dry_average,wet_average,relay_flag,light_onoff,brightness,sensor_onoff= read_files()
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False)
pixels.fill((0,0,255)) # set to turn off the pixel
pixels.show()
while True:
    io.loop()
    if sensor_onoff == 1 and light_onoff == 1: #when the sensor is on and the light is turn on 
        light_per= light.value/ 65535* 100 #convert to %
        #print("light(%):" + str(light_per))
        for i in range(10):
            if light_per > i*10 and light_per < i*10 +10: # check the value is in which range
                value = (10-i)/10 #calucate the related brightness based on light sensor 
                #print(value)
                pixels.brightness = value # change the light
                pixels.show() #change the brightness
    lightfile = open('light_settings.txt', 'w+')
    lightdata = lightfile.write(str(light_onoff) + ',' + str(value)+ ','+ str(sensor_onoff))
    try:
        if delay_counter >= 5:
            #send a new message
            temp_reading = dhtDevice.temperature
            print("Publishing value {0} to feed: {1}".format(temp_reading, temp_feed))
            io.publish(temp_feed, temp_reading)

            humid_reading = dhtDevice.humidity
            print("Publishing value {0} to feed: {1}".format(humid_reading, humid_feed))
            io.publish(humid_feed, humid_reading)
        
            soil_reading = (soil.value - dry_average) / ((wet_average - dry_average)/100)
            print("Publishing value {0} to feed: {1}".format(soil_reading, soil_feed))
            io.publish(soil_feed, soil_reading)
            delay_counter = 0
            if relay_flag == 1 and soil_reading <20: 
                relay.value = True
            elif relay_flag == 1 and soil_reading >20:
                relay.value = False
        
        else:
            time.sleep(1)
            delay_counter = delay_counter + 1
        sensorfile = open("settings.txt","w+")
        sensordata = sensorfile.write(str(dry_average)+','+str(wet_average)+','+str(relay_flag))   
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
