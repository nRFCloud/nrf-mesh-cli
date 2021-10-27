''' Bluetooth mesh beacon module '''
class Beacons():
    ''' Unprovisioned Bluetooth mesh device beacon gateway interface '''
    __BEACON_REQ = {
            'id': 'randomId',
            'type': 'operation',
            'operation': {
                'type': 'beacon_request'
                }
            }
    __beacons = [dict]

    def __init__(self, sem, get_choice, publish):
        self.__sem = sem
        self.__get_choice = get_choice
        self.__publish = publish

    def __print_beacons(self):
        ''' Print the current list of beacons '''
        for beacon in self.__beacons:
            print('    Device Type: ' + beacon['deviceType'])
            print('    UUID       : ' + beacon['uuid'])
            print('    OOB Info   : ' + beacon['oobInfo'])
            print('    URI Hash   : ' + str(beacon['uriHash']) + '\n')

        if len(self.__beacons) == 0:
            print('    No Beacons\n')

    def get_choice(self):
        print('Acquiring unprovisioned device beacons from gateway...')
        self.__publish(self.__BEACON_REQ)
        if not self.__sem.acquire():
            return None
        choices = []
        for beacon in self.__beacons:
            choices.append(beacon['uuid'])
        if len(choices) == 0:
            print('No unprovisioned device beacons to choose from\n')
            return None
        print('Select unprovisioned device beacon:')
        choice = self.__get_choice(choices)
        if choice is None or choice == -1:
            return choice
        return self.__beacons[choice]['uuid']

    def request_beacons(self):
        ''' Request a list of unprovisioned beacons from the gateway '''
        print("Acquiring unprovisioned device beacons from gateway...\n")
        self.__publish(self.__BEACON_REQ)
        if not self.__sem.acquire():
            return
        self.__print_beacons()

    def evt(self, event):
        ''' Receive beacon list event from gateway '''
        self.__beacons = event['beacons'].copy()
        self.__sem.release()
