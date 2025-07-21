from batterystate import BatteryState
from display import Display
from wifitools import WLAN, WLANList, WIFIScanner
from bletools import BLEScanner, BLEItem
from displayhelper import BaseItem
import time
import gc
import bluetooth

class LANItem( BaseItem ):
    def __init__( self, wlan, function ):
        self.wlan = wlan
        msg = str(wlan)
        super().__init__( msg, function )
        
    def getColor(self):
        if self.wlan.rssi > -67:
            return Display.GREEN
        elif self.wlan.rssi > -70:
            return Display.YELLOW
        elif self.wlan.rssi > -80:
            return Display.ORANGE
        elif self.wlan.rssi > -90:
            return Display.RED
        else:
            return Display.RED
        
    def getName( self ):
        if self.wlan.ssid == "":
            return f"{self.wlan.bssid}"
        return f"{self.wlan.ssid}"
    
    def __str__(self):
        return str(self.wlan)   

def dummy( item ):
    print( f"Called {item}" )
    
def scaleValue( value, start,stop):
    result = abs(value) + start
    if result > stop:
        result = stop
    return result

def displayLine( xstart, ystart, height):
    display.rectangle( xstart, ystart, 2, height-ystart )
    display.set_pen( Display.BLACK )
    display.rectangle( xstart, 102, 2, ystart-102)
    display.set_pen( Display.GREY )
    display.rectangle( xstart+2, 102, 2, height-102)
    
def watchSingleNetwork( item ):
    '''
    Monitor a single network.  Get the network by SSID and report on the
    power/channel and Security.  Generate a graph of the relative signale
    strength
    
    Parameters:
        item - the network wlan item we are monitoring
        
    Returns:
        True  - if we want to coninue viewing other networks
        False - Terminate the montioring and bounce back to the root function
    '''
    panel = display.createPanel( f"Monitoring {item.getName()}" )
    count = 0
    graphHeight = display.height - 2 #panel.height
    graphWidth  = panel.width
    xpos = 2 #panel.startx
    panel.displayPanel(False)
    display.set_pen( Display.PANEL )
    display.line( 0, 100, graphWidth, 100 )
    tabs = [0,100]
    while True:
        if display.getCancelButton():
            return False
        if display.getSelButton():
            return True
        if count % 20 == 0:
            display.LED( 0, 0, 128 )
            lan = wscanner.scanForSpecificWLAN( item.wlan.ssid, 1 )
            if lan is None:
                lan = item.wlan
            else:
                item.wlan = lan
            display.LED( 0, 0, 0 )
            panel.textAtClear( 2 )
            panel.textAt( f"Channel:\t{lan.channel}", 1, Display.GREY, tabs=tabs )
            panel.textAt( f"RSSI:\t{lan.rssi}", 2, item.getColor(),tabs=tabs)
            panel.textAt( f"Security:\t{lan.getSecurity()}", 3, Display.GREY,tabs=tabs)
            value = scaleValue( lan.rssi, 100, graphHeight )
            display.set_pen( item.getColor() )
            displayLine( xpos, value, graphHeight)
            xpos += 2
            if xpos > graphWidth:
                xpos = panel.startx
            count = 0
            display.update()
        count += 1
        time.sleep( 0.1 )
    return True

def systemStatus(item):  
    panel = display.createPanel( 'System Status' )
    count = 0
    tabs = [0, 180]
    panel.displayPanel(False)
    
    while not display.getCancelButton():
        if count % 20 == 0:
            panel.displayPanel(False)
            count = 0
            gc.collect()
            panel.textAt( f"Memory Used:\t{gc.mem_alloc()}", 1, Display.GREY, tabs=tabs )
            panel.textAt( f"Memory Free:\t{gc.mem_free()}", 2, Display.GREY, tabs=tabs )
            if bs.isCharging():
                panel.textAt( f"Battery:\tCharging...", 3, Display.GREY, tabs=tabs )
            else:
                panel.textAt( f"Voltage:\t{bs.getVoltage():.2f}",     3, Display.GREY,tabs=tabs )
                panel.textAt( f"Percentage:\t{bs.getPercentage():.2f}%", 4, Display.GREY,tabs=tabs )
            display.update()
        count += 1
        time.sleep( 0.1 )
    return False

def watchSingleBLE( item ):
    panel = display.createPanel( f"Monitoring {item.getName()}" )
    panel.displayPanel(False)
    count = 0
    while True:
        if display.getCancelButton():
            return True
        if display.getSelButton():
            return True
        if count % 20 == 0:
            panel.textAt( f"Address Type: {item.getAddrType()}", 1, Display.GREY )
            panel.textAtClear( 2 )
            panel.textAt( f"RSSI: {item.rssi}",2, item.getColor() )
            line = 3
            for data in item.data:
                panel.textAt( f"{data[0]}: {data[1]}",line,Display.GREY,wrap=False)
                line += 1
            display.update()
        count += 1
        time.sleep( 0.1 )
        

def bluetoothDisplay( item ):
    listBox = display.createListBox( 'Blue Tooth' )
    running = True
    scanner.start_scan(0,active=True)
    items = []
    tabs = [0,190, 210, 270,0]
    while running:
        items = scanner.get_scan_results()
        if len(items):
            listBox.setList( items, tabs )
            item = listBox.draw(asyncFunc=scanner.get_scan_results)
            if item is None:
                running = False
            else:
                function = item.getFunction()
                running = function(item)
        else:
            time.sleep( 0.1 )
    return False

def networkDisplay(item):
    '''
    Display the currently available wireless networks available, and display
    information about them.
    
    Parameters:
        A context item from where every we were called from.  In this
        case we do not care about the context item, as we are using it
        to simply redirect us here.
        
    Returns: False
    '''
    panel = display.createListBox( "Networking" )
    panel.displayPanel()
    wlanList = WLANList()
    running = True
    tabs = [0,240,275,0]
    while running:
        panel.changeTitle( "Scanning...", True )
        display.LED( 0, 0, 128 )
        wscanner.scanForWLANS( wlanList, 1 )
        wlanList.sortItems()
        items = []
        for lan in wlanList:
            items.append( LANItem( lan, watchSingleNetwork ) )
        display.LED( 0, 0, 0 )
        panel.changeTitle( "Networking" )
        panel.setList( items, tabs )
        item = panel.draw()
        if not item is None:
            function = item.getFunction()
            running = function( item )
    return False
    
bs = BatteryState()
scanner = BLEScanner(bluetooth.BLE(),watchSingleBLE)
wscanner  =  WIFIScanner()
display = Display()

mainItems = []
mainItems.append( BaseItem( f"Status",    systemStatus ) )
mainItems.append( BaseItem( f"BlueTooth", bluetoothDisplay ) )
mainItems.append( BaseItem( f"Networks",  networkDisplay ) )

mainPanel = display.createListBox( "System Status" )
mainPanel.setList( mainItems )

gc.enable()

while True:
    item = mainPanel.draw()
    if not item is None:
        function  = item.getFunction()
        function( item )