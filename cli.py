import sys
import json
import time
import requests
import threading
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

ACC_URL = 'https://api.nrfcloud.com/v1/account'
DEV_URL = 'https://api.nrfcloud.com/v1/devices'
AUTH_BEARER_PREFIX = 'Bearer '
HEADER = 'Authorization:"Bearer c7ce5856b2aad5d16e12b48c41a80aed3303da9b'
PORT                = 8883
KEEP_ALIVE          = 30

BEACON_REQ = {
        'id': 'randomId',
        'type': 'operation',
        'operation': {
            'type': 'beacon_request'
            }
        }

SUBNET_REQ = {
        'id': 'randomId',
        'type': 'operation',
        'operation': {
            'type' : 'subnet_request'
            }
        }

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

verbose = False
beacon_list = []
subnet_list = []
app_key_list = []
node_list = []
node = {}
prov_result = {}
live = True
resp_sem = threading.Semaphore(0)

def publish(msg):
    client.publish(c2g_topic, payload=json.dumps(msg), qos=0, retain=False)

def uint8(number):
    return '0x{:02x}'.format(number)

def uint16(number):
    return '0x{:04x}'.format(number)

def print_beacon_list():
    global beacon_list

    for beacon in beacon_list:
        print('    Device Type: ' + beacon['deviceType'])
        print('    UUID       : ' + beacon['uuid'])
        print('    OOB Info   : ' + beacon['oobInfo'])
        print('    URI Hash   : ' + str(beacon['uriHash']) + '\n')

    if len(beacon_list) == 0:
        print('    No Beacons\n')

def print_subnets():
    global subnet_list

    print('Subnets:')
    for subnet in subnet_list:
        print('  - ' + uint16(subnet['netIndex']))
    
    if len(subnet_list) == 0:
        print('    No Subnets')
    
    print()

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
            print('        SIG Model ' + uint16(model['modelId']))
            print('            Application Keys:')
            for app_key in model['appKeyIndexes']:
                print('            - ' + uint16(app_key))
            print('        Subscribed Addresses:')
            for addr in model['subscribeAddresses']:
                print('            - ' + uint16(addr))
            print('        Publish Parameters:')
            pub = model['publishParameters']
            print('            Address               : ' + uint16(pub['address']))
            print('            Application Key Index : ' + uint16(pub['appKeyIndex']))
            if pub['friendCredentialFlag']:
                print('            Friend Credential Flag: Enabled')
            else:
                print('            Friend Credential Flag: Disabled')
            print('            Time-to-live          : ' + uint8(pub['timeToLive']))
            print('            Period                : ' + uint8(pub['period']))
            print('            Period Units          : ' + pub['periodUnits'])
            print('            Retransmit Count      : ' + uint8(pub['retransmitCount']))
            print('            Retransmit Interval   : ' + uint8(pub['retransmitInterval']))

        for model in element['vendorModels']:
            print('        Vendor Model ' + uint16(model['modelId']))
            print('            Vendor ID: ' + uint16(model['companyId']))
            print('            Application Keys:')
            for app_key in model['appKeyIndex']:
                print('            - ' + uint16(app_key))
            print('        Subscribed Addresses:')
            for addr in model['subscribeAddresses']:
                print('            - ' + uint16(addr))
            print('        Publish Parameters:')
            pub = model['publishParameters']
            print('            Address               : ' + uint16(pub['address']))
            print('            Application Key Index : ' + uint16(pub['appKeyIndex']))
            if pub['friendCredentialFlag']:
                print('            Friend Credential Flag: Enabled')
            else:
                print('            Friend Credential Flag: Disabled')
            print('            Time-to-live          : ' + uint8(pub['timeToLive']))
            print('            Period                : ' + uint8(pub['period']))
            print('            Period Units          : ' + pub['periodUnits'])
            print('            Retransmit Count      : ' + uint8(pub['retransmitCount']))
            print('            Retransmit Interval   : ' + uint8(pub['retransmitInterval']) + '\n')

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

