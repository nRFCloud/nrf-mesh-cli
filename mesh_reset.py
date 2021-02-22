''' Bluetooth mesh node reset module '''

class Reset():
    ''' Bluetooth mesh node reset interface '''
    def __init__(self, sem, nodes, publish):
        self.__sem = sem
        self.__nodes = nodes
        self.__publish = publish

    def reset(self):
        # TODO
        print('TODO: Must write logic for resetting mesh nodes')
        return

    def evt(self, event):
        # TODO
        print('TODO: Must write logic for reset result events')
        return
