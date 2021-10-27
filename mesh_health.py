''' Bluetooth mesh health client interface module '''
from byte_codec import uint8
from byte_codec import uint16
from byte_codec import uint32

class Health():
    ''' Bluetooth mesh health client interface '''
    __MENU_CHOICES = [
            'Get registered faults',
            'Clear registered faults',
            'Test faults',
            'Get fast health publish period divisor',
            'Set fast health publish period divisor',
            'Get attention timer',
            'Set attention timer',
            'Get gateway\'s health client timeout',
            'Set gateway\'s health client timeout'
            ]

    def __init__(self, sem, app_keys, nodes, get_choice, publish):
        self.__sem = sem
        self.__app_keys = app_keys
        self.__nodes = nodes
        self.__get_choice = get_choice
        self.__publish = publish
        self.__reg_faults = []
        self.__test_id = None
        self.__divisor = None
        self.__attn = None
        self.__timeout = None

    def cur_faults_evt(self, event):
        print('Received current health faults:')
        print('    Address   : ' + uint16(event['address']))
        print('    Test ID   : ' + uint8(event['testId']))
        print('    Company ID: ' + uint16(event['companyId']))
        print('    Faults:')
        if len(event['faults']):
            for fault in event['faults']:
                print('        - ' + uint8(fault['fault']))
            print()
        else:
            print('        None')

    def reg_faults_evt(self, event):
        self.__test_id = event['testId']
        self.__reg_faults = event['faults'].copy()
        self.__sem.release()

    def period_evt(self, event):
        self.__divisor = event['divisor']
        self.__sem.release()

    def attn_evt(self, event):
        self.__attn = event['attention']
        self.__sem.release()

    def timeout_evt(self, event):
        self.__timeout = event['timeout']
        self.__sem.release()

    def menu(self):
        print('HEALTH CLIENT INTERFACE MENU')
        choice = self.__get_choice(self.__MENU_CHOICES)
        if choice is None or choice == -1:
            return choice

        if self.__MENU_CHOICES[choice] == 'Get registered faults':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            cid = int(input('Enter unsigned 16-bit company ID: '), 0)
            health_fault_get = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_fault_get',
                        'address': addr,
                        'appIndex': app_key,
                        'companyId': cid
                        }
                    }
            print('Getting registered faults...')
            self.__publish(health_fault_get)
            if not self.__sem.acquire():
                return
            if not len(self.__reg_faults):
                print('    None')
            else:
                for fault in self.__reg_faults:
                    print('    - ' + uint8(fault['fault']))
            print()

        elif self.__MENU_CHOICES[choice] == 'Clear registered faults':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            cid = int(input('Enter unsigned 16-bit company ID: '), 0)
            health_fault_clear = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_fault_clear',
                        'address': addr,
                        'appIndex': app_key,
                        'companyId': cid
                        }
                    }
            print('Clearing registered faults...')
            self.__publish(health_fault_clear)
            if not self.__sem.acquire():
                return
            if not len(self.__reg_faults):
                print('    None')
            else:
                for fault in self.__reg_faults:
                    print('    - ' + uint8(fault))
            print()
            
        elif self.__MENU_CHOICES[choice] == 'Test faults':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            cid = int(input('Enter unsigned 16-bit company ID: '), 0)
            tid = int(input('Enter unsigned 8-bit test ID: '), 0)
            health_fault_test = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_fault_test',
                        'address': addr,
                        'appIndex': app_key,
                        'companyId': cid,
                        'testId': tid,
                        }
                    }
            print('Testing registered faults...')
            self.__publish(health_fault_test)
            if not self.__sem.acquire():
                return
            if not len(self.__reg_faults):
                print('    None')
            else:
                for fault in self.__reg_faults:
                    print('    - ' + uint8(fault))
            print()

        elif self.__MENU_CHOICES[choice] == 'Get fast health publish period divisor':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            health_period_get = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_period_get',
                        'address': addr,
                        'appIndex': app_key
                        }
                    }
            print('Getting fast health period divisor...')
            self.__publish(health_period_get)
            if not self.__sem.acquire():
                return
            print('\n' + uint16(addr) + ' fast health period divisor: ' + uint8(self.__divisor) + '\n')

        elif self.__MENU_CHOICES[choice] == 'Set fast health publish period divisor':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            divisor = int(input('Enter unsigned 8-bit fast period divisor: '))
            health_period_set = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_period_set',
                        'address': addr,
                        'appIndex': app_key,
                        'divisor': divisor
                        }
                    }
            print('Setting fast health period divisor...')
            self.__publish(health_period_set)
            if not self.__sem.acquire():
                return
            print('\n' + uint16(addr) + ' fast health period divisor: ' + uint8(self.__divisor) + '\n')

        elif self.__MENU_CHOICES[choice] == 'Get attention timer':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            health_attn_get = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_attention_get',
                        'address': addr,
                        'appIndex': app_key
                        }
                    }
            print('Getting attention timer...')
            self.__publish(health_attn_get)
            if not self.__sem.acquire():
                return
            print('\n' + uint16(addr) + ' attention timer: ' + uint8(self.__attn) + '\n')

        elif self.__MENU_CHOICES[choice] == 'Set attention timer':
            addr = self.__nodes.get_choice()
            app_key = self.__app_keys.get_choice()
            attn =  int(input('Enter unsigned 8-bit attention time: '))
            health_attn_set = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'health_attention_set',
                        'address': addr,
                        'appIndex': app_key,
                        'attention': attn
                        }
                    }
            print('\nSetting attention timer...\n')
            self.__publish(health_attn_set)

        elif self.__MENU_CHOICES[choice] == 'Get gateway\'s health client timeout':
            health_timeout_get = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'health_client_timeout_get'
                    }
                }
            self.__publish(health_timeout_get)
            if not self.__sem.acquire():
                return
            print('\nGateway health client timeout: ' + uint32(self.__timeout) + '\n')

        elif self.__MENU_CHOICES[choice] == 'Set gateway\'s health client timeout':
            timeout = int(input('Enter unsigned 32-bit timeout: '))
            health_timeout_set = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'health_client_timeout_set',
                    'timeout': timeout
                    }
                }
            self.__publish(health_timeout_set)
            health_timeout_get = {
                'id': 'randomId',
                'type': 'operation',
                'operation': {
                    'type': 'health_client_timeout_get'
                    }
                }
            self.__publish(health_timeout_get)
            if not self.__sem.acquire():
                return
            print('\nGateway health client timeout: ' + uint32(self.__timeout) + '\n')
