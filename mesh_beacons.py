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

    def __print_beacons(self):
        ''' Print the current list of beacons '''
        for beacon in self.__beacons:
            print('    Device Type: ' + beacon['deviceType'])
            print('    UUID       : ' + beacon['uuid'])
            print('    OOB Info   : ' + beacon['oobInfo'])
            print('    URI Hash   : ' + str(beacon['uriHash']) + '\n')

        if len(self.__beacons) == 0:
            print('    No Beacons\n')

    def request_beacons(self, sem, publish):
        ''' Request a list of unprovisioned beacons from the gateway '''
        print("Acquiring unprovisioned device beacons from gateway...\n")
        publish(self.__BEACON_REQ)

        if not sem.acquire():
            return

        self.__print_beacons()

    def evt(self, event, sem):
        ''' Recieve beacon list event from gateway '''
        self.__beacons = event['beacons'].copy()
        sem.release()
