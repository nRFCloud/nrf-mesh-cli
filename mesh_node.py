''' Bluetooth mesh node module '''
from mesh_models import MODEL_ID_PARSE
from byte_codec import uint8
from byte_codec import uint16

class Node():
    ''' Bluetooth mesh node interface '''
    __MENU_CHOICES = [
            'Set Network Beacon',
            'Set Time-to-Live',
            'Set Relay Feature',
            'Set GATT Proxy Feature',
            'Set Friend Feature',
            'Add Subnet',
            'Delete Subnet',
            'Bind Application Key',
            'Unbind Application Key',
            'Set Publish Parameters',
            'Add Subscribe Address',
            'Delete Subscribe Address',
            'Overwrite Subscribe Addresses'
            ]
    __node = {}

    def __init__(self, sem, nodes, subnets, app_keys, get_choice, publish):
        self.__sem = sem
        self.__nodes = nodes
        self.__subnets = subnets
        self.__app_keys = app_keys
        self.__get_choice = get_choice
        self.__publish = publish

    def __build_disc_json(self, address):
        ''' Build the json object for performing a node discovery '''
        node_disc = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'node_discover',
                    'address': address
                    }
                }
        return node_disc

    def __print(self):
        print('Node: ' + uint16(self.__node['address']))
        print('    UUID: ' + self.__node['uuid'])
        print('    CID : ' + uint16(self.__node['cid']))
        print('    PID : ' + uint16(self.__node['pid']))
        print('    VID : ' + uint16(self.__node['vid']))
        print('    CRPL: ' + uint16(self.__node['crpl']) + '\n')

        if self.__node['networkBeaconState']:
            print('    Network Beacon ENABLED')
        else:
            print('    Network Beacon DISABLED')
        print('    Time-to-live: ' + uint8(self.__node['timeToLive']) + '\n')

        relay = self.__node['relayFeature']
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

        proxy = self.__node['proxyFeature']
        print('    GATT Proxy Feature:')
        if proxy['support']:
            print('        Supported')
            if proxy['state']:
                print('        Enabled')
            else:
                print('        Disabled')
        else:
            print('        NOT Supported')

        friend = self.__node['friendFeature']
        print('    Friend Feature:')
        if friend['support']:
            print('        Supported')
            if friend['state']:
                print('        Enabled')
            else:
                print('        Disabled')
        else:
            print('        NOT Supported')

        lpn = self.__node['lpnFeature']
        print('    Low Power Node Feature:')
        if lpn['state']:
            print('        Supported')
        else:
            print('        NOT Supported')

        print('    Subnets:')
        for subnet in self.__node['subnets']:
            print('        - ' + uint16(subnet))

        for idx, element in enumerate(self.__node['elements']):
            if element['address'] == self.__node['address']:
                print('    Element ' + uint16(idx) + ' (PRIMARY):')
            else:
                print('    Element ' + uint16(idx) + ':')
                print('        Address: ' + uint16(element['address']))
            print('        LOC    : ' + uint16(element['address']) + '\n')
            for model in element['sigModels']:
                print('        SIG Model ' + uint16(model['modelId']) + ' - ' +
                        MODEL_ID_PARSE[model['modelId']])
                print('            Application Keys:')
                if len(model['appIndexes']) == 0:
                    print('              None')
                for app_key in model['appIndexes']:
                    print('            - ' + uint16(app_key))
                print('            Subscribed Addresses:')
                if len(model['subscribeAddresses']) == 0:
                    print('              None')
                for addr in model['subscribeAddresses']:
                    print('            - ' + uint16(addr))
                print('            Publish Parameters:')
                pub = model['publishParameters']
                print('                Address               : ' + uint16(pub['address']))
                print('                Application Index     : ' + uint16(pub['appIndex']))
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
                if len(model['appIndex']) == 0:
                    print('              None')
                for app_key in model['appIndex']:
                    print('            - ' + uint16(app_key))
                print('            Subscribed Addresses:')
                if len(model['subscribeAddresses']) == 0:
                    print('              None')
                for addr in model['subscribeAddresses']:
                    print('            - ' + uint16(addr))
                print('            Publish Parameters:')
                pub = model['publishParameters']
                print('                Address               : ' + uint16(pub['address']))
                print('                Application Key Index : ' + uint16(pub['appIndex']))
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

    def __get_state_choice(self):
        choices = ['ENABLE', 'DISABLE']
        choice = self.__get_choice(choices)
        if choice == 0:
            return True
        elif choice == 1:
            return False
        else:
            return choice

    def configure(self):
        ''' Configure node '''
        address = self.__nodes.get_choice()
        if address is None or address == -1:
            return address
        print('What configuration would you like to perform?')
        choice = self.__get_choice(self.__MENU_CHOICES)
        if choice is None or choice == -1:
            return choice
        cfg_op = {}

        if choice == 0:
            # Set Network Beacon
            print('Do you want ENABLE or DISABLE the Network Beacon?')
            state = self.__get_state_choice()
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'networkBeaconSet',
                    'nodeAddress': address,
                    'state': state
                    }

        elif choice == 1:
            # Set Time-to-Live
            ttl = int(input('Enter unsigned 8-bit time-to-live: '), 0)
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'timeToLiveSet',
                    'nodeAddress': address,
                    'value': ttl
                    }

        elif choice == 2:
            # Set Relay Feature
            print('Do you want to ENABLE or DISABLE the Relay Feature?')
            state = self.__get_state_choice()
            count = int(input('Enter unsigned 8-bit retransmit count: '), 0)
            interval = int(input('Enter unsigned 16-bit retransmit interval: '), 0)
            cfg_op = {
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
            state = self.__get_state_choice()
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'proxyFeatureSet',
                    'nodeAddress': address,
                    'state': state
                    }

        elif choice == 4:
            # Set Friend Feature
            print('Do you want to ENABLE or DISABLE the Friend Feature?')
            state = self.__get_state_choice()
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'friendFeatureSet',
                    'nodeAddress': address,
                    'state': state
                    }

        elif choice == 5:
            # Add Subnet
            net_idx = self.__subnets.get_choice()
            if net_idx is None or net_idx == -1:
                return net_idx
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'subnetAdd',
                    'nodeAddress': address,
                    'netIndex': net_idx
                    }

        elif choice == 6:
            # Delete Subnet
            print('Acquiring subnets from node...')
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for subnet in self.__node['subnets']:
                choices.append(uint16(subnet))
            print('Which subnet would you like to delete from the node?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            net_idx = int(choices[choice], 0)
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'subnetDelete',
                    'nodeAddress': address,
                    'netIndex': net_idx
                    }

        elif choice == 7:
            # Bind Application Key
            app_idx = self.__app_keys.get_choice()
            if app_idx is None or app_idx == -1:
                return app_idx
            print('Acquiring elements and models from node...')
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models to bind application keys to')
                return
            print('Which element has the model you would like to bind an application key to?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            elem_addr = int(choices[choice], 0)
            choices = []
            for model in self.__node['elements'][choice]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to bind application keys to')
                return
            print('Which model would you like to bind an application key to?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            model_id = int(choices[choice][:6], 0)
            cfg_op = {
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
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models to unbind an application key from')
                return
            print('Which element has the the model you would like to unbind an application ' +
                    'key from?')
            element = self.__get_choice(choices)
            if element is None or element == -1:
                return element
            elem_addr = int(choices[element], 0)
            choices = []
            for model in self.__node['elements'][element]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to unbind an application key from')
                return
            print('Which model would you like to unbind an application key from?')
            model = self.__get_choice(choices)
            if model is None or model == -1:
                return model
            model_id = int(choices[model], 0)
            choices = []
            for app_key in self.__node['elements'][element]['sigModels'][model]['appKeyIndexes']:
                choices.append(uint16(app_key))
            if len(choices) == 0:
                print('No application keys to unbind on model')
                return
            print('Which application key would you like to unbind from this model?')
            app_key = self.__get_choice(choices)
            if app_key is None or app_key == -1:
                return app_key
            app_idx = int(choices[app_key], 0)
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'appKeyUnbind',
                    'nodeAddress': address,
                    'elementAddress': elem_addr,
                    'modelId': model_id,
                    'appIndex': app_idx
                    }

        elif choice == 9:
            # Set Publish Parameters
            app_idx = self.__app_keys.get_choice()
            if app_idx is None or app_idx == -1:
                return app_idx
            print('Acquiring elements, models and application keys from node...')
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models that can have their publish parameters set')
                return
            print('Which element has the the model you would like to set the publish ' +
                    'parameters for?')
            element = self.__get_choice(choices)
            if element is None or element == -1:
                return element
            elem_addr = int(choices[element], 0)
            choices = []
            for model in self.__node['elements'][element]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to set publish parameters for')
                return
            print('Which model would you like to set the publish parameters for?')
            model = self.__get_choice(choices)
            if model is None or model == -1:
                return model
            model_id = int(choices[model][:6], 0)
            pub_addr = int(input('Enter unsigned 16-bit address for this model to publish to: '), 0)
            print('Would you like to ENABLE or DISABLE this model\'s publish friend credential ' +
                    'flag?')
            cred_flag = self.__get_state_choice()
            ttl = int(input('Enter unsigned 8-bit value for this model\'s Publish Time-to-Live: '),
                    0)
            choices = ['100ms', '1s', '10s', '10m']
            print('Which unit would you like to use for this models Publish Period?')
            units = choices[self.__get_choice(choices)]
            if units is None or units == -1:
                return units
            period = int(input('Enter unsigned 8-bit value for this models Publish Period in the ' +
                'selected units: '), 0)
            count = int(input('Enter unsigned 8-bit value for this model\'s Retransmit Count: '), 0)
            interval = int(input('Enter unsigned 16-bit value for this model\'s Retransmit ' +
                'Interval: '), 0)
            cfg_op = {
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
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models that can have subscribe addresses added')
                return
            print('Which element has the the model you would like to add a subscribe address to?')
            element = self.__get_choice(choices)
            if element is None or element == -1:
                return element
            elem_addr = int(choices[element], 0)
            choices = []
            for model in self.__node['elements'][element]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to add subscribe addresses to')
                return
            print('Which model would you like to add a subscribe address to?')
            model = self.__get_choice(choices)
            if model is None or model == -1:
                return model
            model_id = int(choices[model][:6], 0)
            sub_addr = int(input('Enter unsigned 16-bit subscribe address to add to this model: '),
                    0)
            cfg_op = {
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
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models that can have subscribe addresses deleted')
                return
            print('Which element has the the model you would like to delete a subscribe ' +
                    'address from?')
            element = self.__get_choice(choices)
            if element is None or element == -1:
                return element
            elem_addr = int(choices[element], 0)
            choices = []
            for model in self.__node['elements'][element]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to delete subscribe addresses from')
                return
            print('Which model would you like to delete a subscribe address from?')
            model = self.__get_choice(choices)
            if model is None or model == -1:
                return model
            model_id = int(choices[model], 0)
            choices = []
            for sub_addr in self.__node['elements'][element]['sigModels'][model]['subscribeAddresses']:
                choices.append(uint16(sub_addr))
            if len(choices) == 0:
                print('No subscribe address to delete from model')
                return
            print('Which subscribe address would you like to delete from this model?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            sub_addr = int(choices[choice], 0)
            cfg_op = {
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
            self.__publish(self.__build_disc_json(address))
            if not self.__sem.acquire():
                return
            choices = []
            for element in self.__node['elements']:
                choices.append(uint16(element['address']))
            if len(choices) == 0:
                print('No elements on node with models that can have subscribe addresses ' +
                        'overwritten')
                return
            print('Which element has the the model you would like to overwrite subscribe ' +
                    'addresses for?')
            element = self.__get_choice(choices)
            if element is None or element == -1:
                return element
            elem_addr = int(choices[element], 0)
            choices = []
            for model in self.__node['elements'][element]['sigModels']:
                choices.append(uint16(model['modelId']) + ' - ' + MODEL_ID_PARSE[model['modelId']])
            if len(choices) == 0:
                print('No models in element to overwrite subscribe addresses for')
                return
            print('Which model would you like to overwrite all subscribe addresses for?')
            model = self.__get_choice(choices)
            if model is None or model == -1:
                return model
            model_id = int(choices[model][:6], 0)
            sub_addr = int(input('What subscribe address would you like overwrite all other' +
                ' subscribe address with on this model?'), 0)
            cfg_op = {
                    'type': 'node_configure',
                    'configuration': 'subscribeAddressOverwrite',
                    'nodeAddress': address,
                    'elementAddress': elem_addr,
                    'modelId': model_id,
                    'subscribeAddress': sub_addr
                    }

        configure = {
                'id': 'randomId',
                'type': 'operation',
                'operation': cfg_op
                }
        print('Sending configuration request to gateway. This may take serveral minutes...\n')
        self.__publish(configure)
        if not self.__sem.acquire():
            return
        self.__print()

    def discover(self):
        ''' Perform a node discovery '''
        address = self.__nodes.get_choice()
        if address is None or address == -1:
            return address
        print('Discovering node. This may take a few minutes...')
        self.__publish(self.__build_disc_json(address))
        if not self.__sem.acquire():
            return
        self.__print()

    def discover_evt(self, event):
        ''' Receive node discovery event from gateway '''
        if event['error'] != 0:
            print('Error performing node discovery: ' + str(event['error']))
            self.__node = {}
            self.__sem.release()
            return
        if event['status'] != 0:
            print('Status performing node discovery: ' + str(event['status']))
            self.__node = {}
            self.__sem.release()
            return
        del event['type']
        del event['timestamp']
        del event['error']
        del event['status']
        self.__node = event.copy()
        self.__sem.release()
