import pymodbus
import time
import serial
from struct import *
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from pymodbus.transaction import ModbusRtuFramer

#import logging
#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

#count= the number of registers to read
#unit= the slave unit this request is targeting
#address= the starting address to read from

client = ModbusClient(method = "rtu", port="/dev/ttyUSB0",stopbits = 1, bytesize = 8, parity = 'E', baudrate= 19200)
#Connect to the serial modbus server
connection = client.connect()
#print(connection)

#Starting add, num of reg to read, slave unit.
#result = client.read_holding_registers(0x00,1,unit= 0xff)
#temps = client.read_input_registers(1, 2, unit=0x02) # address, count, slave address
#print(temps)

#result = client.read_holding_registers(0x02,2,unit= 0x02)
while (True):
    result400 = client.read_holding_registers(400,2,unit= 0x02)
    result12 = client.read_holding_registers(12,2,unit= 0x02)
    result24 = client.read_holding_registers(24,2,unit= 0x02)
    result180 = client.read_holding_registers(180,2,unit= 0x02)
#print(result400.registers)
    print("Temp", unpack('>f', pack('>HH', result400.registers[1], result400.registers[0])))
#print(result12.registers)
    print("Condutividade", unpack('>f', pack('>HH', result12.registers[1], result12.registers[0])))
#print(result24.registers)
    print("TDG", unpack('>f', pack('>HH', result24.registers[1], result24.registers[0])))
#print(result180.registers)
    print("LDO", unpack('>f', pack('>HH', result180.registers[1], result180.registers[0])))
    time.sleep(1)
#setruct.unpack(">fff","0x2 0x3 0x1 0x92 0x0 0x2 0x64 0x29")
#mypack = pack('>HH',16821, 36105)
#f = unpack('>f', mypack)
#print(f)



#Closes the underlying socket connection
client.close()
