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

import sys
import os
import gtk
from gimpfu import *  

#Class for the customized panel interface (using gtk as GUI)
class MainDialog(gtk.Window):
  #constructor
  def __init__(self, image, layer, *args):
    mwin = gtk.Window.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments to be hold
    self.img = image
    self.layer = layer
    self.numblursteps = 5

    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)

    #Design the interface
    vbx = gtk.VBox(spacing=10, homogeneous=True)
    self.add(vbx)

    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxa)
    
    lab = gtk.Label("Blurring steps")
    hbxa.add(lab)
    lab.show()
    
    butaadj = gtk.Adjustment(5, 2, 10, 1, 5)
    spbuta = gtk.SpinButton(butaadj, 0, 0)
    spbuta.connect("output", self.on_blurstep_change)
    hbxa.add(spbuta)
    spbuta.show()
    
    hbxa.show()
    
    butok = gtk.Button("OK")
    vbx.add(butok)
    butok.connect("clicked", self.on_butok_clicked)
    butok.show()

    vbx.show()
    self.show()

    return mwin
    
  #callback method, setting the value to the one in the spinbutton
  def on_blurstep_change(self, widget):
    self.numblursteps = widget.get_value()
    
  #callback method, do the blurring
  def on_butok_clicked(self, widget):
    
    #creating the first phase of layers with different blurring
    for i in range(1, int(self.numblursteps)):
      blurlayer = self.layer.copy()
      self.img.add_layer(blurlayer, i)
      pdb.plug_in_mblur(self.img, blurlayer, 0, 5*i, 0, 0, 0)
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
  "Create an animation using the motion blur filter, starting from a base image and animating a blurring effect",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Filters/MakeAnimationBlurring",
  "RGB*, GRAY*",
  [],
  [],
  python_make_blurring
  )

#The main function to activate the script
main()

