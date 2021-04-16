import sys
import json
import time
import requests
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import sync_sem
import mesh_beacons
import mesh_subnets
from byte_codec import uint8
from byte_codec import uint16

ACC_URL = 'https://api.nrfcloud.com/v1/account'
DEV_URL = 'https://api.nrfcloud.com/v1/devices'
AUTH_BEARER_PREFIX = 'Bearer '
PORT                = 8883
KEEP_ALIVE          = 30

APP_KEY_REQ = {
        'id': 'randomId',
        'type': 'operation',
        'operation': {
            'type': 'app_key_request'
            }
        }

NODE_REQ = {
        'id': 'randomId',
        'type': 'operation',
        'operation': {
            'type': 'node_request'
            }
        }

MODEL_ID_PARSE = {
        0x0000: 'Configuration Server',
        0x0001: 'Configuration Client',
        0x0002: 'Health Server',
        0x0003: 'Health Client',
        0x1000: 'Generic OnOff Server',
        0x1001: 'Generic OnOff Client',
        0x1002: 'Generic Level Server',
        0x1003: 'Generic Level Client',
        0x1004: 'Generic Default Transition Time Server',
        0x1005: 'Generic Default Transition Time Client',
        0x1006: 'Generic Power OnOff Server',
        0x1007: 'Generic Power OnOff Setup Server',
        0x1008: 'Generic Power OnOff Client',
        0x1009: 'Generic Power Level Server',
        0x100A: 'Generic Power Level Setup Server',
        0x100B: 'Generic Power Level Client',
        0x100C: 'Genreic Battery Service',
        0x100D: 'Generic Location Server',
        0x100E: 'Generic Location Server',
        0x100F: 'Generic Location Setup Server',
        0x1010: 'Generic Locatino Client',
        0x1011: 'Generic Admin Property Server',
        0x1012: 'Generic Manufacturer Property Server',
        0x1013: 'Generic User Property Server',
        0x1014: 'Generic Client Property Server',
        0x1015: 'Generic Property Client Server',
        0x1100: 'Sensor Sensor',
        0x1101: 'Sensor Setup Server',
        0x1102: 'Sensor Client',
        0x1200: 'Time Server',
        0x1201: 'Time Setup Server',
        0x1202: 'Time Client',
        0x1203: 'Scene Server',
        0x1204: 'Scene Setup Server',
        0x1205: 'Scene Client',
        0x1206: 'Scheduler Server',
        0x1207: 'Scheduler Setup Server',
        0x1208: 'Scheduler Client',
        0x1300: 'Light Lightness Server',
        0x1301: 'Light Lightness Setup Server',
        0x1302: 'Light Lightness Client',
        0x1303: 'Light CTL Server',
        0x1304: 'Light CTL Setup Server',
        0x1305: 'Light CTL Client',
        0x1307: 'Light HSL Server',
        0x1308: 'Light HSL Setup Server',
        0x1309: 'Light HSL Client',
        0x130A: 'Light HSL Hue Server',
        0x130B: 'Light HSL Saturation Server',
        0x130C: 'Light xyL Server',
        0x130D: 'Light xyL Setup Server',
        0x130E: 'Light xyL Client',
        0x130F: 'Light LC Server',
        0x1310: 'Light LC Setup Server',
        0x1311: 'Light LC Client'
        }

SERVER_MODEL_MSGS = {
        'Generic OnOff': [
            'Generic OnOff Get',
            'Generic OnOff Set',
            'Generic OnOff Set Unacknowledged',
            ],
        'Generic Level': [
            'Generic Level Get',
            'Generic Level Set',
            'Generic Level Set Unacknowledged',
            'Generic Delta Set',
            'Generic Delta Set Unacknowledged',
            'Generic Move Set',
            'Generic Mode Set Unacknowledged'
            ],
        'Generic Default Transition Time': [
            'Generic Default Transition Time Get',
            'Generic Default Transition Time Set',
            'Generic Default Transition Time Set Unacknowledged',
            ],
        'Generic Power OnOff': [
            'Generic OnPowerUp Get',
            ],
        'Generic Power OnOff Setup': [
            'Generic OnPowerUp Set',
            'Generic OnPowerUp Set Unacknowledged'
            ],
        'Generic Power Level': [
            'Generic Power Level Get',
            'Generic Power Level Set',
            'Generic Power Level Set Unacknowledged',
            'Generic Power Last Get',
            'Generic Power Default Get',
            'Generic Power Range Get',
            ],
        'Generic Power Level Setup': [
            'Generic Power Default Set',
            'Generic Power Default Set Unacknowledged',
            'Generic Power Range Set',
            'Generic Power Range Set Unacknowledged'
            ],
        'Generic Battery': [
            'Generic Battery Get',
            ],
        'Generic Location': [
            'Generic Location Global Get',
            'Generic Location Local Get',
            ],
        'Generic Location Setup': [
            'Generic Location Global Set',
            'Generic Location Global Set Unacknowledged',
            'Generic Location Local Set',
            ],
        'Generic Manufacturer Property': [
            'Generic Manufacturer Properties Get',
            'Generic Manufacturer Property Get',
            'Generic Manufacturer Property Set',
            'Generic Manufacturer Property Set Unacknowledged',
            ],
        'Generic Admin Property': [
            'Generic Admin Properties Get',
            'Generic Admin Property Get',
            'Generic Admin Property Set',
            'Generic Admin Property Set Unacknowledged',
            ],
        'Generic User Property': [
            'Generic User Properties Get',
            'Generic User Property Get',
            'Generic User Property Set',
            'Generic User Property Set Unacknowledged',
            ],
        'Generic Client Property': [
            'Generic Client Properties Get',
            ]
        }

