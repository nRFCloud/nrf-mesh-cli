''' Bluetooth Mesh LTE CLI Main Module'''
import sys
import json
import threading
import requests
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import sync_sem
import mesh_beacons
import mesh_subnets
import mesh_app_keys
import mesh_health
import mesh_provision
import mesh_reset
import mesh_nodes
import mesh_node
import mesh_subscriptions
import mesh_models

ACC_URL = 'https://api.nrfcloud.com/v1/account'
DEV_URL = 'https://api.nrfcloud.com/v1/devices'
AUTH_BEARER_PREFIX = 'Bearer '
PORT                = 8883
KEEP_ALIVE          = 30

live = True
getting_input = False

def publish_mqtt(msg):
    ''' Publish mqtt message to mesh gateway '''
    client.publish(c2g_topic, payload=json.dumps(msg), qos=0, retain=False)

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
            return None
        if choice.lower() == 'back' or choice.lower() == 'return':
            return -1
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

sem = sync_sem.Sem()
beacons = mesh_beacons.Beacons(sem, get_choice, publish_mqtt)
subnets = mesh_subnets.Subnets(sem, get_choice, publish_mqtt)
app_keys = mesh_app_keys.App_Keys(sem, subnets, get_choice, publish_mqtt)
provision = mesh_provision.Provision(sem, beacons, subnets, publish_mqtt)
nodes = mesh_nodes.Nodes(sem, get_choice, publish_mqtt)
health = mesh_health.Health(sem, app_keys, nodes, get_choice, publish_mqtt)
node = mesh_node.Node(sem, nodes, subnets, app_keys, get_choice, publish_mqtt)
reset = mesh_reset.Reset(sem, nodes, publish_mqtt)
subscriptions = mesh_subscriptions.Subscriptions(sem, get_choice, publish_mqtt)
models = mesh_models.Models(sem, subnets, app_keys, get_choice, publish_mqtt)

event_dispatch = {
        'beacon_list': beacons.evt,
        'provision_result': provision.evt,
        'reset_result': reset.evt,
        'subnet_list': subnets.evt,
        'app_key_list': app_keys.evt,
        'health_faults_current': health.cur_faults_evt,
        'health_faults_registered': health.reg_faults_evt,
        'health_period': health.period_evt,
        'health_attention': health.attn_evt,
        'health_client_timeout': health.timeout_evt,
        'node_list': nodes.evt,
        'node_discover_result': node.discover_evt,
        'subscribe_list': subscriptions.evt,
        'receive_model_message': models.evt
        }

def on_connect(_client, _userdata, _flags, r_c):
    '''On MQTT broker connect callback'''
    print('Connected with result code: ' + str(r_c))
    print('Subscribing to ' + g2c_topic)
    _client.subscribe(g2c_topic)

def on_message(_client, _userdata, msg):
    ''' On MQTT message receive callback'''
    msg_json = json.loads(msg.payload)
    if msg_json['type'] != 'event':
        return
    if getting_input:
        print('\n')
    event = msg_json['event']
    try:
        event_dispatch[event['type']](event)
    except KeyError:
        print("ERROR: Unrecognized event: " + event['type'])
    if getting_input:
        print('\nMAIN MENU')
        print('Select from the following options:')
        print('1. View unprovisioned device beacons')
        print('2. Provision device')
        print('3. Configure network subnets')
        print('4. Configure network application keys')
        print('5. Health Client Interface')
        print('6. View network nodes')
        print('7. Discover a network node')
        print('8. Configure a network node')
        print('9. Reset a network node')
        print('10. Configure mesh model subscriptions')
        print('11. Send mesh model message')
        print('\n>', end='')

def on_subscribe(_client, _userdata, _midi, granted_qos):
    ''' On MQTT topic subscribe callback'''
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
                'Health client interface',
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

        if choice is None:
            break

        if menu_options[choice] == 'View unprovisioned device beacons':
            beacons.request_beacons()
        elif menu_options[choice] == 'Provision device':
            provision.provision()
        elif menu_options[choice] == 'Configure network subnets':
            subnets.menu()
        elif menu_options[choice] == 'Configure network application keys':
            app_keys.menu()
        elif menu_options[choice] == 'Health client interface':
            health.menu()
        elif menu_options[choice] == 'View network nodes':
            nodes.get()
        elif menu_options[choice] == 'Discover a network node':
            node.discover()
        elif menu_options[choice] == 'Configure a network node':
            node.configure()
        elif menu_options[choice] == 'Reset a network node':
            reset.reset()
        elif menu_options[choice] == 'Configure mesh model subscriptions':
            subscriptions.menu()
        elif menu_options[choice] == 'Send mesh model message':
            models.send_msg()

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
if device is None or device == -1:
    sys.exit()

g2c_topic = mqtt_topic_prefix + 'm/d/' + device_list[int(device)] + '/d2c'
c2g_topic = mqtt_topic_prefix + 'm/d/' + device_list[int(device)] + '/c2d'
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
