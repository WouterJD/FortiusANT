#!/usr/bin/python3

# pip3 install pyusb

import usb.core
import usb.util
import time
import optparse

# Some words about the variants of TACX head units and brakes:
#
# There are 4 different USB based head-units for two types of brakes.
# Head-units:
#    "solid green" T1902,
#    "solid blue"  T1942,
#    "white green" T1904 and
#    "white blue"  T1932.
#
# Brakes: Eddy Current Brake T1901 (220V/50Hz), T1911 (110V/60Hz), T1680 (Cycleforce Basic from the 1990s) 
#         and the motor brake (with power back) T1941 (220V/50hZ) (with several variants T2...)
#
# They all use a 6 wire RJ12 cable to connect the head-unit with the brake and
# at least for the devices I tested, I can say:
#
#     EVERY HEAD-UNIT CAN DRIVE EVERY (newer) BRAKE
#     The "white green" and "white blue" head unit recognize the legacy T1680, but can not drive it
#          
# The "green white" and "blue white" head-units have firmware "inside" and can handle both, eddy current brake and motor brake.
# And even the "solid blue" and "solid green" units can handle both brakes, if you load some 'magic' firmware.

VENDOR_TACX = 0x3561
VENDOR_DYNASTREAM = 0x0fcf

vendors = [ VENDOR_TACX ] # , VENDOR_DYNASTREAM ]

device_types = {
        0x1902 : { 'name' : 'T1902: Old "solid green" IMagic head unit (with or without loaded firmware)', 'allowsfirmware' : True },
        0x1942 : { 'name' : 'T1942: Old "solid blue" Fortius head unit (with firmware loaded)', 'allowsfirmware' : True },
        0xe6be : { 'name' : 'T1942: Old "solid blue" Fortius head unit (without firmware loaded)', 'allowsfirmware' : True } ,
        0x1904 : { 'name' : 'T1904: New "white green" IMagic head unit (white body with green or (sometimes) white ring - firmware inside)' } ,
        0x1932 : { 'name' : 'T1932: New "white blue" VR head unit (white body with blue ring - firmware inside)' },
	# for experimental emulation of ANTUSB stick with EZ-USB
        0x1004 : { 'name' : 'Emulated (or original?) ANTUSB1', 'allowsfirmware' : True },
        0x1008 : { 'name' : 'Emulated (or original?) ANTUSB2', 'allowsfirmware' : True },
        0x1009 : { 'name' : 'Emulated (or original?) ANTUSB-m', 'allowsfirmware' : True },
}

def device2name(device):
    return 'DEVICE ID %04x:%04x on Bus %03d Adresse %03d' % (device.idVendor, device.idProduct, device.bus, device.address)

def list_devices(devices):

    for device in devices:
        print('------------------------------------')
        print('FOUND: {}'.format(device2name(device)))
        if device.idProduct in device_types:
            print('      ', device_types[device.idProduct]['name'])
        else:
            print('       Unknwon Tacx device')


# Firmware Upload/Download
# =======================
#
# from the AN21xx TRM documentation:
#  "These requests are always handled by the EZ-USB core (ReNum=0 or 1). This means that
#   0xA0 is reserved by the EZ-USB chip, and therefore should never be used for a vendor
#   request. Cypress Semiconductor also reserves bRequest values 0xA1 through 0xAF, so
#   your system should not use these bRequest values.
#   A host loader program typically writes 0x01 to the CPUCS register to put the 8051 into
#   RESET, loads all or part of the EZ-USB RAM with 8051 code, and finally reloads the
#   CPUCS register with 0 to take the 8051 out of RESET. The CPUCS register is the only
#   USB register that can be written using the Firmware Download command.
#   Firmware loads are restricted to internal EZ-USB memory."

def writeEzusbVendor_RwInternal(device, addr, data):
    EZUSB_RW_INTERNAL     = 0xA0    #  hardware implements this one
    #EZUSB_RW_MEMORY       = 0xA3
    #EZUSB_RW_EEPROM       = 0xA2
    #EZUSB_GET_EEPROM_SIZE = 0xA5

    assert device.ctrl_transfer(usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_OUT | usb.util.CTRL_RECIPIENT_DEVICE, EZUSB_RW_INTERNAL, addr, 0, data, timeout = 1000) == len(data)
    