MODEL_MSG_OPCODES = {
        'Generic OnOff Get': 0x8201,
        'Generic OnOff Set': 0x8202,
        'Generic OnOff Set Unacknowledged': 0x8203,
        'Generic OnOff Status': 0x8204,
        'Generic Level Get': 0x8205,
        'Generic Level Set': 0x8206,
        'Generic Level Set Unacknowledged': 0x8207,
        'Generic Delta Set': 0x8209,
        'Generic Delta Set Unacknowledged': 0x820A,
        'Generic Move Set': 0x820B,
        'Generic Mode Set Unacknowledged': 0x820C,
        'Generic Default Transition Time Get': 0x820D,
        'Generic Default Transition Time Set': 0x820E,
        'Generic Default Transition Time Set Unacknowledged': 0x820F,
        'Generic OnPowerUp Get': 0x8211,
        'Generic OnPowerUp Set': 0x8213,
        'Generic OnPowerUp Set Unacknowledged': 0x8214,
        'Generic Power Level Get': 0x8215,
        'Generic Power Level Set': 0x8216,
        'Generic Power Level Set Unacknowledged': 0x8217,
        'Generic Power Last Get': 0x8219,
        'Generic Power Default Get': 0x821B,
        'Generic Power Range Get': 0x821D,
        'Generic Power Default Set': 0x821F,
        'Generic Power Default Set Unacknowledged': 0x8220,
        'Generic Power Range Set': 0x8221,
        'Generic Power Range Set Unacknowledged': 0x8222,
        'Generic Battery Get': 0x8223,
        'Generic Location Global Get': 0x8225,
        'Generic Location Local Get': 0x8226,
        'Generic Location Global Set': 0x41,
        'Generic Location Global Set Unacknowledged': 0x42,
        'Generic Location Local Set': 0x8228,
        'Generic Manufacturer Properties Get': 0x822A,
        'Generic Manufacturer Property Get': 0x822B,
        'Generic Manufacturer Property Set': 0x44,
        'Generic Manufacturer Property Set Unacknowledged': 0x45,
        'Generic Admin Properties Get': 0x822C,
        'Generic Admin Property Get': 0x822D,
        'Generic Admin Property Set': 0x48,
        'Generic Admin Property Set Unacknowledged': 0x49,
        'Generic User Properties Get': 0x822E,
        'Generic User Property Get': 0x822F,
        'Generic User Property Set': 0x4C,
        'Generic User Property Set Unacknowledged': 0x4D,
        'Generic Client Properties Get': 0x4F,
        }


verbose = False
app_key_list = []
node_list = []
node = {}
prov_result = {}
subsciption_list = {}
live = True
getting_input = False
tid = 0


def publish(msg):
    client.publish(c2g_topic, payload=json.dumps(msg), qos=0, retain=False)

def print_app_keys():
    global app_key_list

    print('Application Keys')
    print('    App Index : Net Index')
    for app_key in app_key_list:
        print('     - ' + uint16(app_key['appIndex']) + ' : ' + uint16(app_key['netIndex']))
    
    if len(app_key_list) == 0:
        print('     No Application Keys')
    
    print()

def print_prov_result():
    global prov_result

    if prov_result['error'] != 0:
        print('Failed to provision device with UUID: ' + prov_result['uuid'])
        print('    Error: ' + int(prov_result['error']))
        return

    print('Provision Result:')
    print('  - UUID         : ' + prov_result['uuid'])
    print('  - Net Index    : ' + uint16(prov_result['netIndex']))
    print('  - Address      : ' + uint16(prov_result['address']))
    print('  - Element Count: ' + uint16(prov_result['elementCount']))
    print()

def print_nodes():
    global node_list

    print('Network Nodes:')
    for node in node_list:
        if node['address'] == 1:
            print('    Address      : ' + uint16(node['address']) + ' (Gateway)')
        else:
            print('    Address      : ' + uint16(node['address']))
        print('    Device Type  : ' + node['deviceType'])
        print('    UUID         : ' + node['uuid'])
        print('    Network Index: ' + uint16(node['netIndex']))
        print('    Element Count: ' + str(node['elementCount']))
        print()
        
    if len(node_list) == 0:
        print('    No Nodes')
        print()


def print_node():
    global node

    print('Node: ' + uint16(node['address']))
    print('    UUID: ' + node['uuid'])
    print('    CID : ' + uint16(node['cid']))
    print('    PID : ' + uint16(node['pid']))
    print('    VID : ' + uint16(node['vid']))
    print('    CRPL: ' + uint16(node['crpl']) + '\n')
    
    if node['networkBeaconState']:
        print('    Network Beacon ENABLED')
    else:
        print('    Network Beacon DISABLED')
    print('    Time-to-live: ' + uint8(node['timeToLive']) + '\n')

    relay = node['relayFeature']
    print('    Relay Feature:')
    if relay['support']:
        print('        Supported')
        if relay['state']:
            print('        Enabled')
        else:
            print('        Disabled')
        print('        Retransmission Count   : ' + uint8(relay['retransmitCount']))
        print('        Retransmission Interval: ' + uint8(relay['retransmitInterval']))
    else:
        print('        NOT Supported')

    proxy = node['proxyFeature']
    print('    GATT Proxy Feature:')
    if proxy['support']:
        print('        Supported')
        if proxy['state']:
            print('        Enabled')
        else:
            print('        Disabled')
    else:
        print('        NOT Supported')

    friend = node['friendFeature']
    print('    Friend Feature:')
    if friend['support']:
        print('        Supported')
        if friend['state']:
            print('        Enabled')
        else:
            print('        Disabled')
    else:
        print('        NOT Supported')

    lpn = node['lpnFeature']
    print('    Low Power Node Feature:')
    if lpn['state']:
        print('        Supported')
    else:
        print('        NOT Supported')

    print('    Subnets:')
    for subnet in node['subnets']:
        print('        - ' + uint16(subnet))

    for idx, element in enumerate(node['elements']):
        if element['address'] == node['address']:
            print('    Element ' + uint16(idx) + ' (PRIMARY):')
        else:
            print('    Element ' + uint16(idx) + ':')
        
        print('        Address: ' + uint16(element['address']))
        print('        LOC    : ' + uint16(element['address']) + '\n')

        for model in element['sigModels']:
            print('        SIG Model ' + uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            print('            Application Keys:')
            if len(model['appKeyIndexes']) == 0:
                print('              None')
            for app_key in model['appKeyIndexes']:
                print('            - ' + uint16(app_key))
            print('            Subscribed Addresses:')
            if len(model['subscribeAddresses']) == 0:
                print('              None')
            for addr in model['subscribeAddresses']:
                print('            - ' + uint16(addr))
            print('            Publish Parameters:')
            pub = model['publishParameters']
            print('                Address               : ' + uint16(pub['address']))
            print('                Application Key Index : ' + uint16(pub['appKeyIndex']))
            if pub['friendCredentialFlag']:
                print('                Friend Credential Flag: Enabled')
            else:
                print('                Friend Credential Flag: Disabled')
            print('                Time-to-live          : ' + uint8(pub['timeToLive']))
            print('                Period                : ' + uint8(pub['period']))
            print('                Period Units          : ' + pub['periodUnits'])
            print('                Retransmit Count      : ' + uint8(pub['retransmitCount']))
            print('                Retransmit Interval   : ' + uint8(pub['retransmitInterval']))
            print()

        for model in element['vendorModels']:
            print('        Vendor Model ' + uint16(model['modelId']))
            print('            Vendor ID: ' + uint16(model['companyId']))
            print('            Application Keys:')
            if len(model['appKeyIndex']) == 0:
                print('              None')
            for app_key in model['appKeyIndex']:
                print('            - ' + uint16(app_key))
            print('            Subscribed Addresses:')
            if len(model['subscribeAddresses']) == 0:
                print('              None')
            for addr in model['subscribeAddresses']:
                print('            - ' + uint16(addr))
            print('            Publish Parameters:')
            pub = model['publishParameters']
            print('                Address               : ' + uint16(pub['address']))
            print('                Application Key Index : ' + uint16(pub['appKeyIndex']))
            if pub['friendCredentialFlag']:
                print('                Friend Credential Flag: Enabled')
            else:
                print('                Friend Credential Flag: Disabled')
            print('                Time-to-live          : ' + uint8(pub['timeToLive']))
            print('                Period                : ' + uint8(pub['period']))
            print('                Period Units          : ' + pub['periodUnits'])
            print('                Retransmit Count      : ' + uint8(pub['retransmitCount']))
            print('                Retransmit Interval   : ' + uint8(pub['retransmitInterval']))
            print()

def print_subscription_list():
    global subscription_list

    print('Subscribed Addresses:')
    for sub in subscription_list:
        print('  - ' + uint16(sub['address']))

    if len(subscription_list) == 0:
        print('    No subscribed addresses')

    print()

def build_node_disc_json(address):
    node_disc = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'node_discover',
                'address': address
                }
            }

    return node_disc

