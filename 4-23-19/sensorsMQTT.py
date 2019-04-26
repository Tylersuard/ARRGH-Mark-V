
#NOTES:  As of 2/25/19, this is the most recent version.  It includes the correction functioning of the LED's and 
# the transmitter (transmitter has not been tested), and sends MQTT messages to Thingspeak.com, corresponding
# to whatever alarm goes off. 
#Things to note:
#1.  Do NOT use the default MicroPython image that comes with uPyCraft.  Use the most recent image from 
#MicroPython.org, and flash it via ESPcut if necessary.
#2.  Upload DoConnect2.py and test with cell phone app interfaces so you can connect to it and then do the password stuff.
#3.  Upload this file and run it.

print("Starting MQTT and Sensors")

import machine
import time
import os
import network
from umqtt.simple import MQTTClient
import ubinascii

Softversion = "0.9"
Softbuild = "4-23-19"


#Find ESP-12's IP address and set it to variable name "deviceIP"
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)  #activate access point
apIP = ap_if.ifconfig()
deviceIP = apIP[0]

#Find MAC address of ESP-12 and set it to variable name "last4Mac"
macAddrBinary = ap_if.config('mac')
convertedMac = ubinascii.hexlify(macAddrBinary, ":")
finalMac = convertedMac.decode()
last4Mac = str(finalMac[12:14] + finalMac[15:])

MarkVAlert = "All Clear"

#Set up MQTT Connection
SERVER = "54.190.195.131"  #This is Arrgh's server.
client = MQTTClient("umqtt_client", SERVER)
topic = "BCN/from_device/Arrgh_"+last4Mac
longAssPrefix = "{\"ALERT\":\"" + MarkVAlert + "\", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
#Spell check this one ^^^


# H2 1% detector: Changed to Pin 9 from pin 16
H2_alarm_1 = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)

# H2 2% detector: Pin 14
H2_alarm_2 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# Smoke detector: Pin 4
Smoke_detector = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# IR Sensor: Pin 13
IR_Sensor = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# Yellow LED: Changed to pin 0 from pin 9
Y_LED = machine.PWM(machine.Pin(0))
Y_LED.freq(300)

# Red LED: Changed to pin 2 from pin 10   (CAN WE DO PIN 16?  Pin 2 is ADC converter)

#**** DON'T DO PWM FOR THIS ONE, JUST SIMPLE ON/OFF, AND CHANGE IT TO PIN 16!!!
R_LED = machine.PWM(machine.Pin(2))
R_LED.freq(300)

# Test Button: Pin 5
Test_Button = machine.Pin(5, machine.Pin.IN)

# 433mhz Transmitter: Changed to pin 12 from pin 1  (cannot use pin 12.  Use pin 15!)
Transmitter_433 = machine.PWM(machine.Pin(12))
Transmitter_433.freq(300)


#---------------Light Flashing Definitions---------

# Make Yellow LED run for 30 sec at 1/6 duty
def Yellow_Warmup():
  for i in range (1,91):
    Y_LED.duty(170)
    time.sleep(1)
    Y_LED.duty(0)
    time.sleep(1)

def H2_Alert_Steady_Yellow():  #Turn yellow on, full blast
  Y_LED.duty(1023)
 
def Yellow_Off():
  Y_LED.duty(0)
  
def Red_Off():
  R_LED.duty(0)
  
def H2_Alert_Red_Blink_And_Transmit_To_Fan():
  for i in range(1,7):
    Transmitter_433.duty(512)
    for i in range(1,11):
      R_LED.duty(1023)
      time.sleep(0.5)
      R_LED.duty(0)
      time.sleep(0.5)
    Transmitter_433.duty(0)
    for i in range(1,11):
      R_LED.duty(1023)
      time.sleep(0.5)
      R_LED.duty(0)
      time.sleep(0.5)

def Smoke_Alert_Flash():
  for i in range(1,31):
    for i in range (1,4):
      R_LED.duty(1023)
      time.sleep(.5)
      R_LED.duty(0)
      time.sleep(.5)
  #flash4
    R_LED.duty(0)
    time.sleep(1)
  
def Smoke_Alert_And_H2_1_Flash():
  H2_Alert_Steady_Yellow()
  Smoke_Alert_Flash()  
  
def Intrusion_Alert_Blink():
  for i in range (1,121):
      Y_LED.duty(170)
      time.sleep(0.5)
      Y_LED.duty(0)
      time.sleep(0.5)

def Turn_Fan_On():
  for i in range(1,7):
    Transmitter_433.duty(512)
    time.sleep(10)
    Transmitter_433.duty(0)
    time.sleep(10)
  
  
#--------------------ACTION DEFINITIONS---------------

def WarmupCycle():
  Yellow_Warmup()
      
