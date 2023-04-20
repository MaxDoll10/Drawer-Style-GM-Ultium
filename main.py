# RPI Pico W Pinout reference: https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#pinout-and-design-files-2

# Imports
import network, time
from machine import Pin, Timer
from mqtt import MQTTClient
from hx711 import HX711


#######################################

SSID = 'netis_24775C'
PASS = 'password'

#######################################

mqtt_server = '192.168.0.3' # Broker
client_id = 'rpi_pico'
topic_pub_1 = b'test_1' # Topic
topic_pub_2 = b'test_2'
topic_pub_3 = b'test_3'

# Create MQTT client object
client = MQTTClient(client_id, mqtt_server, keepalive=3600)

#######################################

# LED
led = machine.Pin('WL_GPIO0', machine.Pin.OUT) # On-board LED
timer = Timer()

# Load Cell ADC
load_cell_1 = machine.ADC(26)
load_cell_2 = machine.ADC(27)
load_cell_3 = machine.ADC(28)
hx_1 = HX711(d_out = 26, pd_sck = 19)


#######################################

def blink(timer):
    led.toggle()

def connect_wifi():    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while not wlan.isconnected():
        try:
            print('connecting to network...')
            wlan.connect(SSID, PASS)
            time.sleep(2)
        except OSError:
            pass
        print('failed to connect to the network. reattempting...')
        time.sleep(10)
    print('connected to wireless:', wlan.ifconfig(), '\n')

def connect_broker():
    try:
        print('connecting to broker...')
        client.connect()
        print('connected to broker', mqtt_server, '\n')
        time.sleep(2)
    
    except OSError:
        print('failed to connect to the broker. reconnecting...')
        time.sleep(5)
        connect_broker()
    
def transmit_data():
    conversion = 2.5 * (100 / 65535)
    while True:
        raw_data_1 = hx_1.read()
        #raw_data_1 = load_cell_1.read_u16()
        raw_data_2 = load_cell_2.read_u16()
        raw_data_3 = load_cell_3.read_u16()
        converted_data_1 = raw_data_1 * conversion
        converted_data_2 = raw_data_2 * conversion
        converted_data_3 = raw_data_3 * conversion
        data_1 = bytes(str(converted_data_1), 'utf-8')
        data_2 = bytes(str(converted_data_2), 'utf-8')
        data_3 = bytes(str(converted_data_3), 'utf-8')
        print('Sending: ', data_1, ' (converted: ', converted_data_1, ', raw: ', raw_data_1, ')')
        print('Sending: ', data_2, ' (converted: ', converted_data_2, ', raw: ', raw_data_2, ')')
        print('Sending: ', data_3, ' (converted: ', converted_data_3, ', raw: ', raw_data_3, ')')
        client.publish(topic_pub_1, data_1)
        client.publish(topic_pub_2, data_2)
        client.publish(topic_pub_3, data_3)
        print('sent.')
        time.sleep(2)
    
####################################### 
# Start
####################################### 

# Connect
connect_wifi()
connect_broker()

# Begin LED blink
timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink) 

# Begin Load Cell Transmission
transmit_data()
