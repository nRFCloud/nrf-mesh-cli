''' Bluetooth mesh model module '''
from byte_codec import uint8
from byte_codec import uint16

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

class Models():
    ''' Bluetooth mesh model class '''
    def __init__(self, sem, subnets, app_keys, get_choice, publish):
        self.__sem = sem
        self.__subnets = subnets
        self.__app_keys = app_keys
        self.__get_choice = get_choice
        self.__publish = publish
        self.__tid = 0

    def __get_transition_time(self):
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

    def __get_delay(self):
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

    def __get_payload(self, msg):
        payload = []
        if msg == 'Generic OnOff Get':
            return payload
        elif msg == 'Generic OnOff Set' or msg == 'Generic OnOff Set Unacknowledged':
            choices = ['ON', 'OFF']
            print('Do you want to turn the model ON or OFF?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            on_off = choices[choice]
            if on_off == 'ON':
                payload.append({'byte': 0x01})
            elif on_off == 'OFF':
                payload.append({'byte': 0x00})
            payload.append({'byte': self.__tid})
            self.__tid = self.__tid + 1
            tt = self.__get_transition_time()
            if tt:
                payload.append({'byte': tt})
            delay = self.__get_delay()
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

    def send_msg(self):
        ''' Send bluetooth mesh model message '''
        choices = ['SIG Model', 'Vendor Model']
        print('What model type do you want to send a message to?')
        choice = self.__get_choice(choices)
        if choice is None or choice == -1:
            return choice

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
            choice = self.__get_choice(SERVER_MODEL_MSGS.keys())
            if choice is None or choice == -1:
                return choice
            model = list(SERVER_MODEL_MSGS.keys())[choice]
            print('Which ' + model + ' message would you like to send?')
            choice = self.__get_choice(SERVER_MODEL_MSGS[model])
            if choice is None or choice == -1:
                return choice
            msg = SERVER_MODEL_MSGS[model][choice]
            opcode = MODEL_MSG_OPCODES[msg]
            payload = self.__get_payload(msg)

        elif choice == 1:
            # Vendor Model
            while True:
                opcode_str = input('Enter opcode as a string of hexadecimal characters: ')
                try:
                    opcode = int(opcode_str, 16)
                except ValueError:
                    print('Invalid opcode. Must be a hexadecimal number between 0x000000 and ' +
                    '0xFFFFFF')
                    continue
                if opcode < 0 or opcode > 0xFFFFFF:
                    print('Invalid opcode. Must be a hexadecimal number between 0x000000 and ' +
                    '0xFFFFFF')
                    continue
                break

            while True:
                payload_str = input('Enter message payload as a string of hexadecimal characters: ')
                payload = []
                while len(payload_str) > 0:
                    try:
                        byte = int(payload_str[:2], 16)
                    except ValueError:
                        print('Invalid byte in payload: ' + payload_str[:2] + '. Must be a ' +
                        'hexadecimal number')
                        continue
                    payload.append({'byte': byte})
                    payload_str = payload_str[2:]
                break

        net_idx = self.__subnets.get_choice()
        if net_idx is None or net_idx == -1:
            return net_idx
        app_idx = self.__app_keys.get_choice()
        if app_idx is None or app_idx == -1:
            return app_idx
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
                    'netIndex': net_idx,
                    'appIndex': app_idx,
                    'address': address,
                    'opcode': opcode,
                    'payload': payload
                    }
                }
        self.__publish(send_model_message)

    def __print_msg_details(self, event):
        print('    Network Index: ' + uint16(event['netIndex']))
        print('    Application Index: ' + uint16(event['appIndex']))
        print('    Source Address: ' + uint16(event['sourceAddress']))
        print('    Destination Address: ' + uint16(event['destinationAddress']))

    def evt(self, event):
        ''' Receive bluetooth mesh model message from gateway '''
        if event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Get']:
            print('Generic OnOff Get:')
            self.__print_msg_details(event)
            payload = event['payload']

        elif event['opcode']  == MODEL_MSG_OPCODES['Generic OnOff Set'] or \
        event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Set Unacknowledged']:
            print('Generic OnOff Set:')
            self.__print_msg_details(event)
            payload = event['payload']
            if payload is not None and len(payload) > 0:
                if payload[0]['byte']:
                    print('    OnOff: ON')
                else:
                    print('    OnOff: OFF')
                if len(payload) > 1:
                    print('    TID: ' + uint8(payload[1]['byte']))
                if len(payload) > 2:
                    print('    Transition Time: ' + uint8(payload[2]['byte']))
                if len(payload) > 3:
                    print('    Delay: ' + uint8(payload[3]['byte']))

        elif event['opcode'] == MODEL_MSG_OPCODES['Generic OnOff Status']:
            print('Generic OnOff Status:')
            self.__print_msg_details(event)
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
                print('    Remaining Time: ' + uint8(payload[2]['byte']))

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
            print('Received unsupported mesh model message:')
            self.__print_msg_details(event)
            print('    Opcode: ' + hex(event['opcode']))
            print('    Payload: ', end='')
            payload = event['payload']
            if len(payload):
                for byte in payload:
                    print(uint8(byte['byte']), end=' ')
                print()
            else:
                print('None')
