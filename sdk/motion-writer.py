# -*- coding: utf-8 -*-
# Python 2.7

'''
@file  motion_writer.py
@brief Provide PLENbit motion convert&TX.

'''

__author__    = 'Mitsuhiro MIYAGUCHI'
__copyright__ = 'PLEN Project Company, and all authors.'
__license__   = 'The MIT License'

import sys
import serial
import serial.tools.list_ports
import time
from protocol import Protocol
import ctypes
 
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
 
kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)

class color:
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'

def _findDevice():
    com = None
    # TODO: Will fix device finding method.
    for DEVICE in list(serial.tools.list_ports.comports()):
        if 'mbed Serial Port' in DEVICE[1]:
            com = DEVICE[0]
            break
        elif 'USB Serial Port' in DEVICE[1]:
            com = DEVICE[0]
            break
        elif 'USB シリアル デバイス' in DEVICE[1]:
            com = DEVICE[0]
            break
        else:
            print("Waiting for connection...")
            print(DEVICE[1])
            #print("Please press any key to Continue..")
            #input()
            com = DEVICE[0]
            # COM3 - USB シリアル デバイス (COM3) 
            # ???????
            # dont get device name
    return com

def wait_ack(compareto):
    if read_buf_flag: check_buf = ""
    while 1:
        read_buf = ser.read()#b'.'
        #read_buf = str(ser.read(1))
        if compareto == read_buf:
        #if str(compareto) == read_buf:
            if read_buf_flag:
                if check_buf[0:3] == ">mf": print(check_buf)
                elif check_buf[0:3] == ">MF": print(check_buf)
                elif check_buf[0:1] == ">": print(check_buf)
                #elif not check_buf[0:1] == b"'": print(check_buf)
                #elif not check_buf == 0xff:
                elif not check_buf == "\r\n": print(check_buf)
            if debug_flag: print(color.yellow + compareto + color.end)
            #if debug_flag: print(color.yellow + str(compareto) + color.end)
            break
        elif read_buf:
            if read_buf_flag: 
                #print(read_buf.hex())
                #check_buf = check_buf + read_buf.decode('sjis')#.hex()
                check_buf = check_buf + str(read_buf)

def tx_motion(motion_hex):
    data = [0, 0, 0, 0, 0, 0, 0, 0]
    command = ">"
    list_num = 0
    mf = motion_hex
    list_len = len(mf)
    list_num = 0

    while list_len > list_num:
        if command != mf[list_num]:
            list_num += 1
            continue
        list_num += 1
        if "MF" != (mf[list_num] + mf[list_num+1]):
            list_num += 2
            continue
        list_num += 2
        slot = mf[list_num] + mf[list_num+1]
        flame = mf[list_num+2] + mf[list_num+3]
        list_num += 4
        times = (mf[list_num] + mf[list_num+1] + mf[list_num+2] + mf[list_num+3])
        _time = int(times, 16)
        list_num += 4
        val = 0
        while 1:
            if 24 == val:

                _tx_data=(">MF" + slot + flame + times + data[0]+ data[1]+ data[2]+ data[3]+ data[4]+ data[5]+ data[6]+ data[7])
                time.sleep(0.1)
                ser.write(_tx_data.encode('utf-8'))
                if debug_flag: print (color.green+_tx_data+color.end)
                wait_ack(b'.')
                break

            num = (mf[list_num] + mf[list_num+1] + mf[list_num+2] + mf[list_num+3])

            if val in [3,4,5,6,7,9,10,11,15,16,17,18,19,21,22,23]:
                val = val+1
                list_num += 4
                continue
            elif val == 8:
                _val = 3
            elif val == 12:
                _val = 4
            elif val == 13:
                _val = 5
            elif val == 14:
                _val = 6
            elif val == 20:
                _val = 7
            else :
                _val = val
            
            data[_val] = num

            val = val+1
            list_num += 4

    del mf
    del data
    ser.write("end".encode('utf-8'))
    wait_ack(b';')
    print(color.red+"Done"+color.end)

if __name__ == "__main__":
    import os
    from json import load
    from argparse import ArgumentParser

    arg_parser = ArgumentParser(
                description='This is motion writer',
                epilog='Are you connecting a micro:bit to a PC?\r\nIt is convenient to add -u option to python.',
                )
    
    arg_parser.add_argument(
        '-l', '--list',
        action='store_true',
        help     = 'Motion list')
    arg_parser.add_argument(
        '-n', '--number',
        help     = 'Set motion number.')
    arg_parser.add_argument(
        '-a', '--all',
        action='store_true',
        help     = 'All motion writing.')
    arg_parser.add_argument(
        '-c', '--checkData',
        help     = 'Check Read data.')
    arg_parser.add_argument(
        '-m', '--middle',
        help     = 'from the middle: -m + [start num]')
    arg_parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help     = 'print debug.')
    arg_parser.add_argument(
        '-r', '--readbuf',
        action='store_true',
        help     = 'print readbuf.')
    arg_parser.add_argument(
        '-f', '--file',
        dest     = 'file',
        type     = str,
        metavar  = '<FILE>',
        help     = 'Set motion files path.'
    )

    args = arg_parser.parse_args()

    motion_dir = "./motion-plenbit/"
    motion_list = os.listdir(motion_dir)
    leng = len(motion_list)
    num = 0
    flag = 0
    debug_flag = False
    read_buf_flag = False

    if args.list:
        print("LIST: " + str(leng))
        list_number = 0
        for filename in motion_list:
            print(str(list_number) + ": "+ filename)
            list_number = list_number + 1
        exit()
    elif args.number:
        num = int(args.number)
    elif args.all:
        flag = 1
    elif args.checkData:
        flag = 2
        read_buf_flag = True
    elif args.middle:
        num = int(args.middle)
        flag = 1
    elif args.file:
        motion_list[num] = args.file
        flag = 3
    else :
        print("error, please look help.")
        exit()
        
    if args.debug:
        debug_flag = True
    if args.readbuf:
        read_buf_flag = True

    while 1:
        try:
            com = _findDevice()
            if not com == "None":
                ser = serial.Serial(com, 115200,rtscts = True,dsrdtr = True)
                #ser.open()
                time.sleep(0.5) # protect USB connect error
                break
            else:
                time.sleep(1)
                continue
        except:
            print ("not connect")
            time.sleep(1)
            continue

    if args.checkData:
        s_zero = args.checkData
        s_zero = s_zero.zfill(2)
        print(s_zero)
        ser.write( (">DB" + s_zero).encode('utf-8'))
        wait_ack(b';')

    if not flag == 2:

        if os.path.isfile('device_map.json'):
            with open('device_map.json', 'r') as fin:
                DEVICE_MAP = load(fin)
        elif os.path.isfile('sdk/device_map.json'):
            with open('sdk/device_map.json', 'r') as fin:
                DEVICE_MAP = load(fin)
        else:
            print("'device_map.json' not found" )
            exit()
            
        while 1:
            print ( "Num: " + str(num) )
            if flag == 3:
                fileName = motion_list[num]
                flag = 0
            else :
                fileName = motion_dir + motion_list[num]
            print(motion_list[num])

            with open(fileName, 'r') as fin:
                motion_hex = Protocol(DEVICE_MAP).install(load(fin))
            tx_motion(motion_hex)

            if args.readbuf:
                slice_word = motion_list[num][0:2]
                read_buf_flag = True
                time.sleep(0.1) # makecode is slow
                ser.write ( (">DB" + slice_word).encode('utf-8') )
                wait_ack(b';')

            if flag == 0:
                break
            num += 1
            if(leng == num):
                break
        print(color.green+"Complete"+color.end)