#1. Sets up ESP as access point for cell phone to connect to its wifi
#2. Hosts website for user to input their network name and password
#3. Prints SSID and password and assigns them to variables Net_SSID and Net_Pass.  These will be passed
#along to DoConnect2.py

import socket
import network

ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)  #activate access point
ap_if.config(essid='Arrgh! Wifi H2 and Smoke Detector') #set ESP access point name
ap_if.config(password='Arrgh12345')
print("ESSID: ")
print(essid)
print('Password: ')
print(password)
print("Local device network info: ")
print(ap_if.ifconfig())


#HTML to send to browsers
html = """<!DOCTYPE html>
<html>
<head> <title>ARRGH!  Mark V Smoke/Hydrogen Detector</title> </head>
<h2>Arrgh Mark V Smoke and Hydrogen Detector</h2></center>
<h3>To connect to wifi: Type in network name and password<br>
then click "Connect".</h3></center>
<form>
ESSID: <br><input type="text" class="text" name="ESSID"><br>
Password: <br><input type="password" class="text" name="password"><br>
<input type="hidden" name="poo">
<input type="submit" value="Connect">  
</form>
</html>
"""
#maybe change the above html so that the input type = password for the Password, that way the input is masked.
def NetworkPortal():
  server = socket.socket()  #This creates a socket named server
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #lets you reuse the same IP and port
  server.bind(('0.0.0.0', 80))  #This is pretty much naming the socket that you created.  Can't connect to the socket until you do this.
  server.listen(5)
  print("Listening, connect your browser to 192.168.4.1:80")

  while True:
    res = server.accept()
    client_s = res[0]
    client_addr = res[1]
    req = client_s.recv(4096)
    req_Decoded = req.decode('utf-8')
    print(req_Decoded)
    try:
      req_Dec_no_plus = req_Decoded.replace('+','')
      Net_SSID = req_Dec_no_plus[(req_Dec_no_plus.index("ID=")+3):(req_Dec_no_plus.index("&pa"))]
      print('Network SSID:')
      print(Net_SSID) 
      Net_Pass = req_Dec_no_plus[(req_Dec_no_plus.index("rd=")+3):(req_Dec_no_plus.index("&poo"))]
      print('Network Password:')
      print(Net_Pass)
      sta_if = network.WLAN(network.STA_IF)
      sta_if.active(True)  
      sta_if.connect(Net_SSID, Net_Pass)
      print('network config: ', sta_if.ifconfig())
      break
    except:
      print('try again!')
      client_s.send(html)
      client_s.close()
      print()
        
NetworkPortal()
client_s.close() #is this necessary?
import SensorsAndMQTT