def provision():
    global beacon_list

    print("Getting unprovisioned device beacons from gateway...\n")
    publish(BEACON_REQ)
    if not sem.acquire():
        return

    if len(beacon_list) == 0:
        print('No device beacons to provision\n')
        return

    choices = []
    for beacon in beacon_list:
        choices.append(beacon['uuid'])
    print("Which device would you like to provision?")
    choice = get_choice(choices)
    
    uuid = choices[choice]
    print('Provisioning ' + uuid)
    net_idx = int(input('Enter 16-bit network index: '))
    addr = int(input('Enter 16-bit address: '))
    attn_time = int(input('Enter the attention timer for the provisioning process: '))

    print('Sending provision device request. This may take several minutes...\n')
    prov = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'provision',
                'uuid': uuid,
                'netIndex': net_idx,
                'address': addr,
                'attentionTime': attn_time
                }
            }
    publish(prov)
    if not sem.acquire():
        return
    
    print_prov_result()

def app_key_menu():
    global app_key_list
    global subnet_list
    global sem

    choices = ['Add Application Key', 'Generate Application Key', 'Delete Application Key',
            'Get Application Keys']
    print('APPLICATION KEY CONFIGURATION MENU')
    choice = get_choice(choices)

    if choice == 0:
        net_idx = subnets.get_choice(sem, publish)
        if net_idx == None:
            return

        app_key = input('\nEnter 128-bit application key in hexadecimal format: ')
        app_idx = int(input('Enter unsigned 16-bit application index for the application key: '), 0)
        app_key_add = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'app_key_add',
                    'appKey': app_key,
                    'appIndex': app_idx,
                    'netIndex': net_idx
                    }
                }
        print('Adding application key...')
        publish(app_key_add)
        if not sem.acquire():
            return
        print_app_keys()

    elif choice == 1:
        net_idx = subnets.get_choice(sem, publish)
        if net_idx == None:
            return

        app_idx = int(input('\nEnter unsigned 16-bit application index for the application key: '), 0)
        app_key_gen = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'app_key_generate',
                    'appIndex': app_idx,
                    'netIndex': net_idx
                    }
                }
        print('Generating application key...')
        publish(app_key_gen)
        if not sem.acquire():
            return
        print_app_keys()

    elif choice == 2:
        publish(APP_KEY_REQ)
        if not sem.acquire():
            return

        choices = []
        for app_key in app_key_list:
            choices.append(uint16(app_key['appIndex']))

        if len(choices) == 0:
            print('No application keys to delete')
            return

        print('Which application key would you like to delete?')
        choice = get_choice(choices)
        app_idx = int(choices[choice], 0)
        
        app_key_del = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'app_key_delete',
                    'appIndex': app_idx
                    }
                }
        print('Deleting application key...')
        publish(app_key_del)
        if not sem.acquire():
            return
        print_app_keys()

    elif choice == 3:
        print('Getting application keys...')
        publish(APP_KEY_REQ)
        if not sem.acquire():
            return
        print_app_keys()

def node_request():
    print('Getting network nodes from gateway...')
    publish(NODE_REQ)
    if not sem.acquire():
        return
    print_nodes()

def node_discover():
    global node_list
    global node

    print('Acquiring nodes from gateway...\n')
    publish(NODE_REQ)
    if not sem.acquire():
        return

    choices = []
    for node in node_list:
        if node['address'] != 1:
            choices.append(uint16(node['address']))

    if len(choices) == 0:
        print('No nodes in network to discover\n')
        return

    print('Which node would you like to discover?')
    choice = get_choice(choices)

    print('Discovering node. This may take a few minutes...')
    publish(build_node_disc_json(int(choices[choice], 0)))
    if not sem.acquire():
        return
    print_node()

def get_state_choice():
    choices = ['ENABLE', 'DISABLE']
    choice = get_choice(choices)

    if choice == 0:
        return True
    elif choice == 1:
        return False

