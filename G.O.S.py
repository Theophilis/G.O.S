import smbus
from time import sleep
import socket
from struct import pack

#network
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host, port = '192.168.1.3', 21621
server_address = (host, port)

#registers and Addresses
PWR_MGMT_1    = 0x6B
SMPLRT_DIV    = 0x19
CONFIG        = 0x1A
GYRO_CONFIG   = 0x1B
INT_ENABLE    = 0x38
ACCEL_XOUT_H  = 0x3B
ACCEL_YOUT_H  = 0x3D
ACCEL_ZOUT_H  = 0x3F
GYRO_XOUT_H   = 0x43
GYRO_YOUT_H   = 0x45
GYRO_ZOUT_H   = 0x47

#mpu functions
def MPU_Init():
    
    #write sample rate to register
    bus.write_byte_data(MPU_Address, SMPLRT_DIV, 7)
    #write power management to register
    bus.write_byte_data(MPU_Address, PWR_MGMT_1, 1)
    #write config to register
    bus.write_byte_data(MPU_Address, CONFIG, 0)
    #write Gyro config to register
    bus.write_byte_data(MPU_Address, GYRO_CONFIG, 24)
    #write interupt to register
    bus.write_byte_data(MPU_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    
    #Accel and Gyro value are 16-bit
    high = bus.read_byte_data(MPU_Address, addr)
    low = bus.read_byte_data(MPU_Address, addr+1)
    #concatenate higher and lower value
    value = ((high << 8) | low)
    #to get signed values
    if (value > 32768):
        value = value-65536
    
    return value

#mux 
class mux:
    
    def __init__(self, bus):
        self.bus = smbus.SMBus(bus)
        
    def channel(self, address=0x72, channel=0):
        
        if (channel==0): action = 0x01
        elif (channel==1): action = 0x02
        elif (channel==2): action = 0x04
        elif (channel==3): action = 0x08
        elif (channel==4): action = 0x10
        elif (channel==5): action = 0x20
        elif (channel==6): action = 0x40
        elif (channel==7): action = 0x80
        else : action = 0x00
        
        self.bus.write_byte_data(address, 0x04, action)
        

channel = 4
plex = mux(1)
plex.channel(0x72, channel)

print(plex)

number_of_sensors = 8
bus = smbus.SMBus(1)
MPU_Address = 0x68


print()
print(bus)
print(MPU_Address)
print('mpu init')

for x in range(number_of_sensors):
    print(x)
    plex.channel(0x72, x)
    MPU_Init()
    
print()
print('ready')

while True:
    channel += 1
    channel = channel%number_of_sensors
    plex.channel(0x72, channel)
    
    try:
        #read raw Accel values
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        #Full scale range +/- 250degree/C as per sensitivity scale factor
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0

        #send Acc data and channel#        
        message = pack('4f', Ax, Ay, Az, channel)
        sock.sendto(message, server_address)
        sleep(.01)
    except:
        print('crash: ' + str(channel))
    
        