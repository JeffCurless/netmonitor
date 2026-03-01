#
# This file contains the GUI for a network sniffing PICO-W based project
# 

from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P8, PEN_P4
from pimoroni import RGBLED
from pimoroni import Button
from machine import Pin
from batterystate import BatteryState
import time
import gc

from displayhelper import *

TEXT_HEIGHT = 18
BACKGROUND = 2

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)
    
class Panel:
    def __init__( self, display, title ):
        '''
        Create a display panel.  Panels have a title (optional), and an area
        outlined.  Panels have no special properties, but allow for data to be
        written into them.
        
        '''
        self.display  = display
        self.title    = title
        self.titlex   = Display.TEXT_XOFFSET
        self.titley   = Display.TEXT_YOFFSET
        self.startx   = Display.TEXT_XOFFSET
        self.starty   = Display.TEXT_YOFFSET
        self.height   = display.listHeight - 2
        self.width    = display.listWidth
        self.hasTitle = False
        if self.title == None:
            self.title = ""
        if self.title != "":
            self.hasTitle = True
            self.starty += Display.TEXT_HEIGHT
            self.height -= Display.TEXT_HEIGHT
            
    def clearPanel( self, update=True):
        '''
        Erase everything within the panel that is *not* the border or title.
        
        Parameters:
            update - Update the dislay if requested.
        '''
        self.display.set_pen( Display.BLACK )
        self.display.rectangle( BACKGROUND, self.starty, self.display.listWidth, self.height)
        if update:
            self.display.update()
            
    def changeTitle( self, title, update=False):
        '''
        If a panel has a title, make a change to the title and update if required
        adding a title to a panel is not currently supported...
        
        Parameters:
            title    - The new title
            update   - Update the display if requested.
        '''
        if self.hasTitle:
            self.title = title
        if update:
            self.display.set_pen( Display.PANEL )
            self.display.rectangle( self.titlex, self.titley, self.width, Display.TEXT_HEIGHT )
            self.display.set_pen( Display.GREY )
            self.display.textAt( self.title, 0 )
            self.display.update()
            
    def displayPanel( self, update=True ):
        '''
        Actually display panel.
        
        Parameters:
            update - Update the display as requested.
        '''
        self.display.set_pen( Display.PANEL )
        self.display.rectangle( 0, 0, self.display.width, self.display.height )
        if self.hasTitle:
            self.display.set_pen( Display.GREY )
            self.display.textAt( self.title, 0 )
        self.clearPanel( False )
        if update:
            self.display.update()
            
    def textAt( self, message, line, color, tabs=None, wrap=True ):
        self.display.set_pen( color )
        self.display.textAt( message, line, tabs, wrap )
    
    def textAtClear( self, line ):
        self.display.textAtClear( line )
    