def node_configure():
    global subnet_list
    global app_key_list
    global node_list
    global node
    global sem

    print('Acquiring nodes from gateway...')
    publish(NODE_REQ)
    if not sem.acquire():
        return

    choices = []
    for node in node_list:
        if node['address'] != 1:
            choices.append(uint16(node['address']))

    if len(choices) == 0:
        print('No nodes in network to configure\n')
        return

    print('Which node would you like to configure?')
    choice = get_choice(choices)

    address = int(choices[choice], 0)

    choices = ['Set Network Beacon', 'Set Time-to-Live', 'Set Relay Feature',
            'Set GATT Proxy Feature', 'Set Friend Feature', 'Add Subnet', 'Delete Subnet',
            'Bind Application Key', 'Unbind Application Key', 'Set Publish Parameters',
            'Add Subscribe Address', 'Delete Subscribe Address', 'Overwrite Subscribe Addresses']
    print('What configuration would you like to perform?')
    choice = get_choice(choices)

    if choice == 0:
        # Set Network Beacon
        print('Do you want ENABLE or DISABLE the Network Beacon?')
        state = get_state_choice()
        op = {
                'type': 'node_configure',
                'configuration': 'networkBeaconSet',
                'nodeAddress': address,
                'state': state
                }

    elif choice == 1:
        # Set Time-to-Live
        ttl = int(input('Enter unsigned 8-bit time-to-live: '), 0)
        op = {
                'type': 'node_configure',
                'configuration': 'timeToLiveSet',
                'nodeAddress': address,
                'value': ttl
                }

    elif choice == 2:
        # Set Relay Feature
        print('Do you want to ENABLE or DISABLE the Relay Feature?')
        state = get_state_choice()
        count = int(input('Enter unsigned 8-bit retransmit count: '), 0)
        interval = int(input('Enter unsigned 16-bit retransmit interval: '), 0)
        op = {
                'type': 'node_configure',
                'configuration': 'relayFeatureSet',
                'nodeAddress': address,
                'state': state,
                'retransmitCount': count,
                'retransmitInterval': interval
                }
        
    elif choice == 3:
        # Set Proxy Feature
        print('Do you want to ENABLE or DISABLE the GATT Proxy Feature?')
        state = get_state_choice()
        op = {
                'type': 'node_configure',
                'configuration': 'proxyFeatureSet',
                'nodeAddress': address,
                'state': state
                }

    elif choice == 4:
        # Set Friend Feature
        print('Do you want to ENABLE or DISABLE the Friend Feature?')
        state = get_state_choice()
        op = {
                'type': 'node_configure',
                'configuration': 'friendFeatureSet',
                'nodeAddress': address,
                'state': state
                }

    elif choice == 5:
        # Add Subnet
        net_idx = subnets.get_choice(sem, publish)
        if net_idx == None:
            return
        op = {
                'type': 'node_configure',
                'configuration': 'subnetAdd',
                'nodeAddress': address,
                'netIndex': net_idx
                }

    elif choice == 6:
        # Delete Subnet
        print('Acquiring subnets from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for subnet in node['subnets']:
            choices.append(uint16(subnet))
        print('Which subnet would you like to delete from the node?')
        choice = get_choice(choices)
        net_idx = int(chocies[choice], 0)
        op = {
                'type': 'node_configure',
                'configuration': 'subnetDelete',
                'nodeAddress': address,
                'netIndex': net_idx
                }

    elif choice == 7:
        # Bind Application Key
        print('Acquiring application keys from gateway...')
        publish(APP_KEY_REQ)
        if not sem.acquire():
            return
        print('Acquiring elements and models from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for app_key in app_key_list:
            choices.append(uint16(app_key['appIndex']))
        if len(choices) == 0:
            print('No application keys on the gateway to bind to model')
            return
        print('Which application key would you like to bind to the model?')
        choice = get_choice(choices)
        app_idx = int(choices[choice], 0)

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models to bind application keys to')
            return
        print('Which element has the model you would like to bind an application key to?')
        choice = get_choice(choices)
        elem_addr = int(choices[choice], 0)

        choices = []
        for model in node['elements'][choice]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to bind application keys to')
            return
        print('Which model would you like to bind an application key to?')
        choice = get_choice(choices)
        model_id = int(choices[choice][:6], 0)

        op = {
                'type': 'node_configure',
                'configuration': 'appKeyBind',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'appIndex': app_idx
                }

    elif choice == 8:
        # Unbind Application Key
        print('Acquiring elements, models and application keys from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models to unbind an application key from')
            return;
        print('Which element has the the model you would like to unbind an application key from?')
        element = get_choice(choices)
        elem_addr = int(choices[element], 0)

        choices = []
        for model in node['elements'][element]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to unbind an application key from')
            return;
        print('Which model would you like to unbind an application key from?')
        model = get_choice(choices)
        model_id = int(choices[model], 0)

        choices = []
        for app_key in node['elements'][element]['sigModels'][model]['appKeyIndexes']:
            choices.append(uint16(app_key))
        if len(choices) == 0:
            print('No application keys to unbind on model')
            return
        print('Which application key would you like to unbind from this model?')
        app_key = get_choice(choices)
        app_idx = int(choices[app_key], 0)

        op = {
                'type': 'node_configure',
                'configuration': 'appKeyUnbind',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'appIndex': app_idx
                }

    elif choice == 9:
        # Set Publish Parameters
        print('Acquiring application keys from gateway...')
        publish(APP_KEY_REQ)
        if not sem.acquire():
            return
        print('Acquiring elements, models and application keys from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models that can have their publish parameters set')
            return;
        print('Which element has the the model you would like to set the publish parameters for?')
        element = get_choice(choices)
        elem_addr = int(choices[element], 0)

        choices = []
        for model in node['elements'][element]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to set publish parameters for')
            return;
        print('Which model would you like to set the publish parameters for?')
        model = get_choice(choices)
        model_id = int(choices[model][:6], 0)
        
        choices = []
        for app_key in app_key_list:
            choices.append(uint16(app_key['appIndex']))
        if len(choices) == 0:
            print('No application keys on the gateway to set as publish parameter for this model')
            return
        print('Which application key would you like this model to publish with?')
        choice = get_choice(choices)
        app_idx = int(choices[choice], 0)
        

        pub_addr = int(input('Enter unsigned 16-bit address for this model to publish to: '), 0)

        print('Would you like to ENABLE or DISABLE this model\'s publish friend credential flag?')
        cred_flag = get_state_choice()

        ttl = int(input('Enter unsigned 8-bit value for this model\'s Publish Time-to-Live: '), 0)

        choices = ['100ms', '1s', '10s', '10m']
        print('Which unit would you like to use for this models Publish Period?')
        units = choices[get_choice(choices)]

        period = int(input('Enter unsigned 8-bit value for this models Publish Period in the selected units: '), 0)

        count = int(input('Enter unsigned 8-bit value for this model\'s Retransmit Count: '), 0)

        interval = int(input('Enter unsigned 16-bit value for this model\'s Retransmit Interval: '), 0)

        op = {
                'type': 'node_configure',
                'configuration': 'publishParametersSet',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'publishAddress': pub_addr,
                'appIndex': app_idx,
                'friendCredentialFlag': cred_flag,
                'timeToLive': ttl,
                'period': period,
                'periodUnits': units,
                'retransmitCount': count,
                'retransmitInterval': interval
                }

    elif choice == 10:
        # Add Subscribe Address
        print('Acquiring elements, models and application keys from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models that can have subscribe addresses added')
            return;
        print('Which element has the the model you would like to add a subscribe address to?')
        element = get_choice(choices)
        elem_addr = int(choices[element], 0)

        choices = []
        for model in node['elements'][element]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to add subscribe addresses to')
            return;
        print('Which model would you like to add a subscribe address to?')
        model = get_choice(choices)
        model_id = int(choices[model][:6], 0)

        sub_addr = int(input('Enter unsigned 16-bit subscribe address to add to this model: '), 0)

        op = {
                'type': 'node_configure',
                'configuration': 'subscribeAddressAdd',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'subscribeAddress': sub_addr
                }

    elif choice == 11:
        # Delete Subscribe Address
        print('Acquiring elements, models and application keys from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models that can have subscribe addresses deleted')
            return;
        print('Which element has the the model you would like to delete a subscribe address from?')
        element = get_choice(choices)
        elem_addr = int(choices[element], 0)

        choices = []
        for model in node['elements'][element]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to delete subscribe addresses from')
            return;
        print('Which model would you like to delete a subscribe address from?')
        model = get_choice(choices)
        model_id = int(choices[model], 0)

        choices = []
        for sub_addr in node['elements'][element]['sigModels'][model]['subscribeAddresses']:
            choices.append(uint16(sub_addr))
        if len(choices) == 0:
            print('No subscribe address to delete from model')
            return
        print('Which subscribe address would you like to delete from this model?')
        sub_addr = int(choices[get_choice(choices)], 0)

        op = {
                'type': 'node_configure',
                'configuration': 'subscribeAddressAdd',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'subscribeAddress': sub_addr
                }

    elif choice == 12:
        # Overwrite Subscribe Addresses
        print('Acquiring elements, models and application keys from node...')
        publish(build_node_disc_json(address))
        if not sem.acquire():
            return

        choices = []
        for element in node['elements']:
            choices.append(uint16(element['address']))
        if len(choices) == 0:
            print('No elements on node with models that can have subscribe addresses overwritten')
            return;
        print('Which element has the the model you would like to overwrite subscribe addresses for?')
        element = get_choice(choices)
        elem_addr = int(choices[element], 0)

        choices = []
        for model in node['elements'][element]['sigModels']:
            choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
        if len(choices) == 0:
            print('No models in element to overwrite subscribe addresses for')
            return;
        print('Which model would you like to overwrite all subscribe addresses for?')
        model = get_choice(choices)
        model_id = int(choices[model], 0)

        sub_addr = int(input('What subscribe address would you like overwrite all other subscribe address with on this model?'), 0)

        op = {
                'type': 'node_configure',
                'configuration': 'subscribeAddressAdd',
                'nodeAddress': address,
                'elementAddress': elem_addr,
                'modelId': model_id,
                'subscribeAddress': sub_addr
                }

    configure = {
            'id': 'randomId',
            'type': 'operation',
            'operation': op
            }
    print('Sending configuration request to gateway. This may take serveral minutes...\n')
    publish(configure)
    if not sem.acquire():
        return
    print_node()

def reset():
    # TODO
    return

def subscribe_menu():
    global subscription_list

    choices = [
            'Subscribe',
            'Unsubscribe',
            'Get subscription list'
            ]
    print('SUBSCRIPTION CONFIGURATION MENU');
    choice = get_choice(choices);

    if choice == 0:
        # Subscribe
        addr = int(input('Enter unsigned 16-bit mesh address to subscribe to: '), 0)
        subscribe = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subscribe',
                    'address_list': [
                        {
                            'address': addr
                            }
                        ]
                    }
                }
        print('Subscribing...')
        publish(subscribe)
        if not sem.acquire():
            return
        print_subscription_list()

    elif choice == 1:
        # Unsubscribe
        subscribe_list_req = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subscribe_list_request'
                    }
                }
        print('Acquiring subscription list...')
        publish(subscribe_list_req)
        if not sem.acquire():
            return

        choices = []
        for sub in subscription_list:
            choices.append(uint16(sub['address']))

        print('Which address would you to like to unsubscribe from?')
        addr = int(choices[get_choice(choices)], 0)
        unsubscribe = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'unsubscribe',
                    'address_list': [
                        {
                            'address': addr
                            }
                        ]
                    }
                }
        print('Unsubscribing...')
        publish(unsubscribe)
        if not sem.acquire():
            return
        print_subscription_list()

    elif choice == 2:
        # Get subscriptin list
        subscribe_list_req = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subscribe_list_request'
                    }
                }
        print('Acquiring subscription list...')
        publish(subscribe_list_req)
        if not sem.acquire():
            return
        print_subscription_list()

