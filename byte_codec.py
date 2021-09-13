''' Byte codec module '''
def uint8(number):
    ''' Get a hexadecimal formatted string of an unsigned 8-bit integer '''
    return '0x{:02x}'.format(number)

def uint16(number):
    ''' Get a hexadecimal formatted string of an unsigned 16-bit integer '''
    return '0x{:04x}'.format(number)

def uint32(number):
    ''' Get a hexadecimal formatted string of an unsigned 32-bit integer '''
    return '0x{:08x}'.format(number)
