import network
import time
from machine import Pin
import machine as mch
import ujson
from umqtt import MQTTClient
from neopixel import Neopixel 

# MQTT Server Parameters
MQTT_CLIENT_ID = "promake-demo"
MQTT_BROKER    = "test.mosquitto.org"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "promake/led/test"

WIFI_SSID = "BlackFox"
WIFI_PASSWORD = "@li9214970398"

class Colors:
  yellow = (255, 100, 0)
  orange = (255, 50, 0)
  green = (0, 255, 0)
  blue = (0, 0, 255)
  red = (255, 0, 0)
  black = (0,0,0)
  white = (255,255,255)

class PixelCtrl:
  def __init__(self,num_pixels=2):
    self.pixels_obj = Neopixel(num_pixels, 0, 14, "GRB")
    
  def fill(self,color):
      self.pixels_obj.set_pixel(0, color)
      self.pixels_obj.set_pixel(1, color)
      self.pixels_obj.show()
  
  def off(self):
    self.pixels_obj.set_pixel(0, Colors.black)
    self.pixels_obj.set_pixel(1, Colors.black)
    self.pixels_obj.show()
  
  def on(self):
    self.pixels_obj.set_pixel(0, Colors.white)
    self.pixels_obj.set_pixel(1, Colors.white)
    self.pixels_obj.show()



led = Pin(2,Pin.OUT)
pixel_obj = PixelCtrl()
     

print("Connecting to WiFi", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
  print(".", end="")
  time.sleep(1)
print(" Connected!")

commands_list = {
        'on':Colors.white,
        'off':Colors.black,
        'blue':Colors.blue,
        'green':Colors.green,
        'red':Colors.red,
        'yellow':Colors.yellow,
        'orange':Colors.orange
    }


def sub_callback(topic, msg):
  # print((topic, msg))
  str_msg = msg.decode('utf-8')
  if str_msg in commands_list:
    pixel_obj.fill(commands_list[str_msg])


def connect_and_subscribe():
  client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
  client.set_callback(sub_callback)
  client.connect()
  client.subscribe(MQTT_TOPIC)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (MQTT_BROKER, MQTT_TOPIC))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  mch.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    time.sleep(1)
  except OSError as e:
    restart_and_reconnect()