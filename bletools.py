import bluetooth
import time
import re

from displayhelper import *
from micropython import const

# Define BLE event constants
_IRQ_CENTRAL_CONNECT             = const(1)
_IRQ_CENTRAL_DISCONNECT          = const(2)
_IRQ_GATTS_WRITE                 = const(3)
_IRQ_GATTS_READ_REQUEST          = const(4)
_IRQ_SCAN_RESULT                 = const(5)
_IRQ_SCAN_DONE                   = const(6)
_IRQ_PERIPHERAL_CONNECT          = const(7)
_IRQ_PERIPHERAL_DISCONNECT       = const(8)
_IRQ_GATTC_SERVICE_RESULT        = const(9)
_IRQ_GATTC_SERVICE_DONE          = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE   = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT     = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE       = const(14)
_IRQ_GATTC_READ_RESULT           = const(15)
_IRQ_GATTC_READ_DONE             = const(16)
_IRQ_GATTC_WRITE_DONE            = const(17)
_IRQ_GATTC_NOTIFY                = const(18)
_IRQ_GATTC_INDICATE              = const(19)
_IRQ_GATTS_INDICATE_DONE         = const(20)
_IRQ_MTU_EXCHANGED               = const(21)
_IRQ_L2CAP_ACCEPT                = const(22)
_IRQ_L2CAP_CONNECT               = const(23)
_IRQ_L2CAP_DISCONNECT            = const(24)
_IRQ_L2CAP_RECV                  = const(25)
_IRQ_L2CAP_SEND_READY            = const(26)
_IRQ_CONNECTION_UPDATE           = const(27)
_IRQ_ENCRYPTION_UPDATE           = const(28)
_IRQ_GET_SECRET                  = const(29)
_IRQ_SET_SECRET                  = const(30)

# _IRQ_GATTS_READ_REQUEST event, available return codes are:
_GATTS_NO_ERROR                          = const(0x00)
_GATTS_ERROR_READ_NOT_PERMITTED          = const(0x02)
_GATTS_ERROR_WRITE_NOT_PERMITTED         = const(0x03)
_GATTS_ERROR_INSUFFICIENT_AUTHENTICATION = const(0x05)
_GATTS_ERROR_INSUFFICIENT_AUTHORIZATION  = const(0x08)
_GATTS_ERROR_INSUFFICIENT_ENCRYPTION     = const(0x0f)

# for _IRQ_PASSKEY_ACTION event, available return codes are:
_PASSKEY_ACTION_NONE               = const(0)
_PASSKEY_ACTION_INPUT              = const(2)
_PASSKEY_ACTION_DISPLAY            = const(3)
_PASSKEY_ACTION_NUMERIC_COMPARISON = const(4)

ADDR_TYPE_PUBLIC = const(0)
ADDR_TYPE_RANDOM = const(1)

_ADV_IND        = const(0)          # Connectble and scannable undirected advertising
_ADV_DIRECT_IND = const(1)          # connectabe directed advertising
_ADV_SCAN_IND   = const(2)          # scannable undirected advertising
_ADV_NONCONN_ID = const(3)          # non-connectable undirected advertising
_ADV_SCAN_RSP   = const(4)          # scan response

_ADTYPE_FLAGS       = const(0x01)   # Flags (usually in ADV, not SCAN_RSP)
_ADTYPE_SERVICEID   = const(0x02)   # Incomplete list of service ID's
_ADTYPE_SERVICEIDS  = const(0x03)   # Complete list of 16 bit servce ID's
_ADTYPE_SHORT_NAME  = const(0x08)   # Shortened Local Name
_ADTYPE_COMPLETE    = const(0x09)   # Complete Local Name
_ADTYPE_POWERLEVEL  = const(0x0A)   # TX Power Level
_ADTYPE_SERVICEDATA = const(0x16)   # Service Data - 16-bit UUID
_ADTYPE_APPERANCE   = const(0x19)   # Appearance
_ADTYPE_AD_INTERVAL = const(0x1A)   # Advertising Interval
_ADTYPE_MAN_DATA    = const(0xFF)   # Manufacturer Specific Data