def get_tid():
    while True:
        try:
            tid = int(input('Enter the transaction identifier: '), 0)
        except ValueError:
            print('Invalid transaction identifier. Must be a number between 0 and 254')
            continue
        if tid < 0 or tid > 254:
            print('Invalid transaction identifier. Must be a number between 0 and 254')
            continue
        return tid

def get_transition_time():
    while True:
        tt = input('Enter the transition time (leave blank to skip): ')
        if not tt:
            return None
        try:
            tt = int(tt, 0)
        except ValueError:
            print('Invalid transition time. Must be a number between 0 and 254')
            continue
        if tt < 0 or tt > 254:
            print('Invalid transition time. Must be a number between 0 and 254')
            continue
        return tt

def get_delay():
    while True:
        delay = input('Enter the delay (leave blank to skip): ')
        if not delay:
            return None
        try:
            delay = int(delay, 0)
        except ValueError:
            print('Invalid delay. Must be a number between 0 and 254')
            continue
        if delay < 0 or delay > 254:
            print('Invalid delay. Must be a number between 0 and 254')
            continue
        return delay

def get_payload(msg):
    global tid

    payload = []
    if msg == 'Generic OnOff Get':
        return payload
    elif msg == 'Generic OnOff Set' or msg == 'Generic OnOff Set Unacknowledged':
        choices = ['ON', 'OFF']
        print('Do you want to turn the model ON or OFF?')
        on_off = choices[get_choice(choices)]
        if on_off == 'ON':
            payload.append({'byte': 0x01})
        elif on_off == 'OFF':
            payload.append({'byte': 0x00})
        payload.append({'byte': tid})
        tid = tid + 1
        tt = get_transition_time()
        if tt:
            payload.append({'byte': tt})
        delay = get_delay()
        if delay:
            payload.append({'byte': delay})
        return payload
    else:
        print('NOT YET SUPPORTED')
        return
        #'Generic Level Get': 0x8205
        #'Generic Level Set': 0x8206
        #'Generic Level Set Unacknowledged': 0x8207
        #'Generic Level Status': 0x8208
        #'Generic Delta Set': 0x8209
        #'Generic Delta Set Unacknowledged': 0x820A
        #'Generic Move Set': 0x820B
        #'Generic Mode Set Unacknowledged': 0x820C
        #'Generic Default Transition Time Get': 0x820D
        #'Generic Default Transition Time Set': 0x820E
        #'Generic Default Transition Time Set Unacknowledged': 0x820F
        #'Generic Default Transition Time Status': 0x8210
        #'Generic OnPowerUp Get': 0x8211
        #'Generic OnPowerUp Status': 0x8212
        #'Generic OnPowerUp Set': 0x8213
        #'Generic OnPowerUp Set Unacknowledged': 0x8214
        #'Generic Power Level Get': 0x8215
        #'Generic Power Level Set': 0x8216
        #'Generic Power Level Set Unacknowledged': 0x8217
        #'Generic Power Level Status': 0x8218
        #'Generic Power Last Get': 0x8219
        #'Generic Power Last Status': 0x821A
        #'Generic Power Default Get': 0x821B
        #'Generic Power Default Status': 0x821C
        #'Generic Power Range Get': 0x821D
        #'Generic Power Range Status': 0x821E
        #'Generic Power Default Set': 0x821F
        #'Generic Power Default Set Unacknowledged': 0x8220
        #'Generic Power Range Set': 0x8221
        #'Generic Power Range Set Unacknowledged': 0x8222
        #'Generic Battery Get': 0x8223
        #'Generic Battery Status': 0x8224
        #'Generic Location Global Get': 0x8225
        #'Generic Location Global Status': 0x40
        #'Generic Location Local Get': 0x8226
        #'Generic Location Local Status': 0x8227
        #'Generic Location Global Set': 0x41
        #'Generic Location Global Set Unacknowledged': 0x42
        #'Generic Location Local Set': 0x8228
        #'Generic Location Local Status': 0x8229
        #'Generic Manufacturer Properties Get': 0x822A
        #'Generic Manufacturer Properties Status': 0x43
        #'Generic Manufacturer Property Get': 0x822B
        #'Generic Manufacturer Property Set': 0x44
        #'Generic Manufacturer Property Set Unacknowledged': 0x45
        #'Generic Manufacturer Property Status': 0x46
        #'Generic Admin Properties Get': 0x822C
        #'Generic Admin Properties Status': 0x47
        #'Generic Admin Property Get': 0x822D
        #'Generic Admin Property Set': 0x48
        #'Generic Admin Property Set Unacknowledged': 0x49
        #'Generic Admin Property Status': 0x4A
        #'Generic User Properties Get': 0x822E
        #'Generic User Properties Status': 0x4B
        #'Generic User Property Get': 0x822F
        #'Generic User Property Set': 0x4C
        #'Generic User Property Set Unacknowledged': 0x4D
        #'Generic User Property Status': 0x4E
        #'Generic Client Properties Get': 0x4F
        #'Generic Client Properties Status':0x50

