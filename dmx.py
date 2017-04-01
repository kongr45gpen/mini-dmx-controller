#!/usr/bin/env python


import multiprocessing
import time
import pygtk
pygtk.require('2.0')
import gtk
import math

import serial
if __name__ == "__main__":
    ser = serial.Serial('COM3', 9600)

# Convenience functions

import sys

class DMXWidgets:
        
    def chanval(self, chan, val):
        if self.dmxoff is True:
            sys.stdout.write("\r%d -> N/A \t [master@%f]" % (chan,self.adjm.value))
            return
        if self.blackout.get_active():
            val = 0
        else:
            val = val * (self.adjm.value)
        self.chanval_raw(chan, val)
        sys.stdout.write("\r%d -> %d  \t [master@%f]" % (chan,val,self.adjm.value))
        sys.stdout.flush()
        
    def chanval_raw(self, chan, val):
        ser.write('%dc %dw' % (chan, val))
        
    def cb_dmx(self, get, chan):
        self.chanval(chan, get.value)
    
    def cb_master(self, get):
        for i in xrange(1,4):
            self.chanval(i, self.adjustments[i].value)
    
    def cb_reset(self, get):
        for i in xrange(1,7):
            self.chanval(i, self.adjustments[i].value)
    
    def cb_dmxoff(self, get):
       self.dmxoff = get.get_active()
    
    def cb_mode(self, get):
        dmxval = {
            0: 0,
            1: 0,
            2: 50,
            3: 80,
            4: 110,
            5: 140,
            6: 180,
            7: 210,
            8: 240
        }
        
        i = get.get_active()
        if i == 0:
            self.adjustments[5].set_value(0)
        self.moderange.set_value(dmxval[i])
        
    def cb_zero(self, get, i):
        self.adjustments[i].set_value(0)
    
    def cb_full(self, get, i):
        self.adjustments[i].set_value(255)
   
    def cb_colours(self, get, rgb):
        self.adjustments[1].set_value(rgb[0])
        self.adjustments[2].set_value(rgb[1])
        self.adjustments[3].set_value(rgb[2])

    def cb_fadeout(self, get):
        currentValue = self.adjm.value
        def clock():
            for i in range(256):
                if i%4!=255%4:
                    continue
                self.adjm.set_value(currentValue * 1/(math.expm1(1))*math.expm1((255-i)/256.0))
                while gtk.events_pending():
                    gtk.main_iteration_do(False)
                time.sleep(10/1000.0)
        clock()
    
    def cb_fadein(self, get):
        currentValue = self.adjm.value*255.0
        def clock():
            for i in range(0, 256):
                if i%5!=255%5:
                    continue
                i = i+currentValue-currentValue/255.0*i
                self.adjm.set_value(1/(math.expm1(1))*math.expm1((i)/255.0))
                while gtk.events_pending():
                    gtk.main_iteration_do(False)
                time.sleep(10/1000.0)
        clock()

    def __init__(self):
        self.dmxoff = False
        self.colours = [
            ("Red", (255,0,0)),
            ("Green", (0,255,0)),
            ("Blue", (0,0,255)),
            ("Cyan", (0,255,255)),
            ("Magenta", (255,0,255)),
            ("Lime", (255,255,0)),
            ("Orange", (255,55,0)),
            ("Yellow", (255,72,0)),
            ("Natural", (255,77,18)),
            ("White", (255,152,58)),
            ("Full", (255,255,255))
        ]
    
        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", lambda w: gtk.main_quit())
        self.window.set_title("range controls")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.tooltips = gtk.Tooltips()

        box1 = gtk.VBox(False, 0)
        self.window.add(box1)

        labels = {
            1: "R",
            2: "G",
            3: "B",
            4: "white",
            5: "strobe & speed",
            6: "mode"
        }
        
        self.adjustments = {}
        
        boxh = gtk.HBox(False, 20)
        boxh.set_border_width(20)
        
        blackout = gtk.CheckButton("Blackout")
        self.blackout = blackout
        blackout.connect("toggled", self.cb_master)
        boxh.pack_start(blackout, True, True, 0)
        
        dmxoff = gtk.CheckButton("DMX Off")
        self.dmxoff = dmxoff
        dmxoff.connect("toggled", self.cb_dmxoff)
        boxh.pack_start(dmxoff, True, True, 2)
        
        reset = gtk.Button("Refresh")
        reset.connect("clicked", self.cb_reset)
        boxh.pack_start(reset, False, False, 0)
        
        fadeout = gtk.Button("Fadeout")
        fadeout.connect("clicked", self.cb_fadeout)
        boxh.pack_start(fadeout, False, False, 0)
        fadein = gtk.Button("Fadein")
        fadein.connect("clicked", self.cb_fadein)
        boxh.pack_start(fadein, False, False, 0)
        
        box1.pack_start(boxh, True, True, 0)
        
        box2 = gtk.HBox(False, 5)
        box2.set_border_width(5)
        for colour in self.colours:
            button = gtk.Button(colour[0])
            button.connect("clicked", self.cb_colours, colour[1])
            self.tooltips.set_tip(button, str(colour[1]))
            box2.pack_start(button, True, True, 0)
        box1.pack_start(box2, False, False, 0)
        
        box2 = gtk.HBox(False, 20)
        box2.set_border_width(20)
          
        label = gtk.Label("Master")
        box2.pack_start(label, False, False, 0)

        box2 = gtk.HBox(False, 20)
        box2.set_border_width(20)
          
        label = gtk.Label("Master")
        box2.pack_start(label, False, False, 0)
         
        adjm = gtk.Adjustment(1.0, 0.0, 1.0, 1/255.0, 1/255.0, 0.0)
        self.adjm = adjm
        adjm.connect("value_changed", self.cb_master)
        scale = gtk.HScale(adjm)
        scale.set_digits(3)
        box2.pack_start(scale, True, True, 0)
        
        box1.pack_start(box2, True, True, 0)
        
        for i in xrange(1,7):
            box2 = gtk.HBox(False, 10)
            box2.set_border_width(10)
            
            label = gtk.Label(labels[i])
            box2.pack_start(label, False, False, 0)
            
            adj3 = gtk.Adjustment(0.0, 0.0, 255.0, 1.0, 25.0, 0.0)
            self.adjustments[i] = adj3
            adj3.connect("value_changed", self.cb_dmx, i)
            scale = gtk.HScale(adj3)
            scale.set_digits(0)
            box2.pack_start(scale, True, True, 0)
          
            box1.pack_start(box2, True, True, 0)
            
            if i==6:
                # 0  - 31: normal & strobe
                # 31 - 63: fade in
                # 64 - 95: fade out
                # 96 -127: fade in & out
                # 128-159: colour change (smooth)
                # 160-223: colour change (immediate, 3 colors)
                # 224-255: audio sensitive
                self.moderange = adj3
                combobox = gtk.combo_box_new_text()
                combobox.append_text("Normal")
                combobox.append_text("Strobe (& Normal)")
                combobox.append_text("Fade In")
                combobox.append_text("Fade Out")
                combobox.append_text("Fade In & Out")
                combobox.append_text("Colour Change (smooth)")
                combobox.append_text("Colour Change (rough, 3 colours)")
                combobox.append_text("Colour Change (rough, 7 colours)")
                combobox.append_text("Audio")
                combobox.connect('changed', self.cb_mode)
                box2.pack_start(combobox, False, False, 0)
                combobox.set_active(0)
            else:
                reset = gtk.Button("Refresh")
                reset.connect("clicked", self.cb_reset)
                
                zero = gtk.Button(" 0 ")
                zero.connect("clicked", self.cb_zero, i)
                box2.pack_start(zero, False, False, 0)
                
                if i != 4:
                    full = gtk.Button(" F ")
                    full.connect("clicked", self.cb_full, i)
                    box2.pack_start(full, False, False, 0)

        separator = gtk.HSeparator()
        box1.pack_start(separator, False, True, 0)

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box2.set_size_request(400, -1)
        box1.pack_start(box2, False, True, 0)

        button = gtk.Button("Quit")
        button.connect("clicked", lambda w: gtk.main_quit())
        box2.pack_start(button, True, True, 0)
        button.set_flags(gtk.CAN_DEFAULT)
        button.grab_default()
        self.window.show_all()

def main():
    gtk.main()
    return 0            

if __name__ == "__main__":
    DMXWidgets()
    main()