class ListBoxPanel(Panel):
    def __init__( self, display, title ):
        super().__init__( display, title )
        self.itemList = []
        self.tabs     = []
        self.maxTextEntries = ((self.height - self.starty) // Display.TEXT_HEIGHT)+2
           
    def setList( self, itemList, tabs=None ):
        self.itemList = itemList
        if tabs is not None:
            self.tabs = tabs
        
    def fillListBox( self, start, update=True ):
        self.display.set_pen( Display.GREY )
        xOffset = self.startx
        yOffset = self.starty
        count = 0
        for i in range( start, len(self.itemList), 1 ):
            item = self.itemList[i]
            self.display.set_pen( item.getColor() )
            self.display.text( str(item), xOffset, yOffset, tabs=self.tabs )
            yOffset += TEXT_HEIGHT
            if count >= self.maxTextEntries-1:
                break
            count += 1
        if update:
            self.display.update()
            
    def displaySelector( self, line, color, update=True):
        self.display.set_pen( color )
        startx = self.startx - 2
        starty = (line * TEXT_HEIGHT) + self.starty
        stopx  = self.width-2
        stopy  = starty + TEXT_HEIGHT - 2
        self.display.line(startx, starty, stopx,  starty )
        self.display.line(stopx,  starty, stopx,  stopy  )
        self.display.line(stopx,  stopy,  startx, stopy  )
        self.display.line(startx, stopy,  startx, starty )
        if update:
            self.display.update()
            
    def clearListBox(self):
        self.display.set_pen( Display.BLACK )
        self.display.rectangle( BACKGROUND, self.starty, self.display.listWidth, self.height)
        
    def draw( self, asyncFunc=None ):
        self.displayPanel(False)
        #self.clearListBox()
        
        start = 0
        self.fillListBox(start,False)
        waiting = True
        line = 0
        self.displaySelector(line, Display.RED)
        
        item = None
        count = 0
        while waiting:
            if asyncFunc and (count % 10) == 0:
                # Once a second check check the async function...
                self.itemList = asyncFunc()
                self.clearListBox()
                self.fillListBox( start, False )
                self.displaySelector( line, Display.RED )
                gc.collect()
            if self.display.getUpButton():
                if line > 0:
                    self.displaySelector( line, Display.BLACK, False )
                    line -= 1
                    self.displaySelector( line, Display.RED )
                elif start > 0:
                    start -= 1
                    self.clearListBox()
                    self.fillListBox( start, False )
                    self.displaySelector( line, Display.RED )
            elif self.display.getDownButton():
                if line < self.maxTextEntries-1 and line < len(self.itemList)-1:
                    self.displaySelector( line, Display.BLACK, False )
                    line += 1
                    self.displaySelector( line, Display.RED )
                elif len(self.itemList)-start > self.maxTextEntries:
                    start += 1
                    self.clearListBox()
                    self.fillListBox( start, False )
                    self.displaySelector( line, Display.RED )
            elif self.display.getSelButton():
                if (line+start) < len(self.itemList):
                    item = self.itemList[line+start]
                else:
                    print( 'Select pressed - item out of range' )
                    item = None
                waiting = False
            elif self.display.getCancelButton():
                print( 'Cancel Pressed' )
                item = None
                waiting = False
            count += 1
            time.sleep( 0.1 )
        return item   
        
class Display:
    '''
    Display class.  This class exposes a number of functions that create graphics
    on the PICO_DISPLAY_PACK_2 (though it will work on many other platforms).
    
    Note that what we are really doing is writing to a display buffer... that
    buffer is not updated to the screen until update() is called.  The update
    function transfers the current display buffer onto the display screen, thus
    showing what the user intended.
    
    Two typical issues:
        1)  update() is not being called, so ... nothing is being displayed
        2)  update() is being called to often resulting in flashing screens.
        
    Note: Graphics Modes:
    
    1) PEN_P4     - (4 bit) Allows for 16 colors to be selected, each must be predefined
    2) PEN_P8     - (8 bit) Allows for 256 colors
    3) PEN_RGB565 - (16 bit) Allows for 64K colors... and LOTS of RAM used
    
    Memory used by Display Buffer:
    
    DISPLAY_PICO_DISPLAY_2 is 320x240 pixels, or 76,800 pixles.
    
    PEN_P4     - 76,800 pixels at 4 bits per pixel  ->  38,400 bytes
    PEN_P8     - 76,800 pixels at 8 bits per pixel  ->  76,800 bytes
    PEN_RGB565 - 76,800 pixels at 16 bits per pixel -> 153,600 bytes
    
    PEN_4 takes the least ram, and if you are only using a few colors... it works
    out quite well.
    '''
    
    BLACK  = COLOR_BLACK
    GREY   = COLOR_GREY
    GREEN  = COLOR_GREEN
    RED    = COLOR_RED
    BLUE   = COLOR_BLUE
    PANEL  = COLOR_PANEL
    YELLOW = COLOR_YELLOW
    ORANGE = COLOR_ORANGE
    
    TEXT_XOFFSET = BACKGROUND+5
    TEXT_YOFFSET = BACKGROUND+2
    TEXT_HEIGHT  = TEXT_HEIGHT
    
    def __init__(self):
        '''
        Initialize the display class.  This class provides a number of function.
        This class simply wraps the PicoGraphics class to make this a little
        easier on the caller.  In some situations, extending the functionality
        of the orignal.
        
        Using PEN_P4 Graphics mode, this provides a 16 color palette that we can use,
        each pen MUST be predefined.
        '''
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, rotate=0, pen_type=PEN_P4)
        
        self.display.set_font( "bitmap8" )
        self.width, self.height = self.display.get_bounds()
        self.listWidth  = self.width - (BACKGROUND*2)
        self.listHeight = self.height - (BACKGROUND*2)
        
        self.blackPen   = self.display.create_pen(  0,   0,   0)
        self.greyPen    = self.display.create_pen(190, 190, 190)
        self.GreenPen   = self.display.create_pen(  0, 255,   0)
        self.RedPen     = self.display.create_pen(255,   0,   0)
        self.BluePen    = self.display.create_pen(  0,   0, 255)
        self.panelPen   = self.display.create_pen(  0,   0, 128)
        self.yellowPen  = self.display.create_pen(255, 255,   0)
        self.orangePen  = self.display.create_pen(255, 165,   0)
        
        self.led        = RGBLED(6, 7, 8)
        self.led.set_rgb( 0, 0, 0 )
        #
        self.button_up  = Button(12)
        self.button_dwn = Button(13)
        self.button_x   = Button(14)
        self.button_y   = Button(15)
        #   
        self.set_backlight( 0.8 )
        self.maxTextEntries = (self.listHeight - BACKGROUND + 2)//TEXT_HEIGHT
                     
    def set_pen( self, pen ):
        '''
        Set the pen to a new color.  We use the defined constant colors in the
        Display class to determine which pen should be used.  This makes it so
        no other code needs to know what the PEN object type is.
        
        Parameters:
            pen    - Which color value do we want to set the pen to
            
        Note:  Micropython does not yet support match/case syntax.
        '''
        if pen == Display.BLACK:
            self.display.set_pen( self.blackPen )
        elif pen == Display.GREY:
            self.display.set_pen( self.greyPen )
        elif pen == Display.GREEN:
            self.display.set_pen( self.GreenPen )
        elif pen == Display.RED:
            self.display.set_pen( self.RedPen )
        elif pen == Display.BLUE:
            self.display.set_pen( self.BluePen )
        elif pen == Display.PANEL:
            self.display.set_pen( self.panelPen )
        elif pen == Display.YELLOW:
            self.display.set_pen( self.yellowPen )
        elif pen == Display.ORANGE:
            self.display.set_pen( self.orangePen )
        else:
            self.display.set_pen( self.BluePen )
        
    def set_backlight( self, value ):
        '''
        Turn on the backlight to a value between 0 and 1
        
        Parameter:
            value - Value of the backlight to set
        '''
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self.display.set_backlight(value)
        
    def update(self):
        self.display.update()
        
    def text( self, message, x, y, width=0, tabs=None):
        if width == 0:
            width = self.listWidth
        if tabs is None or len(tabs) == 0:
            self.display.text( message, x, y, width, 2, fixed_width=False )
        else:
            strings = message.split( '\t' )
            for i,msg in enumerate(strings):
                self.display.text( msg, x+tabs[i], y, width, 2, fixed_width=False )
            
    def textAt( self, message, line, tabs=None, wrap=True ):
        if wrap:
            width = self.listWidth - 2
        else:
            width = self.display.measure_text( message, 2 ) + 10
        xpos  = self.TEXT_XOFFSET
        ypos  = self.TEXT_YOFFSET + (line * self.TEXT_HEIGHT)
        if tabs is None or len(tabs) == 0:
            self.display.text( message, xpos, ypos, width, 2, fixed_width=False )
        else:
            strings = message.split( '\t' )
            for i,msg in enumerate(strings):
                self.display.text( msg, xpos+tabs[i], ypos, width, 2, fixed_width=False )

    def textAtClear( self, line ):
        width = self.listWidth - self.TEXT_XOFFSET
        xpos  = self.TEXT_XOFFSET
        ypos  = self.TEXT_YOFFSET + (line * self.TEXT_HEIGHT)
        self.display.set_pen( self.blackPen )
        self.display.rectangle( xpos, ypos, width, self.TEXT_HEIGHT)
        
    def rectangle( self, xstart, ystart, xend, yend ):
        self.display.rectangle( xstart, ystart, xend, yend )
        
    def line( self, xstart, ystart, xend, yend):
        self.display.line( xstart, ystart, xend, yend)
        
    def getCancelButton(self):
        return self.button_y.read()
    
    def getUpButton( self ):
        return self.button_up.read()
    
    def getDownButton( self ):
        return self.button_dwn.read()
        
    def getSelButton( self ):
        return self.button_x.read()
        
    def LED(self,R,G,B):
        self.led.set_rgb( R, G, B )
        
    def createListBox( self, title ):
        return ListBoxPanel( self, title )
    
    def createPanel( self, title ):
        return Panel( self, title )

def dummy( item ):
    print( f"Called Dummy with {item}")
    
if __name__ == "__main__":
    items = []
    tabs = [0,270]
    for i in range(15):
        items.append( BaseItem( f"Line Number {i+1}\tWWW", dummy ) )
    display = Display()
    panel = display.createListBox( 'Test...' )
    panel.setList( items, tabs )
    panel.draw()

    