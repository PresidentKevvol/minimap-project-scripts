import network
import time
import random
import socket
import urequests

# info for connecting to the parent network (the building's actual wifi)
parent_info = open('parent.info', 'r')
parent_ssid = parent_info.readline().replace('\r', '').replace('\n', '')
parent_password = parent_info.readline().replace('\r', '').replace('\n', '')
# the ip of the pivot server
pivot_server_info = open('pivot_server.info', 'r')
pivot_server_ip = pivot_server_info.readline().replace('\r', '').replace('\n', '')
pivot_server_url = pivot_server_ip + "/p/"

# the name of this beacon and auth password if needed
self_info = open('self.info', 'r')
beacon_name = self_info.readline().replace('\r', '').replace('\n', '')
beacon_password = self_info.readline().replace('\r', '').replace('\n', '')

print("Info files Read.")

# the essid of the access point of this smart beacon unit
essid = beacon_name
# a completely random password (people are not supposed to connect to this access point)
password = str(random.randint(100000003, 999999999))

# setup access point
ap = network.WLAN(network.AP_IF)
ap.config(essid=essid, password=password)
ap.active(True)
print("Access point created.")

# now for connecting to the parent network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

#wlan.connect(parent_ssid, parent_password)

while True:
    # check if connection to parent stable
    while not wlan.isconnected():
        wlan.connect(parent_ssid, parent_password)
        print("Waiting for connection...")
        while not wlan.isconnected():
            time.sleep(1)
        print("Connected to parent network.")

    # scan all available access points
    accessPoints = wlan.scan()

    # send the scanned info to pivot as json
    pts_list = []
    for ap in accessPoints:
        pts_list.append({"SSID": ap[0].decode("utf-8"), "BSSID": ap[1].hex(), "Channel": ap[2], "RSSI": ap[3]})

    # post request to report signal strengths
    payload = {"SourceName": beacon_name, "Points": pts_list}
    r = ''
    while r.find('info updated') < 0:
        r = urequests.post("http://" + pivot_server_url, json=payload)
        r = r.text
        time.sleep(2.5)
    print("Reading data sent to pivot.")

    # sleep until next cycle
    time.sleep(10)
