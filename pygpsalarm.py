#    PyGPSAlarm, script that wakes you up according to your GPS location.
#    Copyright (C) 2008 Michał Rudowicz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# http://github.com/michalrud/pygpsalarm/
# With permission by Jürgen Scheible this application includes some code  from his PyS60 online tutorial http://www.mobilenin.com/pys60/resources/bt_gps_reader.py .

import appuifw, socket, e32, time

target = ''
# target = ('00:02:76:fd:c4:3a',1)    alternatively you can type here the Bluetooth address in HEX 
#                                     of your GPS reader. Then the phone connects directly to the GPS reader without
#                                     bringing up the BT device search dialog
lat = u"NaN"
lon = u"NaN"
stopChecking = False			# Will be set to true to break the loop.
bg = False

def connectGPS():
 global sock, target
 # create a bluetooth socket and connect to GPS receiver:  (if it is a Nokia LD-3W the PIN is: 0000)
 try:
  sock=socket.socket(socket.AF_BT,socket.SOCK_STREAM)
  if target == '':
   address,services = socket.bt_discover()
   print "Discovered: %s, %s"%(address, services)
   target = (address, services.values()[0])
  print "Connecting to " + str(target)
  sock.connect(target)
  appuifw.note(u"GPS successfully connected!", "info")
  print "connected!"
  connectedMenu()
  # Reading is done separately using a loop.
  #readData()
 except:
  if appuifw.query(u"GPS device problem. Try again?","query") == True:
   sock.close()
   connectGPS()
  else:
   sock.close()

def placeholder():
 appuifw.note(u"nothing to see here yet, see docs", "info")

def readData():
 global sock, position, lat, lon
 packet_received = 0
 print "reading ..."
 while(packet_received == 0):
  ch = sock.recv(1)
  # Loop until packet received
  buffer = ""
  while(ch !='\n'):
   buffer+=ch
   ch = sock.recv(1)
  if (buffer[0:6]=="$GPGGA"):
   gpsData = buffer.split(",")
   lat = gpsData[2]
   lon = gpsData[4]
   if lat == '' :
    pass
   else:
    packet_received = 1
    #let it be quiet
    #appuifw.note(u'Sucessful GPS location reading! ' + unicode(lat) + u' ' + unicode(lon), "info")
    position = [unicode(lat), unicode(lon)]
    print "reading done!"
    #print "Press Options key!"
    #We don't want it to close the connection yet
    #sock.close()
  else:
   pass
            
            
def disconnectGPS():
 try:
  stopChecking = True
  sock.close()
  disconnectedMenu()
 except:
  appuifw.note(u"Error. Maybe we haven't started yet? Only god knows.", "error")

def positionChecking():
 global position, stopChecking
 wasInBackground = False
 checkingMenu()
 # If we put app to background, and then take it back to the foreground,
 # checking will stop.
 while ((wasInBackground == False) or (bg == True)): 
  e32.ao_sleep(1)
  if bg == True: wasInBackground = True
  readData()
  print (u"Lat: " + lat + u"\nLon: " + lon)
 connectedMenu()

def exit_key_handler():
 script_lock.signal()
 sock.close()
 
############# MENU ##################
def disconnectedMenu():
 # Menu that appears when we are disconnected.
 appuifw.app.menu = [(u"Connect to device", connectGPS),
                     (u"Exit", exit_key_handler)]

def connectedMenu():
 # Menu that appears when we are connected.
 appuifw.app.menu = [(u"Enable position checking", positionChecking),
                     (u"Disconnect from device", disconnectGPS),
                     (u"Exit", exit_key_handler)]
                     
def checkingMenu():
 # Menu that appears when we are checking our position.
 appuifw.app.menu = [(u"Disable position checking", placeholder),
                     (u"Exit", exit_key_handler)]
                     
############# MENU ##################

# Setting proper value to bg when app is in foreground or background.
def inBackground(status):
 global bg
 if(status==0): bg = True
 else: bg = False

script_lock = e32.Ao_lock()

appuifw.app.focus = inBackground
appuifw.app.title = u"PyGPSAlarm"
disconnectedMenu()
print "Application initialized."
appuifw.app.exit_key_handler = exit_key_handler
script_lock.wait()
