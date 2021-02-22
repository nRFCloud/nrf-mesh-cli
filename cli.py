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

network = {}
discovery = True
disc_list = []
live = True
resp_sem = threading.Semaphore(0)

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
    global client
    global c2g_topic
    global resp_sem

    print("Publishing beacon request...\n")
    client.publish(c2g_topic, payload=json.dumps(BEACON_REQ), qos=0, retain=False)
    resp_sem.acquire()

def provision():
    uuid = input('Enter 128-bit UUID of device to provision: ')
    net_idx = int(input('Enter 16-bit network index: '))
    addr = int(input('Enter 16-bit address: '))
    attn_time = int(input('Enter the attention timer for the provisioning process: '))

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

    client.publish(c2g_topic, payload=json.dumps(prov), qos=0, retain=False)
    resp_sem.acquire()

def subnet_menu():
    return

def app_key_menu():
    return

def node_request():
    return;

def node_discover():
    return

def node_configure():
    return

def reset():
    return

def main_menu():
    global live

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

def print_beacon_list(event):
    global resp_sem

    for beacon in event['beacons']:
        print('    Device Type: ' + beacon['deviceType'])
        print('    UUID       : ' + beacon['uuid'])
        print('    OOB Info   : ' + beacon['oobInfo'])
        print('    URI Hash   : ' + str(beacon['uriHash']) + '\n')

    if len(event['beacons']) == 0:
        print('    No Beacons\n')

    resp_sem.release()

def print_subnets(network):
    for subnet in network['subnets']:
        print('  - ' + '0x{:02x}'.format(subnet['netIndex']))
    if len(network['subnets']) == 0:
        print('    No Subnets')
    print()

def print_app_keys(network):
    for app_key in network['app_keys']:
        print('  - ' + '0x{:02x}'.format(app_key['appIndex']) + ' : ' +
                '0x{:02x}'.format(app_key['netIndex']))
    if len(network['app_keys']) == 0:
        print('    No Application Keys')
    print()

def print_nodes(network):
    for node in network['nodes']:
        if node == 1:
            print('  - ' + '0x{:02x}'.format(node) + ' (Gateway)')
        else:
            print('  - ' + '0x{:02x}'.format(node))
    if len(network['nodes']) == 0:
        print('    No Nodes in Network')
    print()

def print_node(address):
    print('Still need to write print_node function')

def prov_result(event):
    print('TODO Still need to write provision_result')

def subnet_list(event):
    global network
    global discovery

    network['subnets'] = event['subnetList'].copy()

    if discovery:
        print_subnets(network)
        client.publish(c2g_topic, payload=json.dumps(APP_KEY_REQ), qos=0, retain=False)
    else:
        resp_sem.release()

def app_key_list(event):
    global network
    global discovery

    network['app_keys'] = event['appKeyList'].copy()
    if discovery:
        print_app_keys(network)
        client.publish(c2g_topic, payload=json.dumps(NODE_REQ), qos=0, retain=False)
    else:
        resp_sem.release()

def node_list(event):
    global network
    global discovery
    global disc_idx
    global disc_list

    try:
        del network['nodes']
    except KeyError:
        pass

    network['nodes'] = {}

    for node in event['nodes']:
        network['nodes'][node['address']] = {}

        if discovery and node['address'] != 1:
            disc_list.append(node['address'])

    if discovery:
        if len(disc_list) == 0:
            print('    No nodes in network other than gateway\n')
            discovery = False
            menu_thread = threading.Thread(target=main_menu)
            menu_thread.start()
        else:
            print_nodes(network)
            disc_idx = 0
            client.publish(c2g_topic, payload=json.dumps(build_node_disc_json(disc_list[disc_idx])),
                    qos=0, retain=False)
    else:
        resp_sem.release()

def node_disc(event):
    global network
    global discovery
    global disc_idx
    global disc_list

    if event['error'] != 0:
        print('Error performing node discovery: ' + str(event['error']))
        return

    if event['status'] != 0:
        print('Status performing node discovery: ' + str(event['status']))
        return

    address = event['address']
    del event['type']
    del event['timestamp']
    del event['error']
    del event['status']
    del event['address']
    network['nodes'][address] = event.copy()

    if discovery:
        print_node(address)
        disc_idx = disc_idx + 1
        if disc_idx == len(disc_list):
            discovery = False
            menu_thread = threading.Thread(target=main_menu)
            menu_thread.start()
        else:
            client.publish(c2g_topic, payload=json.dumps(buid_node_disc_json(disc_list[disc_idx])),
                qos=0, retain=False)
    else:
        resp_sem.release()


def on_connect(client, _userdata, _flags, r_c):
    '''On MQTT broker connect callback'''
    global g2c_topic

    print('Connected with result code: ' + str(r_c))

    print('Subscribing to ' + g2c_topic)
    client.subscribe(g2c_topic)

def on_message(_client, _userdata, msg):
    ''' On MQTT message recieve callback'''
    msg_json = json.loads(msg.payload)

    if msg_json['type'] != 'event':
        return

    print('Incoming MQTT message:')
    print('    Gateway ID: ' + msg_json['gatewayId'])
    print('    Timestamp : ' + msg_json['event']['timestamp'] + '\n')

    event = msg_json['event']

    if event['type'] == 'beacon_list':
        print('Recieved beacon list event')
        print_beacon_list(event)

    elif event['type'] == 'provision_result':
        print('Recieved provision result event')
        prov_result(event)

    elif event['type'] == 'reset_result':
        print('Recieved reset result event')

    elif event['type'] == 'subnet_list':
        print('Recieved subnet list event')
        subnet_list(event)

    elif event['type'] == 'app_key_list':
        print('Recieved app key list event')
        app_key_list(event)

    elif event['type'] == 'node_list':
        print('Recieved node list event')
        node_list(event)

    elif event['type'] == 'node_discover_result':
        print('Recieved node discover result event')
        node_disc(event)

    else:
        print("ERROR: Unrecognized event: " + event['type'])

def on_subscribe(client, _userdata, _midi, granted_qos):
    ''' On MQTT topic subscribe callback'''
    global resp_sem
    global menu_thread
    global g2c_topic
    global c2g_topic

    print('Subscribed to ' + g2c_topic)
    print('QOS: ' + str(granted_qos) + '\n')

    # TODO Perform network discovery here!
    print('Performing network discovery...')
    client.publish(c2g_topic, payload=json.dumps(SUBNET_REQ), qos=0, retain=False)

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

while live:
    client.loop()

menu_thread.join()
print("Exiting...")