def send_msg():
    global sem

    choices = ['SIG Model', 'Vendor Model']

    print('What model type do you want to send a message to?')
    choice = get_choice(choices)

    if choice == 0:
        # SIG Model
        choices = [
               'Generic OnOff',
               'Generic Level',
               'Generic Default Transition',
               'Generic Power OnOff',
               'Generic Power OnOff Setup',
               'Generic Power Level',
               'Generic Power Level Setup',
               'Generic Battery',
               'Generic Location',
               'Generic Location Setup',
               'Generic Manufacturer Property',
               'Generic Admin Property',
               'Generic User Property',
               'Generic Client Property'
               ]
        
        print('Which SIG model to you want to send a message for?')
        model = list(SERVER_MODEL_MSGS.keys())[get_choice(SERVER_MODEL_MSGS.keys())]
        
        print('Which ' + model + ' message would you like to send?')
        msg = SERVER_MODEL_MSGS[model][get_choice(SERVER_MODEL_MSGS[model])]

        opcode = MODEL_MSG_OPCODES[msg]

        payload = get_payload(msg)

    elif choice == 1:
        # Vendor Model
        while True:
            opcode_str = input('Enter opcode as a string of hexadecimal characters: ')
            try:
                opcode = int(opcode_str, 16)
            except ValueError:
                print('Invalid opcode. Must be a hexadecimal number between 0x000000 and 0xFFFFFF')
                continue
            if opcode < 0 or opcode > 0xFFFFFF:
                print('Invalid opcode. Must be a hexadecimal number between 0x000000 and 0xFFFFFF')
                continue
            break

        while True:
            payload_str = input('Enter message payload as a string of hexadecimal characters: ')
            payload = []
            while len(payload_str) > 0:
                try:
                    byte = int(payload_str[:2], 16)
                except ValueError:
                    print('Invalid byte in payload: ' + payload_str[:2] + '. Must be a hexadecimal number')
                    continue
                payload.append({'byte': byte})
                payload_str = payload_str[2:]
            break

    subnet = s
    if not net_idx:
        returnubnets.get_choice(sem, publish)
    if not subnet:
        return

    print('\nAcquiring application keys...')
    publish(APP_KEY_REQ)
    if not sem.acquire():
        return

    choices = []
    for app_key in app_key_list:
        if app_key['netIndex'] == subnet:
            choices.append(uint16(app_key['appIndex']))

    if len(choices) == 0:
        print('No application keys to choose from. Add some to the gateway and then to models first\n')
        return

    print('Which application key would you like to use for the mesage?')
    app_idx = int(choices[get_choice(choices)], 0)

    while True:
        address = input('\nEnter destination address of the message: ')
        try:
            address = int(address, 0)
        except ValueError:
            print('Invalid destination address/ Must be a number between 0x0000 and 0xFFFF')
            continue
        if address < 0 or address > 0xFFFF:
            print('Invalid destination address/ Must be a number between 0x0000 and 0xFFFF')
            continue
        break

    send_model_message = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'send_model_message',
                'netIndex': subnet,
                'appIndex': app_idx,
                'address': address,
                'opcode': opcode,
                'payload': payload
                }
            }
    publish(send_model_message)

