# NetMonitor

A GUI based network and bluetooth monitor using a Raspberry PI Pico and a Pimornoni DISPLAY_PACK_2


## Outstanding work
- [ ] Modify the wifi code to constantly monitor for addresses much like the bluetooth module does
- [ ] Comment all of the display code
- [ ] Try to determine why the battery code works sometimes and not others
- [ ] Overall cleanup of code

> [!NOTE]
> This code is supported on an standard PICO, with a Pimoroni DISPLAY_PACK_2 attached.
> 

## Hardware
- [DISPLAY_PACK_2](https://shop.pimoroni.com/products/pico-display-pack-2-0?variant=39374122582099)
- [Raspberry PI PICO-W](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- [LiPo SHIM for Pico](https://shop.pimoroni.com/products/pico-lipo-shim?variant=32369543086163)
  
## STL files for the case

All of the STL files for the case are in the STL sub-directory.  Note that there is a .3mf file for the case top.  The case top consistes of the main top, an up-arrow, a down-arrow an LED Defuser, and a small design.  These are printed in diffent colors from the main body.  The 3mf file works on a PRUSA MK4S though I suspect it will work on many, many others.  All your should have to do is select the colors, on per "extruder".  Since my printer only has a single extruder, I added in a color change to the gcode for the "tool change" this makes the color changes work.

