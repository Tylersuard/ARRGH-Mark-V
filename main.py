#Main Coordinator Function/AKA Switchboard
#Sets up access point, assigns it an ESSID and password.
#Sets up station interface, checks if connected to a wifi network.
#If it IS, this script opens the main sensor loop.
#If it is NOT, this script opens the script for hosting the website for connecting the MarkV to a wifi network.

import network
import time

ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
ap_if.config(essid='Arrgh! Wifi H2 and Smoke Detector') #set ESP access point name
ap_if.config(password='Arrgh12345')
print("Local device network info: ")
print(ap_if.ifconfig())

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
print("Wifi Connection Network Info: ")
try:
    print(sta_if.ifconfig())
except:
    print("Not connected to a wifi network.")

time.sleep(1)

if not sta_if.isconnected():
    print("Mark V not connected, opening Network Connection Portal...")
    import Tywebsite2
   
elif sta_if.isconnected():
    print("Mark V connected, starting main sensor program...")
    import SensorsAndMQTT
    