class BLEItem(BaseItem):
    def __init__(self, addr_type, addr, adv_type, rssi, adv_data, itemFunction  ):
        super().__init__( bytes(addr).hex(), itemFunction )
        self.name      = bytes(addr).hex()
        self.addr      = self.name
        self.addr_type = addr_type
        self.adv_type  = adv_type
        self.rssi      = rssi
        self.adv_data  = bytes(adv_data).hex()
        self.data      = []
        
    def getAddrType(self):
        if self.addr_type == ADDR_TYPE_PUBLIC:
            return "PUBLIC"
        elif self.addr_type == ADDR_TYPE_RANDOM:
            return "RANDOM"
        else:
            return "UNKNOWN"
        
    def getColor(self):
        if self.rssi > -67:
            return COLOR_GREEN
        elif self.rssi > -70:
            return COLOR_YELLOW
        elif self.rssi > -80:
            return COLOR_ORANGE
        elif self.rssi > -90:
            return COLOR_RED
        else:
            return COLOR_RED
        
    def getName( self ):
        return self.name
       
    def decodeName( self, data ):
        return "".join([chr(int(data[i],16)) for i in range(0,len(data)) ])
        #name = ""
        #for i in range(0,len(data)):
        #    name += chr(int(data[i],16))
        #return name
    
    def _addData( self, AdType, AdData ):
        '''
        Add an item to our advertisement data list.  Every item in the list is a
        tuple consisting of the type of data, and the data itself.  If we already
        have that data, toss it.  If not, add it to our stored data items
        
        Parameters:
            AdType - Type of advertisement data inbound
            AdData - Advertisement data we want to store.
            
        '''
        for item in self.data:
            if item[0] == AdType:
                return
        self.data.append( (AdType, AdData ) )
        
    def _leSwap16( self, data ):
        '''
        Convert a 16 bit data item into a little endian data type (i.e. byte swap)
        
        Parameter:
            Two bydes of data
            
        Returns:
            The two bytes swapped.
        '''
        value = [ data[1], data[0] ]
        return "".join( value ).upper()
        
    
    def decode( self ):
        if self.adv_type >= _ADV_IND and self.adv_type <= _ADV_SCAN_RSP:
            data = [self.adv_data[i:i+2] for i in range(0, len(self.adv_data), 2)]
            while len(data) > 0:
                length = int(data[0],16)
                AdType = int(data[1],16)
                if AdType == _ADTYPE_COMPLETE:
                    self.name = self.decodeName(data[2:length+1])
                    self._addData( "CompleteName", self.name )
                elif AdType == _ADTYPE_SHORT_NAME:
                    self.name = self.decodeName(data[2:length+1])
                    self._addData( "ShortName",self.name )
                elif AdType == _ADTYPE_SERVICEDATA:
                    self._addData( "UUID", "".join(data[2:length+1]) )
                elif AdType == _ADTYPE_MAN_DATA:
                    self._addData( "ManData", "".join(data[2:length+1]) )
                elif AdType == _ADTYPE_FLAGS:
                    self._addData( "Flags", "".join(data[2:length+1]) )
                elif AdType == _ADTYPE_SERVICEID:
                    value = self._leSwap16( data[2:length+1])
                    if value == "FEAF" or value == "FEB0":
                        value = "Nest Labs Inc"
                    elif value == "FE96" or value == "FE97":
                        value = "Tesla Motors"
                    elif value == "1122":
                        value = "BasicPrinting"
                    self._addData( "Service ID", value )
                elif AdType == _ADTYPE_SERVICEIDS:
                    self._addData( "All Service IDs", "".join(data[2:length+1]) )
                elif AdType == _ADTYPE_POWERLEVEL:
                    self._addData( "PowerLevel", "".join(data[2:length+1]) )
                else:
                    self._addData( AdType, "".join(data[2:length+1]) )
                data = data[length+1:]
        
    def __str__(self):
        self.decode()
        return f"{self.name}\t{self.addr_type}\t{self.adv_type}\t{self.rssi}"