def prov_result_evt(event):
    global prov_result

    del event['type']
    del event['timestamp']
    prov_result = event.copy()

    sem.release()

def reset_result_evt(event):
    print('TODO: Must write logic for reset result events')
    return

def app_key_list_evt(event):
    global app_key_list

    app_key_list = event['appKeyList'].copy()
    sem.release()

def node_list_evt(event):
    global node_list

    node_list = event['nodes'].copy()
    sem.release()

def node_disc_evt(event):
    global node

    if event['error'] != 0:
        print('Error performing node discovery: ' + str(event['error']))
        sem.release()
        return

    if event['status'] != 0:
        print('Status performing node discovery: ' + str(event['status']))
        sem.release()
        return

    del event['type']
    del event['timestamp']
    del event['error']
    del event['status']
   
    node = event.copy()
    sem.release()

def subscribe_list_evt(event):
    global subscription_list

    subscription_list = event['address_list'].copy()
    sem.release()

def print_msg_details(event):
        print('    Network Index: ' + uint16(event['netIndex']))
        print('    Application Index: ' + uint16(event['appIndex']))
        print('    Source Address: ' + uint16(event['sourceAddress']))
        print('    Destination Address: ' + uint16(event['destinationAddress']))

def recieve_model_message_evt(event):
    global getting_input

    if getting_input:
        print('\n')

    if event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Get']:
        print('Generic OnOff Get:')
        print_msg_details(event)
        payload = event['payload']

    elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Set'] or event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Set Unacknowledged']:
        print('Generic OnOff Set:')
        print_msg_details(event)
        payload = event['payload']
        if payload[0]['byte']:
            print('    OnOff: ON')
        else:
            print('    OnOff: OFF')
        print('    TID: ' + uint8(payload[1]))
        if len(payload) > 2:
            print('    Transition Time: ' + uint8(payload[2]))
        if len(payload) > 3:
            print('    Delay: ' + uint8(payload[3]))

    elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Status']:
        print('Generic OnOff Status:')
        print_msg_details(event)
        payload = event['payload']
        if payload[0]['byte']:
            print('    Present OnOff: ON')
        else:
            print('    Present OnOff: OFF')
        if len(payload) > 1:
            if payload[1]:
                print('    Target OnOff: ON')
            else:
                print('    Target OnOff: OFF')
        if len(payload) > 2:
            print('    Remaining Time: ' + uint8_t(payload[2]))

    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Level Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Level Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Level Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Delta Set']: 0x8209,
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Delta Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Move Set']: 0x820B,
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Mode Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Default Transition Time Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Default Transition Time Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Default Transition Time Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnPowerUp Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnPowerUp Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnPowerUp Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Level Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Level Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Level Set Unacknowledged']: 0x8217,
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Last Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Default Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Range Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Default Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Default Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Range Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Power Range Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Battery Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Location Global Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Location Local Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Location Global Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Location Global Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Location Local Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Manufacturer Properties Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Manufacturer Property Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Manufacturer Property Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Manufacturer Property Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Admin Properties Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Admin Property Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Admin Property Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Admin Property Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic User Properties Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic User Property Get']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic User Property Set']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic User Property Set Unacknowledged']:
    #elif event['opcode'] == MODEL_MSG_OPCODES['Generic Client Properties Get']:
    else:
        print('Recieved unsupported mesh model message:')
        print_msg_details(event)
        print('    Opcode: ' + hex(event['opcode']))

    if getting_input:
        print('\nMAIN MENU')
        print('Select from the following options:')
        print('0. View unprovisioned device beacons')
        print('1. Provision device')
        print('2. Configure network subnets')
        print('3. Configure network application keys')
        print('4. View network nodes')
        print('5. Discover a network node')
        print('6. Configure a network node')
        print('7. Reset a network node')
        print('8. Configure mesh model subscriptions')
        print('9. Send mesh model message')
        print('\n>')

def on_connect(client, _userdata, _flags, r_c):
    '''On MQTT broker connect callback'''
    global g2c_topic

    print('Connected with result code: ' + str(r_c))

    print('Subscribing to ' + g2c_topic)
    client.subscribe(g2c_topic)

def on_message(_client, _userdata, msg):
    ''' On MQTT message recieve callback'''
    global verbose

    msg_json = json.loads(msg.payload)

    if msg_json['type'] != 'event':
        return

    if verbose:
        print('Incoming MQTT message:')
        print('    Gateway ID: ' + msg_json['gatewayId'])
        print('    Timestamp : ' + msg_json['event']['timestamp'] + '\n')

    event = msg_json['event']

    if event['type'] == 'beacon_list':
        if verbose:
            print('Recieved beacon list event')
        beacons.evt(event, sem)

    elif event['type'] == 'provision_result':
        if verbose:
            print('Recieved provision result event')
        prov_result_evt(event)

    elif event['type'] == 'reset_result':
        if verbose:
            print('Recieved reset result event')
        reset_result_evt(event)

    elif event['type'] == 'subnet_list':
        if verbose:
            print('Recieved subnet list event')
        subnets.evt(event, sem)

    elif event['type'] == 'app_key_list':
        if verbose:
            print('Recieved app key list event')
        app_key_list_evt(event)

    elif event['type'] == 'node_list':
        if verbose:
            print('Recieved node list event')
        node_list_evt(event)

    elif event['type'] == 'node_discover_result':
        if verbose:
            print('Recieved node discover result event')
        node_disc_evt(event)
    
    elif event['type'] == 'subscribe_list':
        if verbose:
            print('Recieved subscribe list event')
        subscribe_list_evt(event)

    elif event['type'] == 'recieve_model_message':
        if verbose:
            print('Recieved recieve model message event')
        recieve_model_message_evt(event)

    else:
        print("ERROR: Unrecognized event: " + event['type'])

