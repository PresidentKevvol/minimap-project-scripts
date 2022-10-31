import network
import time
import random
import socket
import urequests

# info for connecting to the parent network (the building's actual wifi)
parent_ssid = ""
parent_password = ""
# the ip of the pivot server
pivot_server_ip = "192.168.1.19"
pivot_server_url = pivot_server_ip + "/p/"

# the name of this beacon
beacon_name = 'SBU-01'

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
    pts_list = []
    for ap in accessPoints:
        pts_list.append({"SSID": ap[0], "BSSID": ap[1], "Channel": ap[2], "RSSI": ap[3]})

    # post request to report signal strengths
    payload = {"SourceName": beacon_name, "Points": payload}
    r = ''
    while r.find('info updated') < 0:
        r = urequests.post(pivot_server_url, json=payload)
        time.sleep(2.5)

    # sleep until next cycle
    time.sleep(10)
