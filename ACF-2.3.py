import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Power Button
GPIO.setup(16, GPIO.OUT) #Lower Gate
GPIO.setup(21, GPIO.OUT) #Induction
GPIO.setup(20, GPIO.OUT) #Upper Gate
GPIO.setup(26, GPIO.OUT) #Radiator Fans
GPIO.setup(13, GPIO.OUT) #Water Pump
GPIO.setup(19, GPIO.OUT) #Induction Fans

lcd = CharLCD('PCF8574', 0x27)
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)

casecount = 0
casecountorg = 0
coiltime = 0
topgatetime = .3
bottomgatetime = .5
pumpstartup = 5
pumpshutdown = 10

def exit_button_callback(channel):
    GPIO.output(16, GPIO.LOW)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
    GPIO.output(26, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)
    print('\r\nEMERGENCY STOP!')
    lcd.cursor_pos = (0, 1)
    lcd.write_string('EMERGENCY STOP!                 ')
    GPIO.cleanup()
    exit(0)

#GPIO.add_event_detect(4, GPIO.RISING, callback=exit_button_callback,bouncetime = 500)

lcd.cursor_pos = (0, 1)
lcd.write_string('Starting up...')

time.sleep(1)
lcd.cursor_pos = (1, 2)
lcd.write_string('ACF Annealer')
time.sleep(2)
lcd.clear()
time.sleep(2)
lcd.cursor_pos = (0, 4)
lcd.write_string('Version:')
lcd.cursor_pos = (1, 5)
lcd.write_string('1.0.8')

GPIO.output(19, GPIO.HIGH)

time.sleep(2)

while coiltime == 0:
    lcd.cursor_pos = (0, 0)
    lcd.write_string('Set Coil Time:                  ')
    coilinput = input('Set Coil Time:')
    try:
        coiltime = float(coilinput)
    except:
        print('Invalid Entry!')
        continue
print('Coil Timer Set to', coiltime, 'Seconds.')
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string('Coil Timer Set\r\nto ' + str(coiltime) + ' Seconds ')
time.sleep(3)
lcd.clear()

while casecount == 0:
    lcd.cursor_pos = (0, 0)
    lcd.write_string('Number of Cases to Anneal: ')
    casecountinp = input('Number of Cases to Anneal: ')
    try:
        casecount = int(casecountinp)
    except:
        print('Invalid Entry!')
        continue
print('Set to Anneal', casecount, 'Cases.')
lcd.clear()
lcd.cursor_pos = (0, 0)
lcd.write_string('Set to Anneal\r\n' + str(casecount) + ' Cases.')
time.sleep(3)

lcd.cursor_pos = (0, 0)
lcd.write_string('Press START     \r\nButton          ')
print('Press START Button')
#launch = input('Press ENTER to Begin')
try:
    GPIO.wait_for_edge(4, GPIO.FALLING)
except KeyboardInterrupt:
    GPIO.cleanup()

print('Turning on cooling system...    ')
GPIO.output(26, GPIO.HIGH)
GPIO.output(13, GPIO.HIGH)
lcd.cursor_pos = (0, 0)
lcd.write_string('Turning on      \r\ncooling system..')
time.sleep(pumpstartup)
lcd.clear()
casecountorg = casecount
while casecount > 0:
    print('Annealing Case', casecountorg-casecount+1, 'Out of', casecountorg)
    lcd.cursor_pos = (0, 0)
    lcd.write_string('Annealing Case\r\n ' + str(casecountorg - casecount + 1) + ' Out of ' + str(casecountorg))
    print('Open Top Case Gate                     ', end='\r')
    GPIO.output(20, GPIO.HIGH)
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Open Top        \r\nCase Gate       ')
    time.sleep(topgatetime)
    print('Close Top Case Gate                    ', end='\r')
    GPIO.output(20, GPIO.LOW)
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Close Top       \r\nCase Gate       ')
    time.sleep(.5)
    print('Case Stabilizing...                     ', end='\r')
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Case Stabilizing...             ')
    time.sleep(1.5)
    #lcd.clear()
    print('Turn on Coil for', coiltime, 'Seconds  ', end='\r')
    GPIO.output(21, GPIO.HIGH)
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Turn on Coil    \r\nfor ' + str(coiltime) + ' Seconds' )
    time.sleep(coiltime)
    GPIO.output(21, GPIO.LOW)
    print('Open Bottom Case Gate                  ', end='\r')
    GPIO.output(16, GPIO.HIGH)
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Open Bottom     \r\nCase Gate       ')
    time.sleep(bottomgatetime)
    print('Close Bottom Case Gate                 ', end='\r')
    GPIO.output(16, GPIO.LOW)
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Close Bottom    \r\nCase Gate       ')
    time.sleep(1)
    #print('Waiting for Bottom Gate...             ', end='\r')
    #lcd.cursor_pos = (0, 0)
    #lcd.write_string('Waiting for     \r\nBottom Gate...  ')
    #time.sleep(1)
    lcd.clear()
    casecount = casecount - 1
print('Completed!                        ', end='\r')
lcd.cursor_pos = (0, 0)
lcd.write_string('Completed!')
print('Cooling down system...')
lcd.cursor_pos = (0, 0)
lcd.write_string('Cooling down    \r\nsystem...       ')
time.sleep(pumpshutdown)
GPIO.output(26, GPIO.LOW)
GPIO.output(13, GPIO.LOW)
GPIO.output(19, GPIO.LOW)
print('Completed!')
lcd.cursor_pos = (0, 0)
lcd.write_string('Complete!                       ')
GPIO.cleanup()