import time
import machine
import network
import binascii

#
# wlan - A class that contains a WLAN we are aware of.
#
class WLAN:
    def __init__(self,ssid,bssid,channel,rssi,security,hidden):
        self.ssid     = ssid
        self.bssid    = bssid
        self.channel  = channel
        self.rssi     = rssi
        self.security = security
        self.hidden   = hidden
        self.count    = 0
        
    def getSSID( self, width=24 ):
        ssid = self.ssid[:24]
        while len(ssid) < 24:
            ssid += ' '
        return ssid
    def getBSSID( self, width=24 ):
        bssid = self.bssid[:24]
        while len(bssid) < 24:
            bssid += ' '
        return bssid
    
    def getSecurity( self ):
        #            0       1          2      3              4       5               6
        security = ["OPEN", "WEP-PSK", "WPA", "WEP-PSK/WPA", "WPA2", "WEP-PSK/WPA2", "WPA2/WPA", "WEP-PSK/WPA/WPA2"]
        if self.security < len(security):
            return security[self.security]
        else:
            return str(self.security)
            
    def __str__(self):
        if self.ssid == "":
            msg = f"{self.getBSSID()}"
        else: 
            msg = f"{self.getSSID()}\t{self.channel:>2}\t{self.rssi:>3}"
        return msg

    def __repr__( self ):
        return f"WLAN(\"{self.ssid}\", {self.bssid}, {self.channel}, {self.rssi}, {self.security}, {self.hidden} )"
        
#
# WLANList - This class is used to create a list of the WLAN's we have seen during a scan.
#
# This class supports being itereated, printed, and supports random access and obtaining the length.
#
class WLANList:
    def __init__( self ):
        self.wlanlist = []
        self.count    = 0
        
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
        if self.index < len(self.wlanlist):
            return self.wlanlist[self.index]
        else:
            raise StopIteration
        
    def __getitem__( self, index ):
        '''
            This function is used to access a specific item within the list, allowing this
            class to be used like and array (i.e. it implments the required code for making
            [] work.
        '''
        if index < len(self.wlanlist):
            return self.wlanlist[index]
        else:
            raise StopIteration
        
    def __len__( self ):
        '''
        __len__ - This function returns the number of items within the WLANList.
        '''
        return len(self.wlanlist)
    
    def __repr__( self ):
        data = f"WLANList( {self.count}, {self.wlanlist})"
        return data
    
    def addItem( self, lan ):
        '''
        addItem - This function adds an item into the WLANList, if and only if it is not a duplicate.
                  The definition of a duplicate is the BSSID matches.  
        '''
        for item in self.wlanlist:
            if item.ssid == lan.ssid:
                item.rssi = lan.rssi
                item.channel = lan.channel
                return
            elif item.bssid == lan.bssid:
                item.rssi = lan.rssi
                item.channel = lan.channel
                return

        lan.count = self.count
        self.count += 1
        self.wlanlist.append( lan )
            
    def defaultSort( self, item ):
        """
        defaultSort  - The default sort function, given an item it returns the Received Signal
                       Strength Indicator, or RSSI of the item selected.  This can be used to
                       sort by best to worst signal strength
        """
        return item.rssi
    
    def sortItems( self, sortFunction=None ):
        """
        sortItems - This function will automatically sort the wlanlist based on the passed in
                    sort function.  If there is no sort function provided, this code will utilize
                    the defaultSort function of sorting by the RSSI of the WLANs.
        """
        if sortFunction == None:
            self.wlanlist.sort( reverse=True, key=self.defaultSort )
        else:
            self.wlanlist.sort( reverse=True, key=sortFunction )

class WIFIScanner:
    def __init__(self):
        self.wlan = network.WLAN()
        self.wlan.active(True)
        
    def scanForWLANS( self, wlanList, iterations = 1):
        '''
        Scan the network looking for wifi networks.
        
        Parameters:
            wlanList    - A location to store the data found
            iterations  - Number of times to scan prior to returning to the caller
        
        '''

        while( iterations > 0 ):
            networks = self.wlan.scan()
            for w in networks:
                lan = WLAN( w[0].decode(),binascii.hexlify(w[1]).decode(),w[2],w[3],w[4],w[5])
                wlanList.addItem(lan)
            
            iterations -= 1
            if iterations > 0:
                time.sleep( 1 )

    def scanForSpecificWLAN( self, ssid, iterations = 10 ):
        '''
        scanForSpecificWLAN - This routine scans for a specific SSID
        
        We scan for a specific SSID, and when found return it.  This routine
        can be used to help graph the power of a specific SSID.
        
        Parameters:
            ssid       - The specific SSID to scan the network for.
            iterations - The number of times to scan prior to returning to the caller
            
        '''

        while( iterations > 0 ):
            networks = self.wlan.scan()
            for w in networks:
                lan = WLAN( w[0].decode(),binascii.hexlify(w[1]).decode(),w[2],w[3],w[4],w[5])
                if lan.ssid == ssid:
                    return lan
            iterations -= 1
            if iterations > 0:
                time.sleep( 1 )
        return None