class BLEList:
    def __init__(self):
        self.mylist = []
        self.index  = -1
        
    def __iter__(self):
        '''
            iterator - Make it so that we can iterate over this class, just like an array
        '''
        self.index = -1
        return self
    
    def __next__(self):
        '''
            next - Obtain the next item in the list, assuming __iter__ was called first
        '''
        self.index += 1
        if self.index < len(self.mylist):
            return self.mylist[self.index]
        else:
            raise StopIteration
    
    def __getitem__( self, index ):
        '''
            This function is used to access a specific item within the list, allowing this
            class to be used like and array (i.e. it implments the required code for making
            [] work.
        '''
        #print( f"__getitem__( {index} ), {len(self.mylist)}" )
        if index < len(self.mylist):
            return self.mylist[index]
        else:
            raise StopIteration
        
    def __len__( self ):
        '''
        __len__ - This function returns the number of items within the WLANList.
        '''
        return len(self.mylist)
    
    def addItem( self, bleItem ):
        global stuff
        '''
        addItem - This function adds an item into the mylist, if and only if it is not a duplicate.
                  The definition of a duplicate is address matches 
        '''
        for item in self.mylist:
            if item.addr == bleItem.addr:
                item.rssi     = bleItem.rssi
                item.adv_type = bleItem.adv_type
                item.adv_data = bleItem.adv_data
                item.decode()
                return
        print( f"Found : {bleItem}\t{bleItem.adv_data}" )
        bleItem.decode()
        self.mylist.append( bleItem )
    
class BLEScanner:
    def __init__(self, ble, itemFunction):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._scan_results = None
        self._itemFunction = itemFunction
        self._filter = None
        
    def __del__():
        self.stop_scan()
        
    def _irq(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            
            item = BLEItem( addr_type, addr, adv_type, rssi, adv_data, self._itemFunction )
            if self._filter is not None:
                if item.addr == self._filter:
                    self._scan_results.addItem( item )
            else:
                self._scan_results.addItem( item )
        elif event == _IRQ_SCAN_DONE:
            print("Scan complete.")
            
    def getMACAddress(self):
        addr = bytes(self._ble.config('mac')[1]).hex()
        return ":".join([addr[i:i+2] for i in range(0, len(addr), 2)] )
        
    def start_scan(self, duration_ms=5000, interval_us=1000000, window_us=1000000, active=False):
        """
        Starts a BLE scan.
        :param duration_ms: Duration of the scan in milliseconds. 0 for indefinite.
        :param interval_us: Scan interval in microseconds.
        :param window_us: Scan window in microseconds.
        :param active: True for active scanning (requests scan response), False for passive.
        """
        self._scan_results = BLEList()
        print(f"Starting BLE scan for {duration_ms}ms...")
        self._ble.gap_scan(duration_ms, interval_us, window_us, active)
        
    def setFilter( self, address ):
        self._filter = address
        self._scan_results = BLEList()
        
    def get_scan_results(self):
        return self._scan_results
    
    def stop_scan(self):
        self._ble.gap_scan( None )

def makeAscii( data ):
    n = 2
    line = [data[i:i+n] for i in range(0, len(data), n)]
    string = ""
    for ch in line:
        letter = chr(int(ch,16))
        if letter >= 'a' and letter <= 'z':
            string += letter
        elif letter >= 'A' and letter <= 'Z':
            string += letter
        elif letter >= '0' and letter <= '9':
            string += letter
        else:
            string += '_'
    return string
    
if __name__ == "__main__":
    
    def dummy(item):
        return item
    def getMACAddress( addr ):
        address = f"{addr[0:2]}:{addr[2:4]}:{addr[4:6]}:{addr[6:8]}:{addr[8:10]}:{addr[10:12]}"
        return address
    
    ble = bluetooth.BLE()
    scanner = BLEScanner( ble, dummy )
    
    print( f"Running on {scanner.getMACAddress()}")
    scanner.start_scan(10000,active=True)
    
    print( "Listing found items..." )
   
    count = 0
    while count < 20:
        time.sleep( 1 )
        count += 1  
    
    for item in scanner.get_scan_results():
        print( f"{item.name} {item.addr} {item.getAddrType()} ")
        for data in item.data:
            print( f"   {data[0]}:{data[1]}" )
        
        #print( f"Addr_type: {item.getAddrType()} Address: {item.name.upper()} RSSI: {item.rssi} AdvType: {item.adv_type} Data: {item.adv_data}" )
        #print( f"{item.name.upper()} {item.addr} {item.getAddrType()} {item.adv_type} {item.decoded}") #\n    Org: {item.adv_data}\n    Data:{makeAscii(item.adv_data)}" )
