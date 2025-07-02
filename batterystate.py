from machine import ADC, Pin
import time

class BatteryState:
    def __init__( self ):
        self.vsys       = ADC(Pin(29))      # reads the system input voltage
        self.conversion = 3 * (3.3 / 65535)
        self.full       = 4.2               # these are our reference voltages for a full/empty battery, in volts
        self.empty      = 2.8               # the values could vary by battery size/manufacturer so you might need to adjust them

    def getVoltage( self ):
        '''
        Obtain the Voltage from the system.
        '''
        raw = self.vsys.read_u16()
        volt = raw * self.conversion
        #print( f"raw = {raw} voltage = {volt}" )
        #if volt < self.empty:
        #    volt = self.full
        return volt
        
    def getPercentage( self ):
        '''
        Obtain the current presentage of battery left to the system
        '''
        voltage = self.getVoltage()
        percentage = 100 * ((voltage - self.empty) / (self.full - self.empty))
        if percentage > 100:
            percentage = 100
        if percentage < 0:
            percentage = 100 * (1/(self.full-self.empty))
        return percentage
    
    def isCharging( self ):
        return self.getVoltage() > self.full 

if __name__ == "__main__":
    bat = BatteryState()
    print( f"Voltage = {bat.getVoltage()}" )
    print( f"Percentage: {bat.getPercentage()}" )