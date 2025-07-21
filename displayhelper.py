#
# Constants for display
#
from micropython import const

COLOR_BLACK  = const(0)
COLOR_GREY   = const(1)
COLOR_GREEN  = const(2)
COLOR_RED    = const(3)
COLOR_BLUE   = const(4)
COLOR_PANEL  = const(5)
COLOR_YELLOW = const(6)
COLOR_ORANGE = const(7)

class BaseItem:
    '''
    BaseItem class - This class should be used for any and all items that are to
    be diplayed in a listbox.  This class has the base functionality for a listbox
    and can have the defined functions overridden.
    
    Members:
        text     - The text that is to be displayed when being placed in a listbox
        function - If selected the function that should be called
        color    - The default color text should be printed in. 
    '''
    def __init__(self, text, function=None, defaultColor=COLOR_GREY):
        '''
        Initialize the default base item.  All items should have the methods in
        this item, as they are utilized to display information in listboxes,
        and any other kind of UI selector.
        
        Parameters:
            text         - Text associated with item, normally the name
            function     - Function to call when this item is selected
            defaultColor - Optional, set to the value of grey from the display
            
        '''
        self.text     = text
        self.function = function
        self.color    = defaultColor
        
    def getFunction(self):
        '''
        Return the function that is stored in the base item.  All functions in
        will be called with this item as a parameter so the function can have
        some kind of context.
        
        Returns:
            self.function is returned
        '''
        return self.function
    
    def getColor( self ):
        '''
        Get the color to display the text it.  We default to GREY.  This allows
        items to be created that may want to change the color of an item based
        on some internal parameter.
        
        Users of this will probably want to define and overide this with their
        own function
        
        Returns:
            The defauult color that text in a list box should be created with.
        '''
        return self.color
    
    def __str__(self):
        '''
        Override the default dunder function to return text if this object
        
        Return:
            The text string
        '''
        return self.text