def loadHexFirmware(device, filename):

    # MAXSIZE_DEFAULT = 0x1b40
    # CPU program code can go up to 0x1b00. Memory above can access via xdata
    # If we allow usage of Buf 2-7 for (x)code - we can load up to 0x1e40
    MAXSIZE = 0x1e40

    cpucs_addr = 0x7f92
    stopCPU  = bytes([0x01])
    startCPU = bytes([0x00])

    print('Load firmware %s for %s' % (filename, device2name(device)))
    with open(filename, 'r') as file:
        # bmRequestType, bmRequest, wValue and wIndex
        print('....Stop CPU')
        writeEzusbVendor_RwInternal(device, cpucs_addr, stopCPU)

        for line in file:
            assert line[0] == ':'

            bytecount = int( line[1:3], 16 )
            address   = int( line[3:7], 16 )
            rec_type  = int( line[7:9], 16 )
            # bighex = 0 if bytecount == 0 else int( line[9:-3], 16 )
            check     = int( line[-3:], 16 )
            data = bytearray([ int( line[i:i+2], 16 ) for i in range(9, len(line)-4, 2) ])

            cks = ~(bytecount+(address>>8)+address+rec_type+sum(data))+1
            if(cks & 0xff != check):
                raise ValueError("Checksum wrong")

            if rec_type == 0x01:
                break
            if bytecount == 0x00:
                continue

            assert address + bytecount <= MAXSIZE            
            writeEzusbVendor_RwInternal(device, address, data)

        print('....Start CPU')
        writeEzusbVendor_RwInternal(device, cpucs_addr, startCPU)



def ihxSplitTo1(filename):
    with open(filename, 'r') as file:
        for line in file:
            assert line[0] == ':'

            bytecount = int( line[1:3], 16 )
            address   = int( line[3:7], 16 )
            rec_type  = int( line[7:9], 16 )

            if rec_type == 1 and bytecount == 0: 
                print(line)
            for i in range(0, bytecount):
                val = int(line[9+2*i:11+2*i],16)
                pos = 1
                address = address+i
                cks = ~(pos+(address>>8)+address+rec_type+val)+1
                print(":{:02X}{:04X}{:02X}{:02X}{:02X}".format(pos,address, rec_type, val,cks&0xff))


def main():

    
    parser = optparse.OptionParser()
    parser.add_option(
        '-f', '--force', action='store_true', default=False, help='Force firmware download to unknown device.' )
    parser.add_option(
        '-a', '--ant', action='store_true', default=False, help='Allow (presumable emulated) Dynastream ANT Devices' )
    (options, args) = parser.parse_args()

    global vendors

    if options.ant:
       vendors = [ VENDOR_TACX , VENDOR_DYNASTREAM ]

    # *********************************************************

    # find our device
    devices = ([ device for device in usb.core.find(custom_match=lambda e : e.idVendor in vendors, find_all=True) ])

    if not devices or len(devices) == 0:
        raise ValueError('No Device(s) found')
    
    num_devices_before_firmware = len(devices)

    for device in devices:
        print(device2name(device))
        if device.idProduct in device_types:
            print(device_types[device.idProduct])
        else:
            print('Unknwon Tacx device')

    list_devices(devices)


    if len(devices) != len(args):
        print('\nNumber of firmware arguments and number of found devices do not match.')
        exit(1)

    for i in range(0,len(devices)):
       if args[i] == '-':
           print('Skipping {}'.format(device2name(device)))
           continue
       elif (device.idProduct in device_types \
             and 'allowsfirmware' in device_types[device.idProduct] \
             and device_types[device.idProduct]['allowsfirmware'] == True) or options.force:
           loadHexFirmware(devices[i], args[i])
       else:
           print("Unknwon Device or device does not allow firmware download'. Use --force/-f Option to force download." )
           exit(1)

    time.sleep(1)

    # find (all) our device(s) after firmwareload
    devices = ([ device for device in usb.core.find(custom_match=lambda e : e.idVendor in vendors, find_all=True) ])

    retry = 0
    while len(devices) < num_devices_before_firmware:
        retry += 1
        if retry > 5:
            raise ValueError('Missing device after firmware load')
        time.sleep(1)
        print('Waiting for device ... Try again')
        devices = ([ device for device in usb.core.find(custom_match=lambda e : e.idVendor in vendors, find_all=True) ])

    print('\nDevices found after download:')

    list_devices(devices)


if __name__ == '__main__':
    main()
