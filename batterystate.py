from machine import ADC, Pin
from micropython import const
import time

class BatteryState:
    FULL       = const(4.2)                 # these are our reference voltages for a full/empty battery, in volts
    EMPTY      = const(2.8)                 # the values could vary by battery size/manufacturer so you might need to adjust them
    
    def __init__( self ):
        self.vsys       = ADC(Pin(29))      # reads the system input voltage
        self.conversion = 3 * 3.3 / 65535   # Conversion factor
    def getVoltage( self ):
        '''
        Obtain the Voltage from the system.
        '''
        raw = self.vsys.read_u16()
        volt = raw * self.conversion
        #print( f"raw = {raw} voltage = {volt} vsys={self.vsys}" )
        return volt
        
    def getPercentage( self ):
        '''
        Obtain the current presentage of battery left to the system
        '''
        voltage = self.getVoltage()
        percentage = 100 * ((voltage - BatteryState.EMPTY) / (BatteryState.FULL - BatteryState.EMPTY))
        if percentage > 100:
            percentage = 100
        if percentage < 0:
            percentage = 100 * (1/(BatteryState.FULL-BatteryState.EMPTY))
        return percentage
    
    def isCharging( self ):
        return self.getVoltage() > BatteryState.FULL 

if __name__ == "__main__":
    bat = BatteryState()
    while True:
        print( f"Voltage = {bat.getVoltage()}" )
        print( f"Percentage: {bat.getPercentage()}" )
        time.sleep(1)