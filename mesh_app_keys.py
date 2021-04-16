''' Bluetooth mesh appliucaiton key module '''
from byte_codec import uint16

class App_Keys():
    ''' Bluetooth mesh gateway application key interface '''
    __MENU_CHOICES = [
            'Add Application Key',
            'Generate Application Key',
            'Delete Application Key',
            'Get Application Keys'
            ]
    __APP_KEY_REQ = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'app_key_request'
                }
            }
    __app_keys = [dict]

    def __init__(self, get_choice, publish):
        self.__get_choice = get_choice
        self.__publish = publish

    def __print(self):
        ''' Print the list of current application keys '''
        print('Application Keys:')
        print('    App Index : Net Index')
        for app_key in self.__app_keys:
            print('     - ' + uint16(app_key['appIndex']) + ' : ' + uint16(app_key['netIndex']))
        if len(self.__app_keys) == 0:
            print('     No Application Keys')
        print()

    def get_choice(self, sem):
        ''' Get an application key selection from the user '''
        print('Acquiring application keys from gateway...')
        self.__publish(self.__APP_KEY_REQ)
        if not sem.acquire():
            return None
        choices = []
        for app_key in self.__app_keys:
            choices.append(uint16(app_key['appIndex']))
        if len(choices) == 0:
            print(
            'No application keys to choose from. Try adding application keys to the gateway first.'
            )
            return None
        print('Select an applicaiton key:')
        return self.__app_keys[self.__get_choice(choices)]['appIndex']

    def evt(self, event, sem):
        ''' Recieve an application key list from the gateway '''
        self.__app_keys = event['appKeyList'].copy()
        sem.release()

    def menu(self, sem, subnets):
        print('APPLICATION KEY CONFIGURATION MENU')
        choice = self.__get_choice(self.__MENU_CHOICES)

        if self.__MENU_CHOICES[choice] == 'Add Application Key':
            net_idx = subnets.get_choice(sem)
            if net_idx is None:
                return
            app_key = input('\nEnter 128-bit application key in hexadecimal format: ')
            app_idx = int(
                    input('Enter unsigned 16-bit application index for the application key: '), 0)
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
            self.__publish(app_key_add)
            if not sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Generate Application Key':
            net_idx = subnets.get_choice(sem)
            if net_idx is None:
                return
            app_idx = int(
                    input('\nEnter unsigned 16-bit application index for the application key: '), 0)
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
            self.__publish(app_key_gen)
            if not sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Delete Application Key':
            self.__publish(self.__APP_KEY_REQ)
            if not sem.acquire():
                return
            choices = []
            for app_key in self.__app_keys:
                choices.append(uint16(app_key['appIndex']))
            if len(choices) == 0:
                print('No application keys to delete')
                return
            print('Which application key would you like to delete?')
            choice = self.__get_choice(choices)
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
            self.__publish(app_key_del)
            if not sem.acquire():
                return
            self.__print()

        elif self.__MENU_CHOICES[choice] == 'Get Application Keys':
            print('Getting application keys...')
            self.__publish(self.__APP_KEY_REQ)
            if not sem.acquire():
                return
            self.__print()
