import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)  #activate access point
ap_if.config(essid='Arrgh! Wifi H2 and Smoke Detector') #set ESP access point name

if ap_if.isconnected() and not sta_if.isconnected(): #?
  time.sleep(30)
  ssid = input('Enter network name: ')
  password = input('Enter password: ')
  sta_if.active(True)
  sta_if.connect(ssid, password)
print('network config: ', sta_if.ifconfig())

#connect to a WebRepl app?


