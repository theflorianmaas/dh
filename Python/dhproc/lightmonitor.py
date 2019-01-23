#!/usr/bin/env python3
"""
This is an example of how the pytradfri-library can be used async.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_async.py)
$ python3 example_async.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

# Hack to allow relative import above top level package
import sys
import os
folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

import asyncio
import uuid
import argparse
import json
import datetime

lightArrayId = []
lightArraySts = []
lightArrayColor = []
lightArrayValue = []

groupArrayId = []
groupArraySts = []
groupArrayValue = []
groupArrayMood = []

def output(x):
	print(str(datetime.datetime.now().time())[:8] + " "+ str(x))
	sys.stdout.flush()

def get_color_temp_idx(color):
	if color == 'dcf0f8':
		c=4
	elif color == 'eaf6fb':
		c=5
	elif color == 'f5faf6':
		c=1		
	elif color == 'f2eccf':
		c=6	
	elif color == 'f1e0b5':
		c=2
	elif color == 'efd275':
		c=3		
	elif color == 'ebb63e':
		c=7		
	elif color == 'e78834':
		c=8		
	elif color == 'e57345':
		c=9		
	elif color == 'da5d41':
		c=10		
	elif color == 'dc4b31':
		c=11		
	elif color == 'e491af':
		c=12		
	elif color == 'e8bedd':
		c=13		
	elif color == 'd9337c':
		c=14		
	elif color == 'c984bb':
		c=15
	elif color == '8f2686':
		c=16
	elif color == '4a418a':
		c=17
	elif color == '6c83ba':
		c=18
	elif color == 'a9d62b':
		c=19
	elif color == 'd6e44b':
		c=20
	else: 
		c=1
	return c	


CONFIG_FILE = 'tradfri_standalone_psk.conf'

parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='IP', type=str,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Key found on your Tradfri gateway')
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print("Please provide the 'Security Code' on the back of your "
          "Tradfri gateway:", end=" ")
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


try:
    # pylint: disable=ungrouped-imports
    from asyncio import ensure_future
except ImportError:
    # Python 3.4.3 and earlier has this as async
    # pylint: disable=unused-import
    from asyncio import async
    ensure_future = async


def savelights():
    i = 0
    lista = "" 
    for id in lightArrayId: 
		# scrivi record
        lista = lista + str(lightArrayId[i])
        lista = lista +  ","
        lista = lista + str(lightArraySts[i])
        lista = lista +  ","
        lista = lista + str(lightArrayValue[i])
        lista = lista +  ","
        lista = lista + str(lightArrayColor[i])
        lista = lista +  ","     
        i += 1
    wfile = open ("files/datafile.json", "w")
    wfile.write(lista)
    wfile.close()
    output("file salvato")    
    
def get_index(id, list_):
	for i, s in enumerate(list_):	
		if str(id) == str(s):			
			return i
	return -1	    


@asyncio.coroutine
def run():
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get('identity')
        psk = conf[args.host].get('key')
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)

        try:
            psk = yield from api_factory.generate_psk(args.key)
            print('Generated PSK: ', psk)

            conf[args.host] = {'identity': identity,
                               'key': psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError:
            raise PytradfriError("Please provide the 'Security Code' on the "
                                 "back of your Tradfri gateway using the "
                                 "-K flag.")

    api = api_factory.request

    gateway = Gateway()

  
    devices_command = gateway.get_devices()
    devices_commands = yield from api(devices_command)
    devices = yield from api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]
    
    #insert lights in the arrays
    for light in lights:
        lightArrayId.append(light.id)
        lightArraySts.append(light.light_control.lights[0].state)
        lightArrayValue.append(light.light_control.lights[0].dimmer)
        lightArrayColor.append(get_color_temp_idx(light.light_control.lights[0].hex_color))        
    
    savelights()
	
    # Lights can be accessed by its index, so lights[1] is the second light
    if lights:
        light = lights[0]
    else:
        print("No lights found!")
        light = None

    def observe_callback(updated_device):
        light = updated_device.light_control.lights[0]
        output("Received message for: %s" % light)
        light = updated_device
        x = get_index(light.id, lightArrayId)
        lightArraySts[x] = light.light_control.lights[0].state
        lightArrayValue[x] = light.light_control.lights[0].dimmer
        lightArrayColor[x] = get_color_temp_idx(light.light_control.lights[0].hex_color)
        savelights()

    def observe_err_callback(err):
        output('observe error:', err)

    for light in lights:
        observe_command = light.observe(observe_callback, observe_err_callback,
                                        duration=120)
        # Start observation as a second task on the loop.
        ensure_future(api(observe_command))
        # Yield to allow observing to start.
        yield from asyncio.sleep(0)

    print("Waiting for observation to end (2 mins)")
    print("Try altering any light in the app, and watch the events!")
    while True:
	    print("restart")
	    yield from asyncio.sleep(10)

    #yield from api.shutdown()


asyncio.get_event_loop().run_until_complete(run())
