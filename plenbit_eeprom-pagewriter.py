# plenbit motion writer
from microbit import *

romAD1 = 0x56
romAD2 = 0x57


flag = False
def flash():
    global flag
    if flag:
        display.set_pixel(0,0,9)
        flag = False
    else:
        display.set_pixel(0,0,0)
        flag = True

def graph(percent):
    if percent >= 100: percent = 100
    for x in range(5):
        for y in range(5):
            if (4-int(percent/20)) <= y:
                display.set_pixel(x,y,9)
    
    

'''
PLENmini
>MF1900016800000000000000b8000000000000019f
ack
>MF190103e8ffa201f4fddd00c3000001f40000014b
ack
>MF1902012cff0501f4fed400c4000001f400000107
ack
>MF1903012cff0501f4fed400c8000001f4000000d5
ack
>MF19040258ff0501f4fed400ccfda701ea000000de
ack
>MF1905015e01b9fdc5ffbd00930000fdcd00000011
ack
>MF190600c801b9fdc5ffbd00930000fdcd00000011
ack
>MF190700c8ff5efe60ffbd00930000fe53000000b9
ack
>MF190800c80000ff73ffbd00930000000000000000
ack
>MF1909016800000000000000000000000000000000
ack
end!

PLEN2
>MF190001680000000000000000000000000000000000b800000000000000000000000000000000000000000000019f000000000000
>MF190103e8ffa201f4fddd0000000000000000000000c3000000000000000001f4000000000000000000000000014b000000000000

'''

def weep(eepAdr, value):
    data = bytearray(3)
    data[0]=eepAdr >> 8 #msb
    data[1]=eepAdr & 0xFF #lsb
    data[2]=value
    i2c.write(romAD1, data, repeat = False)
    #print(data)
    sleep(5)#20
    return("OK")

def weep_page(eepAdr, value):   #adrres bug! buf error?

    dataFloat = bytearray(2)
    data = bytearray(2)
    data[0]=eepAdr >> 8 #msb
    data[1]=eepAdr & 0xFF #lsb

    counter = eepAdr
    float_flag = False
    #if debugFlag: print(value)
    for i in value:
        neko = counter % 64
        # 1Mbit EEPROM: 256byte pagewrite
        # 128kb EEPROM: 64byte  motion end num 17 file
        # 64 -> ANnTeI
        # need 512kb ?
        #print("adress",counter)
        if(float_flag):
            dataFloat.append(i)
        elif not neko == 0:
            data.append(i)
        else:
            ###print("next page",counter)
            float_flag = True
            dataFloat[0]=counter >> 8
            dataFloat[1]=counter & 0xFF
            dataFloat.append(i)
        counter+=1

    #if debugFlag: print(data)
    i2c.write(romAD1, data, repeat = False)
    sleep(20)

    if(float_flag):
        #print("page error")
        #print(dataFloat)
        #if debugFlag: print(dataFloat)
        i2c.write(romAD1, dataFloat, repeat = False)
        sleep(20)
    return("OK")

def reep(eepAdr = 0x00, num = 1):
    data = bytearray(2)
    data[0]=eepAdr >> 8
    data[1]=eepAdr & 0xFF
    i2c.write(romAD1, data)
    value = (i2c.read(romAD1, num, repeat=False))
    return value[:]

def checkEprom(eepAdr):
    adrrr = initial_zone + interval * eepAdr
    for _val in range(0, 20):
            """
            if line_num > 43:
                _n = reep(adrrr,43)
                print(str(_n, 'utf-8'))
                adrrr = adrrr + 43

                _n = reep(adrrr,line_num - 43)
                print(str(_n, 'utf-8'))
                adrrr = adrrr + line_num - 43

            else:"""
            _n = reep(adrrr,line_num)
            print(str(_n, 'utf-8'))
            adrrr = adrrr + line_num
    sleep(300)
    print(b';')

print("start")
_motion_adr = 0
_stage = 0
display.show("E")

read_num = 0x7100 #28500
read_num = 0

#PLENbit
initial_zone = 0x32
interval = 860
line_num = 43
#PLEN2
#initial_zone = 0x520
#interval = 0x520
#line_num = 107

debugFlag = False

_stage = 0
_start_adr = 0
_resetEEPROM = True
_nHead = ""