def on_subscribe(client, _userdata, _midi, granted_qos):
    ''' On MQTT topic subscribe callback'''
    global g2c_topic
    global c2g_topic

    print('Subscribed to ' + g2c_topic)
    print('QOS: ' + str(granted_qos) + '\n')

    sem.release()

def http_req(req_url, req_api_key):
    ''' Make an HTTP request '''
    try:
        resp = requests.get(req_url, headers={'Authorization': 'Bearer ' + req_api_key})
    except requests.RequestException:
        print('Request Exception')
    except requests.ConnectionError:
        print('Connection Error')
    except requests.HTTPError:
        print('HTTP Error')
    except requests.TooManyRedirects:
        print('Too many redirects')
    except requests.ConnectTimeout:
        print('Connect Timeout')
    except requests.ReadTimeout:
        print('Read Timeout')
    except requests.Timeout:
        print('Timeout')

    if resp.status_code != 200:
        print('GET Error: ' + str(resp.status_code))

    return resp.json()

def get_choice(options):
    ''' Get a choice from the user from a list of menu options '''
    global live
    global getting_input

    getting_input = True
    while True:
        for idx, option in enumerate(options):
            print(str(idx+1) + '. ' + option)

        choice = input('\n>')

        if choice.lower() == 'exit' or choice.lower() == 'quit':
            live = False
            return

        if choice.lower() == 'back' or choice.lower() == 'return':
            return len(options)

        try:
            choice = int(choice)
        except ValueError:
            print('Invalid choice. You must enter a number between 1 and ' + str(len(options)))
            continue

        if choice < 1 or choice > len(options):
            print('Invalid choice. You must enter a number between 1 and ' + str(len(options)))
            continue

        getting_input = False
        return choice-1

def main_menu():
    ''' Main menu for CLI. Runs as a thread '''
    global sem;
    global live;

    sem.acquire()
    while live:
        menu_options = [
                'View unprovisioned device beacons',
                'Provision device',
                'Configure network subnets',
                'Configure network application keys',
                'View network nodes',
                'Discover a network node',
                'Configure a network node',
                'Reset a network node',
                'Configure mesh model subscriptions',
                'Send mesh model message'
                ]

        print("MAIN MENU")
        print("Select from the following options:")

        choice = get_choice(menu_options)

        if not choice:
            break

        if menu_options[choice] == 'View unprovisioned device beacons':
            beacons.request_beacons(sem, publish)
        elif menu_options[choice] == 'Provision device':
            provision()
        elif menu_options[choice] == 'Configure network subnets':
            subnets.menu(sem, publish)
        elif menu_options[choice] == 'Configure network application keys':
            app_key_menu()
        elif menu_options[choice] == 'View network nodes':
            node_request()
        elif menu_options[choice] == 'Discover a network node':
            node_discover()
        elif menu_options[choice] == 'Configure a network node':
            node_configure()
        elif menu_options[choice] == 'Reset a network node':
            reset()
        elif menu_options[choice] == 'Configure mesh model subscriptions':
            subscribe_menu()
        elif menu_options[choice] == 'Send mesh model message':
            send_msg()

sem = sync_sem.Sem()
beacons = mesh_beacons.Beacons()
subnets = mesh_subnets.Subnets(get_choice)

print('nRF Cloud Bluetooth Mesh Gateway Interface')
api_key = input("Enter your nRF Cloud API key: ")

print('\nQuerying nRF Cloud for account details...')
resp = http_req(ACC_URL, api_key)
mqtt_endpoint = resp['mqttEndpoint']
mqtt_topic_prefix = resp['mqttTopicPrefix']

client_id = mqtt_topic_prefix[mqtt_topic_prefix.index('/')+1:]
client_id = client_id[:client_id.index('/')]
client_id = 'account-' + client_id

print('    MQTT Endpoint    : ' + mqtt_endpoint)
print('    MQTT Topix Prefix: ' + mqtt_topic_prefix)
print('    MQTT Client ID   : ' + client_id)

print('\nQuerying nRF Cloud for account devices...')
resp = http_req(DEV_URL, api_key)
device_list = []
for device in resp['items']:
    device_list.append(device['id'])
    print('    Device ID  : ' + device['id'])
    print('    Device Name: ' + device['name'])
    print('    Type       : ' + device['type'])
    print('    Created On : ' + device['$meta']['createdAt'])
    print('    Version    : ' + device['$meta']['version'] + '\n')

print ('\nSelect which gateway device to interface with:')
device = get_choice(device_list)

c2g_topic = mqtt_topic_prefix + 'm/gateways/' + device_list[int(device)] + '/c2g'
g2c_topic = mqtt_topic_prefix + 'm/gateways/' + device_list[int(device)] + '/g2c'

print('    Cloud-to-Gateway MQTT Topic: ' + c2g_topic)
print('    Gateway-to-Cloud MQTT Topic: ' + g2c_topic)

print('\nConnecting to MQTT broker...\n')
client = mqtt.Client(client_id)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.tls_set(ca_certs = './credentials/caCert.crt', certfile = './credentials/clientCert.crt',\
        keyfile = './credentials/privateKey.key', cert_reqs=mqtt.ssl.CERT_REQUIRED,\
        tls_version=mqtt.ssl.PROTOCOL_TLS, ciphers=None)
client.connect(mqtt_endpoint, PORT, KEEP_ALIVE)

if not sem.acquire():
    print('nRF Cloud connection timed out. Try again later.')
    sys.exit()

main_menu_thread = threading.Thread(target=main_menu)
main_menu_thread.start()

while live:
    client.loop()

main_menu_thread.join()
print("Exiting...")
