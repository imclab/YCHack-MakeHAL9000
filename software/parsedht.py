import sys
import serial
import time
import os
import requests
import json
import pickle

block_list = []
machine_name = "old_raspi"

if not os.path.exists("data"):
    os.makedirs("data")

# remove old block
if os.path.exists(os.path.join('data', "block.blk")):
    os.remove(os.path.join('data', "block.blk"))

# save it to a block
if os.path.exists(os.path.join('data', "block.blk")):
    with open(os.path.join('data', 'block.blk'), 'rb') as f:
        block_list = pickle.load(f)
else:
    # create a blank block
    with open(os.path.join('data', 'block.blk'), 'wb') as f:
        pickle.dump(block_list, f)

url = "https://timeseriesvisual.firebaseio.com/raw.json"
device = "/dev/tty.usbmodemfa131"
ser = serial.Serial(device, 9600, timeout=5, parity="N", bytesize=8)

while True:
    line = ser.readline()
    if len(line) == 25:
		dht22 = map(lambda x:float(x), line.strip().split(' '))
		output_dhc22 = dict()
		output_dhc22["timestamp"] = time.time()
		output_dhc22["data"] = dict()
		output_dhc22["data"]["%s_humidity"%machine_name] = dht22[0]
		output_dhc22["data"]["%s_temperaturec"%machine_name] = dht22[1]
		output_dhc22["data"]["%s_temperaturef"%machine_name] = dht22[2]
		output_dhc22["data"]["%s_heatindexf"%machine_name] = dht22[3]

		block_list.append(output_dhc22)
		# create a blank block
		with open(os.path.join('data', 'block.blk'), 'wb') as output:
		    pickle.dump(block_list, output, pickle.HIGHEST_PROTOCOL)
		    print "save it to file"

		print len(block_list)

		# post to firebase
		response = requests.post(url, data=json.dumps(output_dhc22))
		print response