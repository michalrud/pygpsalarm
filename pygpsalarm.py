# first version
# not even sure if it works, but what the hell, we're gonna try it later
# based on http://www.mobilenin.com/pys60/resources/bt_gps_reader.py


import appuifw, socket, e32

target = ''
# target = ('00:02:76:fd:c4:3a',1)    alternatively you can type here the Bluetooth address in HEX 
#                                     of your GPS reader. Then the phone connects directly to the GPS reader without
#                                     bringing up the BT device search dialog
lat = u"NaN"
lon = u"NaN"
stopChecking = False			# Will be set to true to break the loop.

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
        # Reading is done separately using a loop.
        #readData()
    except:
        if appuifw.query(u"GPS device problem. Try again?","query") == True:
            sock.close()

            connectGPS()
        else:
            sock.close()

def placeholder():
    appuifw.note(u"nothing to see here yet", "info")

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
                print "Press Options key!"
                #We don't want it to close the connection..
                #sock.close()
        else:
            pass
            
            
def positionChecking():
	global position, stopChecking
	#stopChecking = False
	while (stopChecking != True):
		e32.ao_sleep(1)
		readData()
		print (u"Lat: " + lat + u"\nLon: " + lon)

def exit_key_handler():
    script_lock.signal()
    sock.close()

script_lock = e32.Ao_lock()

print "Application initialized."

appuifw.app.title = u"PyGPSAlarm"
appuifw.app.menu = [(u"Connect to device", connectGPS),
                    (u"Enable position checking", positionChecking),
                    (u"Placeholder",
                        ((u"Placeholder 1", placeholder),
                         (u"Placeholder 2", placeholder))),
                    (u"Exit", exit_key_handler)]

#appuifw.app.exit_key_handler = exit_key_handler
script_lock.wait()