while 1:
    adr = 0
    if button_a.is_pressed():
        #test R/W
        i = 0
        v = 0
        value = 20
        for i in range(0, 20):
            # servo posison reset
            weep(v,0xff)
            v = v + 1

        """
        sleep(300)
        _adr = 0

        #weep_page (_adr, b'1000')
        weep(_adr,255)
        weep (_adr+1, 254)
        _n = reep(_adr,2)
        _adr += 1
        print(_n)
            """



    elif button_b.is_pressed():
        #test Read
        sleep(300)
        #adrrr = 0    # 0x00
        #adrrr = 0x32+860    # 0x00
        #_n = reep(adrrr,50)

        print(read_num)
        _n = reep(read_num,32)
        #_n = reep(read_num,128)
        print(_n)

        read_num += 32 #0x520

    if uart.any():
        if _stage == 0:
            if _resetEEPROM:
                # 初期位置データ吸出し
                initPosition = reep(0,50)
                
                # モーションデータ削除
                display.clear()
                
                for x in range(255):
                    weep_page(x * 255,bytearray(b'\xff'*255))
                    graph(x/255*100)

                # 初期位置データ書き込み
                    weep_page(0,initPosition)

                print(";")
                _resetEEPROM = False

            display.show(Image('00000:'
                               '00000:'
                               '97521:'
                               '00000:'
                               '00000'))
            sleep(20)
            
            _nHead = uart.read(3)
            
            if _nHead == b'>MF':
                _stage = 1

            elif _nHead == b'>DB':
                display.show("D")
                #print("checkEEPROM")
                testnum = uart.read(2)
                testnum2 =  str(testnum)
                testnum3 = int(testnum2, 16)
                checkEprom( testnum3 )
                #print(b';')
                display.show("E")
            elif _nHead == b'com':
                break
        elif _stage == 1:
            display.show(Image('00000:'
                               '00000:'
                               '15951:'
                               '00000:'
                               '00000'))
            sleep(20)
            
            #slot
            _n_slot = uart.read(2)
            
            
            #if debugFlag: print(_n_slot)
            if _n_slot:
                _n_adr =  int(_n_slot,16)
                ###print(_n_adr)
                #_motion_adr = 0x32 + 860 * _n_adr
                _motion_adr = initial_zone + interval * _n_adr
                ###print(_motion_adr)
                _start_adr = _motion_adr
                _end_adr = _start_adr + interval
                _stage = 2
                weep_page(_motion_adr, _nHead)
                _motion_adr += 3
    
                weep_page(_motion_adr, _n_slot)
                _motion_adr += 2
                #flame
                #time
        elif _stage == 2:
            display.show(Image('00000:'
                               '00000:'
                               '13579:'
                               '00000:'
                               '00000'))
            sleep(20)
            
            #_n = uart.read(1)# byte Write
            _n = uart.read(line_num)#org
            
            #if debugFlag: print(_n)

            #if _n == b';':#endcode
            flash()
            if _n:
                if _n == b'end':
                    """
                    #FF Ume
                    while 1:
                        if _end_adr <= _motion_adr:
                            break
                        weep (_motion_adr,int.from_bytes(b'\xff', 'big'))
                        _motion_adr += 1
                    print("end",_motion_adr)
                    #FF
                    """
                    weep (_motion_adr, int.from_bytes(b'\xff', 'big'))
                    while uart.any()==False: print(";")
                    _stage = 0
                    display.show("b")
                else:
                    # page Write
                    # 1page = 256byte
    
                    _len = len(_n)
                    #print(_len)
                    weep_page(_motion_adr, _n)
                    
                    #if debugFlag: print(reep(_motion_adr,line_num))
                    if debugFlag: print(reep(_motion_adr,_len))
                    _motion_adr += _len
    
                    """
                    # byte Write
                    weep (_motion_adr, int.from_bytes(_n, 'big'))
                    _motion_adr += 1
                    """
    
                    _adr_count = _motion_adr - _start_adr
    
                    if _adr_count == 53:
                        while uart.any()==False: print(".")
                        _n = uart.read(54)
                    #if debugFlag: print("total",_adr_count)
                    if _adr_count == line_num:
                        #print(b'.')#ack
                        while uart.any()==False: print(".")
                        _start_adr = _motion_adr
                        #_stage = 0
                    elif _adr_count >= line_num:
                            #print("total",_adr_count)
                        while uart.any()==False: print("bo")#bufferover

        #serialread()