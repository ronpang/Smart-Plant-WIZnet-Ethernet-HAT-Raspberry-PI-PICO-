# Smart Plant (WIZnet Ethernet HAT + Raspberry Pi PICO)
This Smart Plant Application is a simple system to monitor and control devices through Adafruit IO platform

By using WIZnet Ethernet HAT with Raspberry Pi PICO, it required simple coding to create the communication method between PICO with Adafruit IO.

Youtube: 

## Network Diagram
The communication method with Adafruit IO required to used a network application protocol: MQTT protocol. (information)

This protocol required TCP protocol for the based of the communication. 

WIZnet's hardwired TCP/IP protocol provides a substainable solution with a less meomory space to easily communicate with Adafruit IO

The following image is network diagrams between Raspberry Pi Pico with Adafruit IO

![][link-network diagram]

## Required modules (linked required)

![][link-connection diagram]

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

## Connection Diagram
### Digital IO
1. DHT11 - GP0
2. 5V realy - GP1
3. Neopixel - GP2

### Analogue IO (ADC converter)
1. Soil Moisture Sensor - A0
2. Light Sensor - A1

## Software
### Bundles:
1. Circuit Python 7.0 (1 MB) (information)
2. Adafruit circuit python bundle (information)
3. WIZnet's circuit python bundle (information)

### Required Libraries:
1. adafruit_bus_services folder
2. adafruit_io folder
3. adafruit_minimqtt folder
4. adafruit_wiznet5k folder
5. adafruit_dht
6. adafruit_request
7. neopixel

## Function
### 1. Creating a TCP communication
### 2. Using MQTT to communicate
### 3. Set the correct format to communicate with MQTT broker
### 4. Simple calibration on Soil moisture sensor (setting range)
### 5. Collecting data from sensor 
### 6. Analysis commands from Adafruit IO 
### 7. Control relays to control the water valve
### 8. LED controls by light sensor


[link-network diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/network%20diagram%20-%20github.PNG
[link-connection diagram]: https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-/blob/main/image/connection%20diagram%20-%20github.PNG
