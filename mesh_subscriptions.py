''' Bluetooth mesh cloud subscriptions module '''
from byte_codec import uint16

class Subscriptions():
    ''' Bluetooth mesh cloud subscriptions class '''
    __MENU_CHOICES= [
            'Subscribe',
            'Unsubscribe',
            'Get subscription list'
            ]

    def __init__(self, sem, get_choice, publish):
        self.__sem = sem
        self.__get_choice = get_choice
        self.__publish = publish
        self.____subsciptions = [dict]

    def __print(self):
        print('Subscribed Addresses:')
        for sub in self.__subscriptions:
            print('  - ' + uint16(sub['address']))
        if len(self.__subscriptions) == 0:
            print('    No subscribed addresses')
        print()

    def menu(self):
        ''' Subscription configuration '''
        print('SUBSCRIPTION CONFIGURATION MENU')
        choice = self.__get_choice(self.__MENU_CHOICES)
        if choice is None or choice == -1:
            return choice
        if choice == 0:
            # Subscribe
            addr = int(input('Enter unsigned 16-bit mesh address to subscribe to: '), 0)
            subscribe = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'subscribe',
                        'addressList': [
                            {
                                'address': addr
                                }
                            ]
                        }
                    }
            print('Subscribing...')
            self.__publish(subscribe)
            if not self.__sem.acquire():
                return
            self.__print()
        elif choice == 1:
            # Unsubscribe
            subscribe_list_req = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'subscribe_list_request'
                        }
                    }
            print('Acquiring subscription list...')
            self.__publish(subscribe_list_req)
            if not self.__sem.acquire():
                return
            choices = []
            for sub in self.__subscriptions:
                choices.append(uint16(sub['address']))
            print('Which address would you to like to unsubscribe from?')
            choice = self.__get_choice(choices)
            if choice is None or choice == -1:
                return choice
            addr = int(choices[choice], 0)
            unsubscribe = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'unsubscribe',
                        'addressList': [
                            {
                                'address': addr
                                }
                            ]
                        }
                    }
            print('Unsubscribing...')
            self.__publish(unsubscribe)
            if not self.__sem.acquire():
                return
            self.__print()

        elif choice == 2:
            # Get subscriptin list
            subscribe_list_req = {
                    'id': 'randomId',
                    'type': 'operation',
                    'operation': {
                        'type': 'subscribe_list_request'
                        }
                    }
            print('Acquiring subscription list...')
            self.__publish(subscribe_list_req)
            if not self.__sem.acquire():
                return
            self.__print()

    def evt(self, event):
        ''' Recieve subscription list from gateway '''
        self.__subscriptions = event['addressList'].copy()
        self.__sem.release()
