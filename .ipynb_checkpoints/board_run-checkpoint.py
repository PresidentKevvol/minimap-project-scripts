import network
import time
import random
import socket

# info for connecting to the parent network (the building's actual wifi)
parent_ssid = ""
parent_password = ""
# the ip of the pivot server
pivot_server_ip = "192.168.1.19"

# the name of this beacon
beacon_name = ''

# the essid of the access point of this smart beacon unit
essid = "SBU-01"
# a completely random password (people are not supposed to connect to this access point)
password = str(random.randint(100000003, 999999999))

# setup access point
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password) 
ap.active(True)


# now for connecting to the parent network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(parent_ssid, parent_password)
if not wlan.isconnected():
    wlan.connect()
    # print("Waiting for connection...")
while not wlan.isconnected():
    time.sleep(1)

while True:
    # scan all available access points
    accessPoints = wlan.scan()

    # send the scanned info to pivot as json
    payload = ""
    for ap in accessPoints: 
        payload += ('{"SSID": "' + ap[0] + '", "Channel": "' + ap[2] + '", "RSSI": "' + ap[3] + '"},')
    payload = "[" + payload + "]"
    
    # setup the socket
    addr = socket.getaddrinfo(pivot_server_ip, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    
    # post request to report signal strengths
    payload = '{"SourceName": "' + beacon_name + '", "Points": ' + payload + '}'
    content = 'POST /p/ HTTP/1.1\r\n' + \
        'Host: ' + pivot_server_ip + '\r\n' + \
        'Accept: application/json\r\n' + \
        'Content-Type: application/json\r\n' + \
        'Content-Length: ' + str(len(payload)) + '\r\n\r\n' + \
        payload

    s.send(content.encode('utf-8'))
    data = s.recv(1000)
    s.close()
    
    # sleep until next cycle
    time.sleep(10)