import os
import time
import json
import datetime
from tqdm import tqdm

times = []

for i in tqdm(range(200)):
    t = os.popen('sudo iwlist wlan0 scan | egrep "Cell|ESSID|Signal|Rates|Frequency"').read()
    cells = t.split('Cell')
    cur_time = datetime.datetime.now()
    networks = []
    for cel in cells[1:]:
        lns = cel.split('\n')

        a = lns[0].find('Address:')
        mac = lns[0][a+8:].strip()

        freq = float(lns[1].strip()[10:15])
        strength = float(lns[2].split('Signal level=')[-1].replace('dBm', '').strip())
        essid = lns[3].replace('ESSID:', '').replace('"', '').strip()

        networks.append({"mac": mac, "essid": essid, "frequency": freq, "strength": strength})
    times.append({"time": cur_time.strftime("%H:%M:%S"), "networks": networks})

    time.sleep(5.0)

f = open('wlan0_survey_records.json', 'w')
f.write(json.dumps(times))
f.close()
