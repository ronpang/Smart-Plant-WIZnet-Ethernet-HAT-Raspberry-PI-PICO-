# Smart Plant (WIZnet Ethernet HAT + Raspberry Pi PICO)
This Smart Plant Application is a simple system to monitor and control devices through Adafruit IO platform

By using WIZnet Ethernet HAT with Raspberry Pi PICO, it required simple coding to create the communication method between PICO with Adafruit IO. 

### 🟥  [YouTube video][link-youtube smart plant]

![][link-application]

# Directory
1. [Network Diagram](#NetworkDiagram)
2. [Required modules](#Requiredmodules)
3. [Connection Diagram](#ConnectionDiagram)
4. [Software](#Software)
5. [Features](#Features)
    - [WIZnet's basic setup for a MQTT socket](#MQTT)
    - [Using MQTT to communicate with Adafruit IO](#MQTTadafruit)
    - [Set the correct format to communicate with MQTT broker](#MQTTbroker)
    - [Simple calibration on Soil moisture sensor](#soilrange)
    - [Collecting data from sensor](#datacollect)
    - [Adafruit IO dashboard setup](#dashboard)
    - [Analysis commands from Adafruit IO](#commands)
    - [Controls relay to control the water valve](#watervalve)
    - [LED controls by light sensor](#LEDcontrol)
    - [File system in circuit python](#filesystem)

<a name="NetworkDiagram"></a>
## 🗺️ Network Diagram
The communication method with Adafruit IO required to use a network application protocol: MQTT protocol. ([information][link-mqtt info])

This protocol required TCP protocol as the based of the communication. 

WIZnet's hardwired TCP/IP protocol provides a substainable solution with a less meomory space to easily communicate with Adafruit IO

The following image is network diagrams between Raspberry Pi Pico with Adafruit IO

![][link-network diagram]

<a name="Requiredmodules"></a>
## 💻 Required modules (linked provided)

### Solution boards
1. [WIZnet Ethernet HAT][link-Ethernet HAT] (or [W5100s-EVB pico][link-w5100s pico])
2. [Raspberry PI PICO][link-pico] (If used W5100S-EVB pico, it does not required to have PICO)

### Sensors:
1. [DHT11][link-DHT11] 
2. [Soil Moisture Sensor][link-soil sensor]
3. [Light Sensor / Photosensitive Sensor][link-light sensor]

#### Controls:
1. [6V Water Valve][link-water valve]
2. [5V relay][link-relay]
3. [Pixel LED][link-pixel] (12 pcs of LED lights)

### External components
1. Power Supply: USB 5V external power supply
2. Resistor: Around 7 ohm resistor 

<a name="ConnectionDiagram"></a>
## 🖱️Connection Diagram

![][link-connection diagram]

### Digital IO
1. DHT11 - GP0
2. 5V realy - GP1
3. Pixel LED - GP2

### Analogue IO (ADC converter)
1. Soil Moisture Sensor - A0
2. Light Sensor - A1

### External circuit
1. Water valve required to use another circuit to prevent any short circuit that may causes to the developing board
2. Resistor is required to reduce current from the supply to the water valves input current requirement 

<a name="Software"></a>
## 📚 Software
### Bundles:
1. [Circuit Python 7.0][link-circuit python] (it required to use 1 MB from the flash) 
2. [Adafruit circuit python bundle][link-adafruit] - Use the latest version from adafruit bundle page
3. [WIZnet's circuit python bundle][link-wiznet] - Use the latest version from WIZnet bundle page

### Required Libraries from adafruit bundle:
1. adafruit_bus_services folder
2. adafruit_io folder
3. adafruit_minimqtt folder
4. adafruit_wiznet5k folder
5. adafruit_dht
6. adafruit_request
7. neopixel (This application is neopixel-compatiable)

### How to install circuit Python into Raspberry Pi Pico
🟥Youtube: [Linux install method][link-linux install]

🟥Youtube: [Window install method][link-window install]

<a name="Features"></a>
## 🤖 Features

<a name="MQTT"></a>
### 1. WIZnet's basic setup for a MQTT socket ([WIZnet official sample coding - MQTT example coding][link-MQTT example])
For Smart Plant application, it required to create one of the socket for MQTT. This created MQTT socket, it will be used for MQTT protocol to communicate.

#### Create and Initialize the network:
```python
##Set SPI pins to commnunicate with WIZnet's Ethernet Chip 
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

##Reset pin for the Ethernet chip
W5x00_RSTn = board.GP20

##Initialize and collect the IP address for the device through DHCP protocol (collect IP address from your router)
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=False)
```
WIZnet library are software compatiable with Adafruit mini MQTT library. Therefore user could easily use minimqtt fuction to activate the connection.
#### Create a MQTT socket:

```python
# Initialize MQTT interface with the ethernet interface
MQTT.set_socket(socket, eth)

# Setup a new MQTT Client
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"], # Explain in the next section
    password=secrets["aio_key"], # Explain in the next section
    is_ssl=False,
)

# Create an Adafruit IO MQTT Client connection
io = IO_MQTT(mqtt_client)
```

<a name="MQTTadafruit"></a>
### 2. Using MQTT to communicate with Adafruit IO
MQTT protocol required a standard format to communicate a MQTT broker. This broker will received all information from different parties.

The method for creating communication for both parties are connecting to the broker for uploading(publish) or downloading(subscribe) information through the broker.

For connecting to Adafruit IO's MQTT broker, it required to to have username and key provided by Adafruit IO ([register a account from Adafruit IO][link-register])

#### Adafruit IO account setup:
```python
secrets = {
    'aio_username' : '*****',  ### Wirte your Username here ###
    'aio_key' : 	 '*****',  ### Write your Active Key here ###
    }
```
#### Function to connect Adafruit IO:
```python    
# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()
```

<a name="MQTTbroker"></a>
### 3. Set the correct format to communicate with MQTT broker
When any MQTT clients has connected to the broker and subscribe related feeds, it will received data/command from the MQTT broker. Base on the data from the broker, PICO will starts taking action based on the received data/command from WIZnet's Ethernet HAT

#### Subscribe example Procedure from smart plant application:
All these procdures are reuqired to be done before and after connecting Adafruit IO
```python
# Set up a callback feeds - setup before the connecting Adafruit IO. If there is a update, it will collect values
io.add_feed_callback("relay", on_relay_msg)
io.add_feed_callback("led-onoff", on_led_onoff)
io.add_feed_callback("sensor-onoff", on_sensor_onoff)

# Subscribe to all messages on the led feed - after Adafruit IO is connected. 
# Subscribed channel will be listen for updates. if there is an update, it will use callback function to collect data
io.subscribe("relay")
io.subscribe("led-onoff")
io.subscribe("sensor-onoff")
```
#### Start looping for listening updates from the subscribed feeds:
```python  
while True:
    io.loop()
```
For publish a feeds to a MQTT broker, Adafruit minimqtt has provide the function to simply publish data to the broker.

#### Puslish example Procedure from smart plant application:
```python
#Published Feeds setup before sending to Adafruit IO 
temp_feed = "weatherstation.temperature"
humid_feed = "weatherstation.humidity"
soil_feed = "weatherstation.soil"

temp_reading = dhtDevice.temperature #Collect temperature data from DHT11
print("Publishing value {0} to feed: {1}".format(temp_reading, temp_feed))
io.publish(temp_feed, temp_reading) #publish to adafruit IO

humid_reading = dhtDevice.humidity #Collect humidity data from DHT11
print("Publishing value {0} to feed: {1}".format(humid_reading, humid_feed))
io.publish(humid_feed, humid_reading) #publish to adafruit IO

#Calculate ADC converted soil moisture reading from the sensor
soil_reading = (soil.value - dry_average) / ((wet_average - dry_average)/100) 
print("Publishing value {0} to feed: {1}".format(soil_reading, soil_feed))
io.publish(soil_feed, soil_reading) #publish to adafruit IO
```

<a name="soilrange"></a>
### 4. Simple calibration on Soil moisture sensor (setting range)
The range of the soil moisture sensor are required to set. This is based on the soil moisture sensor ADC value could not used the whole range of the analogue signal by the restriction by environment and the sensor's conductivity. 

Therfore the range will be set between the dry condition (air result) and wet condition (water result)

**Air result** are the results collecting from the air. This would be the driest condition for the surrounding environment

**water result** are the results submerge in the water, This would be the moisted condition for the surrounding environment 

#### Process logic of this fucntion:
1. 10 seconds delay before starting collect air result (dry condition)
2. Collect 100 samples for air result (10 seconds) and get average value
3. 10 seconds delay for changing to collect wet result (water result)
4. Collect 100 samples for water result (10 seconds) and get average value
5. Using both (air and water) average to become the range 

This application has a feature to saved all the previous setting to a file system.

#### Codes from the application:
```python 
Soil_setting.delay("dry")
dry= int(Soil_setting.average("dry"))
Soil_setting.delay("wet")
wet = int(Soil_setting.average("wet"))
```

For more information, please refer the links below.
1. [Soil moisture calibration (setting range) code][link-soil code]
2. [Soil moisture calibration example from arduino][link-soil example] 

<a name="datacollect"></a>
### 5. Collecting data from sensor
DHT11: DHT library included, it required to activate the function as follow.
DHT11 or DHT22 will easily have errors, using try method to prevent some errors
#### DHT11:
```python
try:
    #temperature data from DHT11
    temp_reading = dhtDevice.temperature 

    #Humidity data from DHT11
    humid_reading = dhtDevice.humidity
    
except RuntimeError as error:
    #Errors happen fairly often, DHT's are hard to read, just keep going
    print(error.args[0])
    time.sleep(2.0)
    continue
except Exception as error:
    dhtDevice.exit()
    raise error
```
Soil moisture sensor: Soil sensor required to have (range set) before using it for providing a more resonable results
After converting the data to digital form, the calculation for this application will be showed like follow.

#### Soil Moisture Sensor:
```python
soil_reading = (soil.value - dry_average) / ((wet_average - dry_average)/100) 
```

<a name="dashboard"></a>
### 6. Adafruit IO dashboard setup
It is required to register a [account][link-register] before using the Dashboard.

After the account is opened, you could create your own dashboard by creating your [feeds and blocks][link-register] from Adafruit IO

#### Smart Plant Adafruit IO setup:
**Feeds setup:** Try to name your feeds name is the same as your subscribe/publish name. 

If not, please ensure your key is the same a your subscribe/publish name.
![][link-keynames]
```python
#Published Feeds
temp_feed = "weatherstation.temperature"
humid_feed = "weatherstation.humidity"
soil_feed = "weatherstation.soil"

#Subscribed Feeds
io.subscribe("relay")
io.subscribe("led-onoff")
io.subscribe("sensor-onoff")
```
**Block setup:** Please ensure your block is using the correct feeds
![][link-dashboard]


<a name="commands"></a>
### 7. Analysis commands from Adafruit IO
Adafruit Setup: it needs to set correct command for Subscribed blocks to communicate with PICO
#### Block command setup:
![][link-block]
```python
#Call back function for LED switch
io.add_feed_callback("led-onoff", on_led_onoff)

#correspond function for analysis the command 
def on_led_onoff(client, topic, message): 
    # Method callled when a client's subscribed feed has a new value.
    global light_onoff
    print("New message on topic {0}: {1}".format(topic, message))
    if message == "on": #if received "on" command, turn on LED
        light_onoff = 1
        pixels.brightness = 0.1
        pixels.show() #Turn ON
    elif message == "off": #if received "off" command, turn on LED
        light_onoff = 0
        pixels.brightness = 0
        pixels.show() #Turn OFF
    else:
        print("Unexpected message on LED feed")
```


<a name="watervalve"></a>
### 8. Controls relay to control the water valve
If it turns **on**, it will closed the water valve circuit by the relay

If it turns **off**, it will go to automation mode. if lower than 20% moist content, it will turn on the water valve
#### Application Code:
```python
#Called back function
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
  
 # If statement for decision making   
 if relay_flag == 1 and soil_reading <20: 
       relay.value = True
 elif relay_flag == 1 and soil_reading >60:
       relay.value = False 
  
```
<a name="LEDcontrol"></a>

### 9. LED controls by light sensor
The following function required the LED light has turn on. (If it is turn off, light sensor will not affect the brightness of the LED light)

If it turns **on**, brightness of the light will depends on the light sensor

If it turns **off**, brightness will not be changed by light sensor.

For a better version of Pixel LED appication, please refer this [link][link-pixel io]

#### Application code:
```python
# Call back function
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
        
#Process for light sensor
if sensor_onoff == 1 and light_onoff == 1: #when the sensor is on and the light is turn on 
     light_per= light.value/ 65535* 100 #convert to %
     for i in range(10):
         if light_per > i*10 and light_per < i*10 +10: # check the value is in which range
             value = (10-i)/10 #calucate the related brightness based on light sensor 
              pixels.brightness = value # change the light
              pixels.show() #change the brightness
```
<a name="filesystem"></a>

### 10. File system in circuit python
Raspberry PI PICO with Circuit Python are capable to use file system to save records into it's 2MB flash drive.

However, it required to add a boot.py file to flash to have this ability

For more information, please refer to the [link][link-file system].

## Reference:
Adafruit Neopixel link: https://github.com/adafruit/Adafruit_NeoPixel


[link-network diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/network%20diagram%20-%20github.PNG
[link-connection diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/connection%20diagram%20-%20github.PNG
[link-application]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/IMG_0039.JPG
[link-dashboard]:https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/dashboard%20image.PNG
[link-youtube smart plant]: https://www.youtube.com/watch?v=daI-JMGb_9Q&t=12s
[link-keynames]:https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/Key%20name%20(adafruit%20IO).PNG
[link-block]:https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/block%20example.PNG
[link-mqtt info]: https://mqtt.org/
[link-Ethernet HAT]: https://docs.wiznet.io/Product/Open-Source-Hardware/wiznet_ethernet_hat
[link-pico]: https://www.raspberrypi.com/products/raspberry-pi-pico/
[link-w5100s pico]: https://docs.wiznet.io/Product/iEthernet/W5100S/w5100s-evb-pico
[link-DHT11]: https://www.aliexpress.com/item/1005002418805042.html?spm=a2g0o.search0304.0.0.35e921e9Wyhdny&algo_pvid=9d8bbd2c-dc0c-44e7-94e1-b800f5791a21&algo_exp_id=9d8bbd2c-dc0c-44e7-94e1-b800f5791a21-0
[link-soil sensor]: https://www.sparkfun.com/products/13637
[link-light sensor]: https://www.arrow.com/en/products/dfr0095/dfrobot
[link-water valve]: https://www.ebay.com/itm/263420396952
[link-relay]: https://www.amazon.com/SunFounder-Module-Arduino-Raspberry-Trigger/dp/B0151F3A9Q
[link-pixel]: https://www.arrow.com/en/products/1643/adafruit-industries
[link-circuit python]: https://circuitpython.org/board/raspberry_pi_pico/
[link-adafruit]: https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20211208
[link-wiznet]: https://github.com/ronpang/RP2040-HAT-CircuitPython/tags
[link-MQTT example]: https://github.com/ronpang/RP2040-HAT-CircuitPython/blob/master/examples/Adafruit_IO/Up%26DownLink/W5x00_Adafruit%20IO_Up%26DownLink.py
[link-register]: https://github.com/ronpang/RP2040-HAT-CircuitPython/blob/master/examples/Adafruit_IO/Getting%20Start%20Adafruit%20IO.md
[link-soil code]: https://github.com/ronpang/WIZnet-HK_Ron/tree/main/Soil%20Sensor
[link-soil example]: https://lastminuteengineers.com/soil-moisture-sensor-arduino-tutorial/
[link-pixel io]: https://github.com/ronpang/WIZnet-HK_Ron/blob/main/Adafruit%20io/Adafruit%20io%20(Neopixel%20light%20control)%20%2B%20previous%20record.py
[link-file system]: https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/data-logger
[link-linux install]: https://www.youtube.com/watch?v=onBkPkaqDnk&list=PL846hFPMqg3h4HpTVO8cPPHZnJIRA4I2p&index=3
[link-window install]: https://www.youtube.com/watch?v=e_f9p-_JWZw&t=374s
