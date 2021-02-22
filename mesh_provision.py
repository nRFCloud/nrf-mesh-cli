''' Bluetooth mesh device provision module '''
from byte_codec import uint16

class Provision():
    ''' Bluetooth mesh device provision interface '''
    __prov_result = {}

    def __init__(self, sem, beacons, subnets, publish):
        self.__sem = sem
        self.__beacons = beacons
        self.__subnets = subnets
        self.__publish = publish

    def __print(self):
        if self.__prov_result['error'] != 0:
            print('Failed to provision device with UUID: ' + self.__prov_result['uuid'])
            print('    Error: ' + int(self.__prov_result['error']))
            return

        print('Provision Result:')
        print('  - UUID         : ' + self.__prov_result['uuid'])
        print('  - Net Index    : ' + uint16(self.__prov_result['netIndex']))
        print('  - Address      : ' + uint16(self.__prov_result['address']))
        print('  - Element Count: ' + uint16(self.__prov_result['elementCount']))
        print()

    def provision(self):
        uuid = self.__beacons.get_choice()
        if uuid is None or uuid == -1:
            return uuid
        net_idx = self.__subnets.get_choice()
        if net_idx is None or net_idx == -1:
            return net_idx
        while True:
            try:
                addr = int(input('Enter 16-bit address (enter 0 for lowest available address): '), 0)
            except ValueError:
                print('Invalid address')
                continue
            break
        attn = int(input('Enter the attention timer for the provisioning process: '))
        print('Provisioning ' + uuid + '. This may take several minutes.')
        prov = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'provision',
                    'uuid': uuid,
                    'netIndex': net_idx,
                    'address': addr,
                    'attention': attn
                    }
                }
        self.__publish(prov)
        if not self.__sem.acquire():
            return
        self.__print()

    def evt(self, event):
        del event['type']
        del event['timestamp']
        self.__prov_result = event.copy()
        self.__sem.release()
