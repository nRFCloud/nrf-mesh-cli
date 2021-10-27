''' Bluetooth mesh subnet module '''
from byte_codec import uint16

class Subnets():
    ''' Bluetooth mesh gateway subnet interface '''
    __MENU_CHOICES = [
            'Add Subnet',
            'Generate Subnet',
            'Delete Subnet',
            'Get Subnets'
            ]
    __SUBNET_REQ = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type' : 'subnet_request'
                }
            }
    __subnets = [dict]

    def __init__(self, sem, get_choice, publish):
        self.__sem = sem
        self.__get_choice = get_choice
        self.__publish = publish

    def __print(self):
        ''' Print the list of current subnets '''
        print('Subnets:')
        for subnet in self.__subnets:
            print('  - ' + uint16(subnet['netIndex']))
        if len(self.__subnets) == 0:
            print('    No Subnets')
        print()

    def get_choice(self):
        ''' Get a subnet selection from the user '''
        print('Acquiring subnets from gateway...')
        self.__publish(self.__SUBNET_REQ)
        if not self.__sem.acquire():
            return None
        choices = []
        for subnet in self.__subnets:
            choices.append(uint16(subnet['netIndex']))
        if len(choices) == 0:
            print('No subnets to choose from. Try adding subnets to the gateway first.')
            return None
        print('Select a subnet:')
        choice = self.__get_choice(choices)
        if choice is None or choice == -1:
            return choice
        return self.__subnets[choice]['netIndex']

    def evt(self, event):
        ''' Receive a subnet list event from the gateway '''
        self.__subnets = event['subnetList'].copy()
        self.__sem.release()

    def menu(self):
        ''' Run subnet menu for user '''
        print('SUBNET CONFIGURATION MENU')
        choice = self.__get_choice(self.__MENU_CHOICES)
        if choice is None or choice == -1:
            return choice

        if self.__MENU_CHOICES[choice] == 'Add Subnet':
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
            self.__publish(subnet_add)
            if not self.__sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Generate Subnet':
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
            self.__publish(subnet_gen)
            if not self.__sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Delete Subnet':
            self.__publish(self.__SUBNET_REQ)
            if not self.__sem.acquire():
                return

            choices = []
            for subnet in self.__subnets:
                if subnet['netIndex'] != 0:
                    choices.append(uint16(subnet['netIndex']))

            if len(choices) == 0:
                print('No subnets to delete')
                return

            print('Which subnet would you like to delete?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice

            subnet_del = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'subnet_delete',
                        'netIndex': int(choices[choice], 0)
                        }
                    }
            print('Deleteing subnet...')
            self.__publish(subnet_del)
            if not self.__sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Get Subnets':
            print('Getting subnets...')
            self.__publish(self.__SUBNET_REQ)
            if not self.__sem.acquire():
                return
            self.__print()