def get_choice(options):
    global live

    while True:
        for idx, option in enumerate(options):
            print(str(idx) + '. ' + option)

        choice = input('\n>')

        if choice.lower() == 'exit' or choice.lower() == 'quit':
            live = False
            return

        if choice.lower() == 'back' or choice.lower() == 'return':
            return len(options) + 1

        try:
            choice = int(choice)
        except ValueError:
            print('Invalid choice. You must enter a number between 0 and ' + str(len(options) - 1))
            continue

        if choice < 0 or choice > (len(options) - 1):
            print('Invalid choice. You must enter a number between 0 and ' + str(len(options) - 1))
            continue

        return choice

def beacon_request():
    ''' Request a list of unprovisioned beacons from the gateway '''
    global resp_sem

    print("Acquiring unprovisioned device beacons from gateway...\n")
    publish(BEACON_REQ)
    resp_sem.acquire()
    print_beacon_list()

def provision():
    global beacon_list
    global resp_sem

    print("Getting unprovisioned device beacons from gateway...\n")
    publish(BEACON_REQ)
    resp_sem.acquire()

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
    resp_sem.acquire()
    print_prov_result()

def subnet_menu():
    global resp_sem
    global subnet_list

    choices = ['Add Subnet', 'Generate Subnet', 'Delete Subnet', 'Get Subnets']
    print('SUBNET CONFIGURATION MENU')
    choice = get_choice(choices)

    if choice == 0:
        net_key = input('Enter 128-bit network key in hexadecimal format: ')
        net_idx = int(input('Enter unsigned 16-bit network index: '), 0)
        subnet_add = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subnet_add',
                    'netKey': net_key,
                    'netIndex': net_idx
                    }
                }
        print('Adding subnet...')
        publish(subnet_add)
        resp_sem.acquire()
        print_subnets()

    elif choice == 1:
        net_idx = int(input('Enter unsigned 16-bit network index: '), 0)
        subnet_gen = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subnet_generate',
                    'netIndex': net_idx
                    }
                }
        print('Generating subnet...')
        publish(subnet_gen)
        resp_sem.acquire()
        print_subnets()
        
    elif choice == 2:
        publish(SUBNET_REQ)
        resp_sem.acquire()
        
        choices = []
        for subnet in subnet_list:
            if subnet['netIndex'] != 0:
                choices.append(uint16(subnet['netIndex']))

        if len(choices) == 0:
            print('No subnets to delete')
            return

        print('Which subnet would you like to delete?')
        choice = get_choice(choices)
        
        subnet_del = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'subnet_delete',
                    'netIndex': int(choices[choice], 0)
                    }
                }
        print('Deleteing subnet...')
        publish(subnet_del)
        resp_sem.acquire()
        print_subnets()

    elif choice == 3:
        print('Getting subnets...')
        publish(SUBNET_REQ)
        resp_sem.acquire()
        print_subnets()

def app_key_menu():
    global resp_sem
    global app_key_list
    global subnet_list

    choices = ['Add Application Key', 'Generate Application Key', 'Delete Application Key',
            'Get Application Keys']
    print('APPLICATION KEY CONFIGURATION MENU')
    choice = get_choice(choices)

    if choice == 0:
        publish(SUBNET_REQ)
        resp_sem.acquire()

        choices = []
        for subnet in subnet_list:
            choices.append(uint16(subnet['netIndex']))

        print('Which subnet will the new application key part be a part of?')
        choice = get_choice(choices)
        net_idx = int(choices[choice], 0)

        app_key = input('Enter 128-bit application key in hexadecimal format: ')
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
        resp_sem.acquire()
        print_app_keys()

    elif choice == 1:
        publish(SUBNET_REQ)
        resp_sem.acquire()

        choices = []
        for subnet in subnet_list:
            choices.append(uint16(subnet['netIndex']))

        print('Which subnet will the generated application key be a part of?')
        choice = get_choice(choices)
        net_idx = int(choices[choice], 0)

        app_idx = int(input('Enter unsigned 16-bit application index for the application key: '), 0)
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
        resp_sem.acquire()
        print_app_keys()

    elif choice == 2:
        publish(APP_KEY_REQ)
        resp_sem.acquire()

        choices = []
        for app_key in app_key_list:
            choices.append(uint16(app_key['appIndex']))

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
        resp_sem.acquire()
        print_app_keys()

    elif choice == 3:
        print('Getting application keys...')
        publish(APP_KEY_REQ)
        resp_sem.acquire()
        print_app_keys()

