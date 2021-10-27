''' Bluetooth mesh nodes module '''
from byte_codec import uint16

class Nodes():
    ''' Bluetooth mesh nodes class '''
    __NODE_REQ = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'node_request'
                }
            }
    __nodes = [dict]

    def __init__(self, sem, get_choice, publish):
        self.__sem = sem
        self.__get_choice = get_choice
        self.__publish = publish

    def __print(self):
        print('Network Nodes:')
        for node in self.__nodes:
            if node['address'] == 1:
                print('    Address      : ' + uint16(node['address']) + ' (Gateway)')
            else:
                print('    Address      : ' + uint16(node['address']))
            print('    Device Type  : ' + node['deviceType'])
            print('    UUID         : ' + node['uuid'])
            print('    Network Index: ' + uint16(node['netIndex']))
            print('    Element Count: ' + str(node['elementCount']) + '\n')
        if len(self.__nodes) == 0:
            print('    No Nodes\n')

    def get_choice(self):
        ''' Get a node selection from the user '''
        print('Acquiring network nodes from gateway...')
        self.__publish(self.__NODE_REQ)
        if not self.__sem.acquire():
            return None
        choices = []
        for node in self.__nodes:
            if node['address'] != 1:
                choices.append(uint16(node['address']))
        if len(choices) == 0:
            print('No nodes to choose from\n')
            return None
        print('Select a node:')
        choice = self.__get_choice(choices)
        if choice is None or choice == -1:
            return choice
        return int(choices[choice], 0)

    def get(self):
        ''' Get a list of nodes from the gateway '''
        print('Getting network nodes from gateway...')
        self.__publish(self.__NODE_REQ)
        if not self.__sem.acquire():
            return
        self.__print()

    def evt(self, event):
        ''' Receive list of nodes from gateway '''
        self.__nodes = event['nodes'].copy()
        self.__sem.release()
