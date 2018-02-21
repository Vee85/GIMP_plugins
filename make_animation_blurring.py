#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  make_blurred_anim.py
#  
#  Copyright 2018 Valentino Esposito <valentinoe85@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#It creates an animation using the motion blur filter, starting from a base image and animating a blurring linear effect

import sys
import os
import gtk
import gobject
from gimpfu import *

BLURSTEPS = 5
BLURDIR = ["left", "top-left", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left"]
DEFBLURDIR = 0

#Class for the customized panel interface (using gtk as GUI)
class MainDialog(gtk.Window):
  #constructor
  def __init__(self, image, layer, *args):
    mwin = gtk.Window.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments to be hold
    self.img = image
    self.layer = layer
    self.numblursteps = BLURSTEPS
    self.blurdir = 0 #will be reinitialized in GUI construction

    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)

    #Design the interface
    vbx = gtk.VBox(spacing=10, homogeneous=True)
    self.add(vbx)

    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxa)
    
    laba = gtk.Label("Blurring steps")
    hbxa.add(laba)
    laba.show()
    
    butaadj = gtk.Adjustment(BLURSTEPS, 2, 10, 1, 5)
    spbuta = gtk.SpinButton(butaadj, 0, 0)
    spbuta.connect("output", self.on_blurstep_change)
    hbxa.add(spbuta)
    spbuta.show()
    
    hbxa.show()
    
    hbxb = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxb)
    
    labb = gtk.Label("Blur direction")
    hbxb.add(labb)
    labb.show()
    
    boxmodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model
    for i, j in zip(BLURDIR, range(len(BLURDIR))):
      irow = boxmodel.append(None, [i, j])
      if (j == DEFBLURDIR):
        self.blurdir = j

    cbox = gtk.ComboBox(boxmodel)
    rendtext = gtk.CellRendererText()
    cbox.pack_start(rendtext, True)
    cbox.add_attribute(rendtext, "text", 0)
    cbox.set_entry_text_column(0)
    cbox.set_active(0)
    cbox.connect("changed", self.on_cbox_changed)
    hbxb.add(cbox)
    cbox.show()
    
    hbxb.show()
    
    butok = gtk.Button("OK")
    vbx.add(butok)
    butok.connect("clicked", self.on_butok_clicked)
    butok.show()

    vbx.show()
    self.show()

    return mwin
    
  #callback method, setting the step number value to the one in the spinbutton
  def on_blurstep_change(self, widget):
    self.numblursteps = widget.get_value()
   
  #callback method, setting the blurring direction value to the one in the combobox
  def on_cbox_changed(self, widget):
    refmode = widget.get_model()
    self.blurdir = refmode.get_value(widget.get_active_iter(), 1)
    
  #callback method, do the blurring
  def on_butok_clicked(self, widget):
    
    #defining blurring parameters
    blrang = self.blurdir * 45
    
    #creating the first phase of layers with different blurring
    for i in range(1, int(self.numblursteps)):
      blurlayer = self.layer.copy()
      self.img.add_layer(blurlayer, i)
      pdb.plug_in_mblur(self.img, blurlayer, 0, 5*i, blrang, 0, 0)
      blurlayer.name = self.layer.name + "_" + str(i)
      blurlayer.flush()
    
    pdb.gimp_displays_flush()

#The function to be registered in GIMP
def python_make_blurring(img, layer):
  ll = MainDialog(img, layer)
  gtk.main()

  
#The command to register the function
register(
  "python-fu_make_blurring",
  "python-fu_make_blurring",
  "Create an animation using the motion blur filter, starting from a base image and animating a blurring linear effect",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Filters/Animation/BlurMotion",
  "RGB*, GRAY*",
  [],
  [],
  python_make_blurring
  )

#The main function to activate the script
main()