def node_request():
    global resp_sem

    print('Getting network nodes from gateway...')
    publish(NODE_REQ)
    resp_sem.acquire()
    print_nodes()

def node_discover():
    global resp_sem
    global node_list
    global node

    print('Acquiring nodes from gateway...\n')
    publish(NODE_REQ)
    resp_sem.acquire()

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
    resp_sem.acquire()
    print_node()

def node_configure():
    return

def reset():
    return

def main_menu():
    global live

    resp_sem.acquire()
    while live:
        menu_options = [
                'View unprovisioned device beacons',
                'Provision device',
                'Configure network subnets',
                'Configure network application keys',
                'View network nodes',
                'Discover a network node',
                'Configure a network node'
                'Reset a network node',
                ]

        print("MAIN MENU")
        print("Select from the following options:")

        choice = get_choice(menu_options)

        if choice == 0:
            beacon_request()
        elif choice == 1:
            provision()
        elif choice == 2:
            subnet_menu()
        elif choice == 3:
            app_key_menu()
        elif choice == 4:
            node_request()
        elif choice == 5:
            node_discover()
        elif choice == 6:
            node_configure()
        elif choice == 7:
            reset()

def prov_result_evt(event):
    global resp_sem
    global prov_result

    del event['type']
    del event['timestamp']
    prov_result = event.copy()

    resp_sem.release()

def beacon_list_evt(event):
    global resp_sem
    global beacon_list

    beacon_list = event['beacons'].copy()
    resp_sem.release()

def subnet_list_evt(event):
    global resp_sem
    global subnet_list

    subnet_list = event['subnetList'].copy()
    resp_sem.release()

def app_key_list_evt(event):
    global resp_sem
    global app_key_list

    app_key_list = event['appKeyList'].copy()
    resp_sem.release()

def node_list_evt(event):
    global resp_sem
    global node_list

    node_list = event['nodes'].copy()
    resp_sem.release()

def node_disc_evt(event):
    global resp_sem
    global node

    if event['error'] != 0:
        print('Error performing node discovery: ' + str(event['error']))
        resp_sem.release()
        return

    if event['status'] != 0:
        print('Status performing node discovery: ' + str(event['status']))
        resp_sem.release()
        return

    del event['type']
    del event['timestamp']
    del event['error']
    del event['status']
   
    node = event.copy()
    resp_sem.release()

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
        beacon_list_evt(event)

    elif event['type'] == 'provision_result':
        if verbose:
            print('Recieved provision result event')
        prov_result_evt(event)

    elif event['type'] == 'reset_result':
        if verbose:
            print('Recieved reset result event')

    elif event['type'] == 'subnet_list':
        if verbose:
            print('Recieved subnet list event')
        subnet_list_evt(event)

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

    else:
        print("ERROR: Unrecognized event: " + event['type'])

def on_subscribe(client, _userdata, _midi, granted_qos):
    ''' On MQTT topic subscribe callback'''
    global resp_sem
    global g2c_topic
    global c2g_topic

    print('Subscribed to ' + g2c_topic)
    print('QOS: ' + str(granted_qos) + '\n')

    resp_sem.release()

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
client.tls_set(ca_certs = './caCert.crt', certfile = './clientCert.crt',\
        keyfile = './privateKey.key', cert_reqs=mqtt.ssl.CERT_REQUIRED,\
        tls_version=mqtt.ssl.PROTOCOL_TLS, ciphers=None)
client.connect(mqtt_endpoint, PORT, KEEP_ALIVE)

menu_thread = threading.Thread(target=main_menu)
menu_thread.start()

while live:
    client.loop()

menu_thread.join()
print("Exiting...")