def H2_1_Alert():
  if H2_alarm_1.value() and not H2_alarm_2.value() and Smoke_detector.value():
    print('1% H2: Detected!')
    H2_Alert_Steady_Yellow()
    Turn_Fan_On()
    
def H2_2_Alert():
  if H2_alarm_1.value() and H2_alarm_2.value() and Smoke_detector.value():
    #Send wifi alarm:
    MarkVAlert = "\"1%_H2\":1, \"2%_H2\":1, \"Smoke\":0, \"Motion\":0"
    longAssPrefix = "{"+ MarkVAlert + ", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
    payload = longAssPrefix
    try:
      client.connect()
      client.publish(topic, payload)
      client.disconnect()
    except:
      pass
    #Show lights
    print('2% H2: Detected!')
    H2_Alert_Red_Blink_And_Transmit_To_Fan()
    

    
def Smoke_Alert():    
  if not Smoke_detector.value() and not H2_alarm_1.value() and not H2_alarm_2.value():  #Smoke detector has active LOW
    print('Smoke: Detected!')
    #Send wifi alarm:
    MarkVAlert = "\"1%_H2\":0, \"2%_H2\":0, \"Smoke\":1, \"Motion\":0"
    longAssPrefix = "{"+ MarkVAlert + ", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
    payload = longAssPrefix
    try:
      client.connect()
      client.publish(topic, payload)
      client.disconnect()
    except:
      pass
    #Show lights
    Smoke_Alert_Flash()
    #turn fan off
    

def Smoke_Alert_And_H2_1():
  if not Smoke_detector.value() and H2_alarm_1.value() and not H2_alarm_2.value(): 
    print('Smoke: Detected!')
    print('1% H2: Detected!')
#Send wifi alarm;
    MarkVAlert = "\"1%_H2\":1, \"2%_H2\":0, \"Smoke\":1, \"Motion\":0"
    longAssPrefix = "{"+ MarkVAlert + ", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
    payload = longAssPrefix
    try:
      client.connect()
      client.publish(topic, payload)
      client.disconnect()
    except:
      pass
#Show lights
    H2_Alert_Steady_Yellow()
    Smoke_Alert_Flash()
    #turn fan off


def Smoke_Alert_And_H2_2():

  if not Smoke_detector.value() and H2_alarm_2.value():
    print('Smoke: Detected!')
    print('2% H2: Detected!')
#Send wifi alarm:
    MarkVAlert = "\"1%_H2\":1, \"2%_H2\":1, \"Smoke\":1, \"Motion\":0"
    longAssPrefix = "{"+ MarkVAlert + ", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
    payload = longAssPrefix
    try:
      client.connect()
      client.publish(topic, payload)
      client.disconnect()
    except:
      pass
#Show lights:
    Smoke_Alert_Flash()
    #turn fan off
    
def IR_Sensor_Alert():
  if IR_Sensor.value():
    print('Movement Detected!')
#Send wifi alarm:
    MarkVAlert = "\"1%_H2\":0, \"2%_H2\":0, \"Smoke\":0, \"Motion\":1"
    longAssPrefix = "{"+ MarkVAlert + ", \"host_Name\":\"Arrgh_" + last4Mac + "\", \"On_line\":1, \"IP\":\"" + deviceIP + "\", \"Version\":\"" + Softversion + "\", \"Build\":\"" + Softbuild + "\"}"
    payload = longAssPrefix
    try:
      client.connect()
      client.publish(topic, payload)
      client.disconnect()
    except:
      pass
#Show Lights:
    Intrusion_Alert_Blink()
    

 
def Clear_All():
  if not H2_alarm_1.value() and not H2_alarm_2.value() and Smoke_detector.value() and not IR_Sensor.value():
    Yellow_Off()
    Red_Off()
    Transmitter_433.duty(0)

#--------------EXECUTING-----------------    

def MainLoop():
  H2_1_Alert()
  H2_2_Alert()
  Smoke_Alert()
  Smoke_Alert_And_H2_1()
  Smoke_Alert_And_H2_2()
  IR_Sensor_Alert()
  Clear_All()
  time.sleep(0.1)

#WarmupCycle()   


while True:
  MainLoop()
#-------------Reset if loop breaks-------

#def ReBoot():
  # configure RTC.ALARM0 to be able to wake the device
 # rtc = machine.RTC()
  #rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

  # set RTC.ALARM0 to fire after 10 seconds (waking the device)
  #rtc.alarm(rtc.ALARM0, 10000)

  # put the device to sleep
  #machine.deepsleep()

#print("Error: Loop Interrupted.  Resetting")
#for i in range(1,11):
 # print(i)
  #time.sleep(1)

#ReBoot()
#Or just machine.reset()?




