#!/usr/bin/python

#Author : Ankit Mishra
#Date : 10 Oct, 2018

"""
   Anti-spoofing Biometric System
"""

import time
import RPi.GPIO as GPIO
from pyfingerprint.pyfingerprint import PyFingerprint
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class my_lcd:
    global LCD_WIDTH, LCD_CHR, LCD_CMD, LCD_LINE_1, LCD_LINE_2
    global LCD_LINE_3, LCD_LINE_4, E_PULSE, E_DELAY
    
    LCD_WIDTH, LCD_CHR, LCD_CMD = 20, True, False
    LCD_LINE_1, LCD_LINE_2, LCD_LINE_3, LCD_LINE_4 = 0x80, 0xC0, 0x94, 0xD4
    E_PULSE, E_DELAY = 0.0005, 0.0005
    
    def __init__(self, pin_rs, pin_e, pins_db):
        
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setup(self.pin_e, GPIO.OUT)  
        GPIO.setup(self.pin_rs, GPIO.OUT)  
        for pin in self.pins_db:  
            GPIO.setup(pin, GPIO.OUT)  
        self.lcd_init()
        self.lcd_clear()

    def lcd_init(self):
        global command
        
        command = [0x33, 0x32, 0x06, 0x0C, 0x01]
        for i in range(len(command)):
            self.lcd_byte(command[i], LCD_CMD)
        
        time.sleep(E_DELAY)
        
    def lcd_clear(self):
        self.lcd_byte(0x01, LCD_CMD)

    def setCursor(x,y):
        if y == 0:
            n=128+x
        elif y == 1:
            n=192+x
        lcd_byte(n, LCD_CMD)

    def lcd_byte(self, bits, mode):
        """ Send command to LCD """    
        time.sleep(0.0005)  
        bits = bin(bits)[2:].zfill(8)          
        GPIO.output(self.pin_rs, mode)  
  
        for pin in self.pins_db:  
            GPIO.output(pin, False)  
  
        for i in range(4):  
            if bits[i] == "1":  
                GPIO.output(self.pins_db[::-1][i], True)    
        self.lcd_toggle_enable()        
        for pin in self.pins_db:  
            GPIO.output(pin, False)  
  
        for i in range(4, 8):  
            if bits[i] == "1":  
                GPIO.output(self.pins_db[::-1][i-4], True)  
        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(E_DELAY)
        GPIO.output(self.pin_e, True)
        time.sleep(E_PULSE)
        GPIO.output(self.pin_e, False)
        time.sleep(E_DELAY)

    def lcd_string(self, message, line):
        # Send string to display        
        message = message.ljust(LCD_WIDTH, " ")        
        self.lcd_byte(line, LCD_CMD)         
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]), LCD_CHR)

class finger():

    def __init__(self):
        print('finger object has been initialized')
        #pass

    def enrollFinger(self):
        lcd.lcd_string("Enrolling Finger", LCD_LINE_1)
        time.sleep(2)
        print('Waiting for finger...')
        lcd.lcd_string("Place Finger", LCD_LINE_1)
        while ( f.readImage() == False ):
            pass
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        if ( positionNumber >= 0 ):
            print('Template already exists at position #' + str(positionNumber))
            lcd.lcd_string("Finger ALready", LCD_LINE_1)
            lcd.lcd_string("   Exists     ", LCD_LINE_2)
            time.sleep(2)
            lcd.lcd_clear()
            return
        lcd.lcd_string("Do not remove", LCD_LINE_1)
        lcd.lcd_string("finger", LCD_LINE_1)
        lcd.lcd_clear()
        while ( f.readImage() == False ):
            pass
        f.convertImage(0x02)
        if ( f.compareCharacteristics() == 0 ):
            print("Fingers do not match")
            lcd.lcd_string("Finger Did not", LCD_LINE_1)
            #lcdcmd(192)
            lcd.lcd_string("   Mactched   ", LCD_LINE_2)
            time.sleep(2)
            return
        f.createTemplate()
        positionNumber = f.storeTemplate()
        print('Finger enrolled successfully!')
        lcd.lcd_string("Stored at Pos:{}".format(str(positionNumber)), LCD_LINE_1)
        lcd.lcd_string("successfully", LCD_LINE_2)
        print('New template position #' + str(positionNumber))
        time.sleep(2)
        lcd.lcd_clear()

    def searchFinger(self):
        try:
            print('Waiting for finger...')
            while( f.readImage() == False ):
                #pass
                time.sleep(.5)
                return
            f.convertImage(0x01)
            result = f.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]
            print('Accuracy is {}'.format(accuracyScore))
            if positionNumber == -1 :
                print('No match found!')
                lcd.lcd_string("No Match Found", LCD_LINE_1)
                time.sleep(2)
                return
            else:
                print('Found template at position #{}'.format(str(positionNumber)))
                lcd.lcd_string("Found at Pos:{}".format(str(positionNumber)), LCD_LINE_1)
                time.sleep(2)

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            #exit(1)

    def deleteFinger(self):
        positionNumber = 0
        count=0
        lcd.lcd_clear()
        lcd.lcd_string("Delete Finger", LCD_LINE_1)
        lcd.lcd_string("Position:{}".format(str(count)), LCD_LINE_2)
        while GPIO.input(enrol) == True:   # here enrol key means ok
            if GPIO.input(inc) == False:
                count=count+1
                if count>1000:
                    count=1000
                lcd.lcd_string("Position:{}".format(str(count)), LCD_LINE_2)        
                time.sleep(0.2)
            elif GPIO.input(dec) == False:
                count=count-1
                if count<0:
                    count=0
                lcd.lcd_string("Position:{}".format(str(count)), LCD_LINE_2)        
                time.sleep(0.2)
        positionNumber=count
        if f.deleteTemplate(positionNumber) == True :
            print('Template deleted!')
            lcd.lcd_clear()
            lcd.lcd_string("Finger Deleted", LCD_LINE_1)
            time.sleep(2)

if __name__ == '__main__':
    enrol=12
    delet=16
    inc=20
    dec=21
    user = finger()
    lcd = my_lcd(4, 5,[6, 13, 19, 26 ])    
    lcd.lcd_string('  Fingerprint', LCD_LINE_1)
    lcd.lcd_string('  Interfacing', LCD_LINE_2)
    time.sleep(1)
    lcd.lcd_string('   IIT Indore', LCD_LINE_1)
    lcd.lcd_string('  Welcomes you', LCD_LINE_2)
    time.sleep(3)
    lcd.lcd_clear()
    GPIO.setup(enrol, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(delet, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(inc, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(dec, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

        while 1:
            #GPIO.output(led, HIGH)
            lcd.lcd_string("Place Finger", LCD_LINE_1)
            if GPIO.input(enrol) == 0:
                #GPIO.output(led, LOW)
                user.enrollFinger()
            elif GPIO.input(delet) == 0:
                #GPIO.output(led, LOW)
                while GPIO.input(delet) == 0:
                    time.sleep(0.1)
                user.deleteFinger()
            else:
                user.searchFinger()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Exception message: ' + str(e))
        
    finally:
        lcd.lcd_clear()
        GPIO.cleanup()
