# Smart Plant (WIZnet Ethernet HAT + Raspberry Pi PICO)
This Smart Plant Application is a simple system to monitor and control devices through Adafruit IO platform

By using WIZnet Ethernet HAT with Raspberry Pi PICO, it required simple coding to create the communication method between PICO with Adafruit IO. 

### 🟥  [YouTube video][link-youtube smart plant]

![][link-application]

## 🗺️ Network Diagram
The communication method with Adafruit IO required to use a network application protocol: MQTT protocol. (information)

This protocol required TCP protocol for the based of the communication. 

WIZnet's hardwired TCP/IP protocol provides a substainable solution with a less meomory space to easily communicate with Adafruit IO

The following image is network diagrams between Raspberry Pi Pico with Adafruit IO

![][link-network diagram]

## 💻 Required modules (linked required)

### Solution boards
1. WIZnet Ethernet HAT (or W5100s-EVB pico)
2. Raspberry PI PICO (If used W5100S-EVB pico, it does not required to have PICO)

### Sensors:
1. DHT11
2. Soil Moisture Sensor
3. Light sensor 

#### Controls:
1. 6V Water Valve 
2. 5V relay
3. Neopixel (12 pcs of LED lights)

### External components
1. Power Supply: USB 5V external power supply
2. Resistor: Around 7 ohm resistor 

## 🖱️Connection Diagram

![][link-connection diagram]

### Digital IO
1. DHT11 - GP0
2. 5V realy - GP1
3. Neopixel - GP2

### Analogue IO (ADC converter)
1. Soil Moisture Sensor - A0
2. Light Sensor - A1

## 📚 Software
### Bundles:
1. Circuit Python 7.0 (1 MB) (information)
2. Adafruit circuit python bundle (information) - Use the latest version from adafruit bundle page
3. WIZnet's circuit python bundle (information) - Use the latest version from WIZnet bundle page

### Required Libraries from adafruit bundle:
1. adafruit_bus_services folder
2. adafruit_io folder
3. adafruit_minimqtt folder
4. adafruit_wiznet5k folder
5. adafruit_dht
6. adafruit_request
7. neopixel

## 🤖 Features
### 1. WIZnet's basic setup a MQTT socket (WIZnet official sample coding - MQTT example coding)
For Smart Plant application, it required to create one of the socket for MQTT. This created MQTT socket, it will be used for MQTT protocol to communicate.

#### Create and Initialize the network 
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
#### Create a MQTT socket

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

### 2. Using MQTT to communicate with Adafruit IO
MQTT protocol required a standard format to communicate a MQTT broker. This broker will received all information from different parties.

The method for creating communication for both parties are connecting to the broker for uploading(publish) or downloading(subscribe) information through the broker.

For connecting to Adafruit IO's MQTT broker, it required to to have username and key provided by Adafruit IO (register a account from Adafruit IO)

#### Adafruit IO account setup
```python
secrets = {
    'aio_username' : '*****',  ### Wirte your Username here ###
    'aio_key' : 	 '*****',  ### Write your Active Key here ###
    }
```
#### Function to connect Adafruit IO
```python    
# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()
```
### 3. Set the correct format to communicate with MQTT broker
When any MQTT clients has connected to the broker and subscribe related feeds, it will received data/command from the MQTT broker. Base on the data from the broker, PICO will starts taking action based on the received data/command from WIZnet's Ethernet HAT

#### Subscribe example Procedure from smart plant application
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
#### Start looping for listening updates from the subscribed feeds
```python  
while True:
    io.loop()
```
For publish a feeds to a MQTT broker, Adafruit minimqtt has provide the function to simply publish data to the broker.

#### Puslish example Procedure from smart plant application
```python
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
### 4. Simple calibration on Soil moisture sensor (setting range)
### 5. Collecting data from sensor 
### 6. Analysis commands from Adafruit IO 
### 7. Control relays to control the water valve
logic are required
### 8. LED controls by light sensor
logic are required
### 9. Adafruit IO dashboard setup

[link-network diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/network%20diagram%20-%20github.PNG
[link-connection diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/connection%20diagram%20-%20github.PNG
[link-application]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/IMG_0039.JPG
[link-youtube smart plant]: https://www.youtube.com/watch?v=daI-JMGb_9Q&t=12s
