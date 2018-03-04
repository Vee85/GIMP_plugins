#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  make_animation_snowing.py
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

#This script creates an animation superimposing a snowing effect on an image
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

import sys
import os
import math
import random
import gtk
import gobject
from gimpfu import *

COVERAGE = 10 #a percentage
FRAGMENTATION = ["low", "medium", "high"]
DEFFRAGM = [10, 30, 60]
DIRECTIONS = ["down", "right", "top", "left"]
DEFDIRECTION = 0
SPEEDS = ["slow", "medium", "fast"]
DEFSPEED = [2, 5, 10]
OBSCIINT = ["null", "weak", "medium", "strong"]
DEFOBSCIINT = [0, 1, 3, 6]
TIME = 1

#generic function used by
def gdkcoltorgb(gdkc):
  red = int(gdkc.red_float * 255)
  green = int(gdkc.green_float * 255)
  blue = int(gdkc.blue_float * 255)
  return (red, green, blue)


#class holding information on a single flake
class SnowFlake:
  #constructor
  def __init__(self, r, x, y):
    self.r = r
    self.x = x
    self.y = y
    
  #method, get list with coord [x y]
  def get_coord(self):
    return [self.x, self.y]
    
  #method, set arbitrary coordinates
  def set_coord(self, x, y):
    self.x = x
    self.y = y
    
  #method, apply a speed to move the 
  def push_speed(self, vx, vy):
    self.x = self.x + vx
    self.y = self.y + vy


#Class for the customized GUI
class MainApp(gtk.Window):
  #constructor
  def __init__(self, image, drawab, *args):
    mwin = gtk.Window.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments
    self.img = image
    self.drawab = drawab
    self.cover = COVERAGE
    self.direc = 0 #will be reinitialized in GUI costruction
    self.speed = 0 #will be reinitialized in GUI costruction
    self.obsci = 0 #will be reinitialized in GUI costruction
    self.pn = 0 #will be reinitialized in GUI costruction
    self.sncol = gtk.gdk.Color(65535, 65535, 65535) #initialized to white
    self.time = TIME * 10.0
    self.savepath = os.getcwd() #will be updated by user choice

    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)

    #Designing the interface
    vbx = gtk.VBox(spacing=10, homogeneous=True)
    self.add(vbx)
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxa)
    
    laba = gtk.Label("Maximum coverage allowed")
    hbxa.add(laba)
    
    butaadj = gtk.Adjustment(COVERAGE, 5, 80, 1, 5)
    spbuta = gtk.SpinButton(butaadj, 0, 0)
    spbuta.connect("output", self.on_coverage_change)
    hbxa.add(spbuta)

    #new row    
    hbxd = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxd)
    
    labd = gtk.Label("Fragmentation")
    hbxd.add(labd)
    
    boxmodelc = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(FRAGMENTATION, DEFFRAGM):
      irow = boxmodelc.append(None, [i, j])

    self.pn = DEFFRAGM[0]

    cboxc = gtk.ComboBox(boxmodelc)
    rendtextc = gtk.CellRendererText()
    cboxc.pack_start(rendtextc, True)
    cboxc.add_attribute(rendtextc, "text", 0)
    cboxc.set_entry_text_column(0)
    cboxc.set_active(0)
    cboxc.connect("changed", self.on_fragmentation_changed)
    hbxd.add(cboxc)
    
    #new row
    hbxb = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxb)
    
    labb = gtk.Label("Motion direction")
    hbxb.add(labb)
    
    boxmodela = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(DIRECTIONS, range(len(DIRECTIONS))):
      irow = boxmodela.append(None, [i, j])
      if (j == DEFDIRECTION):
        self.direc = j

    cboxa = gtk.ComboBox(boxmodela)
    rendtexta = gtk.CellRendererText()
    cboxa.pack_start(rendtexta, True)
    cboxa.add_attribute(rendtexta, "text", 0)
    cboxa.set_entry_text_column(0)
    cboxa.set_active(self.direc) #is an index
    cboxa.connect("changed", self.on_direction_changed)
    hbxb.add(cboxa)
    
    #new row
    hbxc = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxc)
    
    labc = gtk.Label("Motion Speed")
    hbxc.add(labc)
    
    boxmodelb = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(SPEEDS, DEFSPEED):
      irow = boxmodelb.append(None, [i, j])

    self.speed = DEFSPEED[0]

    cboxb = gtk.ComboBox(boxmodelb)
    rendtextb = gtk.CellRendererText()
    cboxb.pack_start(rendtextb, True)
    cboxb.add_attribute(rendtextb, "text", 0)
    cboxb.set_entry_text_column(0)
    cboxb.set_active(0)
    cboxb.connect("changed", self.on_speed_changed)
    hbxc.add(cboxb)

    #new row
    hbxe = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxe)
    
    labe = gtk.Label("Strength of obscillations")
    hbxe.add(labe)
    
    boxmodeld = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(OBSCIINT, DEFOBSCIINT):
      irow = boxmodeld.append(None, [i, j])

    self.obsci = DEFOBSCIINT[1]

    cboxd = gtk.ComboBox(boxmodeld)
    rendtextd = gtk.CellRendererText()
    cboxd.pack_start(rendtextd, True)
    cboxd.add_attribute(rendtextd, "text", 0)
    cboxd.set_entry_text_column(0)
    cboxd.set_active(1)
    cboxd.connect("changed", self.on_obsci_changed)
    hbxe.add(cboxd)

    #new row
    hbxf = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxf)
    
    labf = gtk.Label("Snow color")
    hbxf.add(labf)
    
    #colorbutton
    colbu = gtk.ColorButton()
    colbu.set_color(self.sncol)
    hbxf.add(colbu)
    colbu.connect("color-set", self.on_color_chosen)

    #new row
    hbxg = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxg)
    
    labg = gtk.Label("Animation time (seconds)")
    hbxg.add(labg)
    
    butgadj = gtk.Adjustment(TIME, TIME, 20.0, 0.1, 5.0)
    spbutg = gtk.SpinButton(butgadj, 0, 1)
    spbutg.connect("output", self.on_time_change)
    hbxg.add(spbutg)

    #new row
    butok = gtk.Button("OK")
    vbx.add(butok)
    butok.connect("clicked", self.on_butok_clicked)

    self.show_all()
    return mwin
    
  #callback method, setting the coverage factor to the one in the spinbutton
  def on_coverage_change(self, widget):
    self.cover = widget.get_value()
    
  #callback method, setting the fragmentation to the one in the combobox
  def on_fragmentation_changed(self, widget):
    refmode = widget.get_model()
    self.pn = refmode.get_value(widget.get_active_iter(), 1)
  
  #callback method, setting the direction to the one in the combobox
  def on_direction_changed(self, widget):
    refmode = widget.get_model()
    self.direc = refmode.get_value(widget.get_active_iter(), 1)

  #callback method, setting the speed to the one in the combobox
  def on_speed_changed(self, widget):
    refmode = widget.get_model()
    self.speed = refmode.get_value(widget.get_active_iter(), 1)

  #callback method, setting the strength of obscillation to the one in the combobox
  def on_obsci_changed(self, widget):
    refmode = widget.get_model()
    self.obsci = refmode.get_value(widget.get_active_iter(), 1)

  #callback method, setting the snow color
  def on_color_chosen(self, widget):
    self.sncol = widget.get_color()

  #callback method, setting the animation time (frame numbers)
  def on_time_change(self, widget):
    self.time = widget.get_value() * 10.0 #each frame is 0.1 seconds
  
  #callback method, do the animation
  def on_butok_clicked(self, widget):
    oldfgcol = pdb.gimp_context_get_foreground()
    oldbrush = pdb.gimp_context_get_brush()
    
    #setting the color
    pdb.gimp_context_set_foreground(gdkcoltorgb(self.sncol))
    
    #setting basic dimension
    ww = pdb.gimp_image_width(self.img)
    hh = pdb.gimp_image_height(self.img)
    
    imarea = ww * hh
    covarea = imarea * (self.cover/100)
    porad = math.sqrt((covarea / self.pn) / math.pi) #radius of a circle
    
    #initializing the flake list
    flakes = [None] * self.pn
    for i in range(self.pn):
      rx = random.uniform(1, ww)
      ry = random.uniform(1, hh)
      npr = porad * (1 + (0.5 * random.random()))
      fl = SnowFlake(npr, rx, ry)
      flakes[i] = fl
    
    #creating the layer copies if there is only one layer
    if (len(self.img.layers) == 1):
      baselayer = self.img.layers[0]
      bname = baselayer.name
      for i in range(1, int(self.time)):
        copylayer = baselayer.copy()
        self.img.add_layer(copylayer, 0)
        copylayer.name = bname + "_" + str(i)
        copylayer.flush()
    
    #drawing the flakes on top of each layer
    for ll in self.img.layers[::-1]: #this reverses the list
      self.drawflakes(ll, flakes)
      self.moveflakes(flakes)
    
    pdb.gimp_displays_flush()
  
    #asking if the gif should be exported now
    askdi = gtk.Dialog(title="Exporting", parent=self)
    qlabel = gtk.Label("Do I need to export the animated gif now?")
    askdi.vbox.add(qlabel)
    qlabel.show()
    askdi.add_button("No", gtk.RESPONSE_CANCEL)
    askdi.add_button("Yes", gtk.RESPONSE_OK)
    askdi.connect("destroy", gtk.main_quit)
    
    exportnow = askdi.run()
    
    if (exportnow == gtk.RESPONSE_OK):
      #creating the file chooser dialog
      ffilter = gtk.FileFilter()
      ffilter.set_name("Animated Graphic Interface Format (gif)")
      ffilter.add_mime_type("image/gif")
      filechooser = gtk.FileChooserDialog(title="Choose file", parent=askdi, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=None, backend=None)
      filechooser.add_filter(ffilter)
      filechooser.add_button("Cancel", gtk.RESPONSE_CANCEL)
      filechooser.add_button("Save", gtk.RESPONSE_OK)
      
      respfc = filechooser.run()

      #export the animated gif      
      if (respfc == gtk.RESPONSE_OK):
        self.savepath = filechooser.get_filename()
        
        if (self.img.base_type != 2): #converting to indexed image only if is not already an indexed image
          pdb.gimp_image_convert_indexed(self.img, 0, 0, 100, False, False, "ignored")

        pdb.file_gif_save(self.img, self.drawab, self.savepath, self.savepath, 0, 1, 100, 0)

    askdi.destroy()
    pdb.gimp_context_set_foreground(oldfgcol)
    pdb.gimp_context_get_brush(oldbrush)
  
  #method to draw on the drawable the flakes in the flake list
  def drawflakes(self, drw, flakelist):
    pdb.gimp_context_set_brush('2. Hardness 025')
    for flake in flakelist:
      flc = flake.get_coord()
      pdb.gimp_context_set_brush_size(flake.r)
      pdb.gimp_paintbrush_default(drw, len(flc), flc)
    
  #method to move the flakes applying velocity
  def moveflakes(self, flakelist):
    ww = pdb.gimp_image_width(self.img)
    hh = pdb.gimp_image_height(self.img)
    
    maxobs = int((self.obsci / 100.0) * ((ww + hh) / 2.0))
    
    #set velocity
    if (self.direc == 0):
      pxspeed = int((self.speed / 100.0) * hh)
      vx = [random.uniform(-1*maxobs, maxobs) for x in range(self.pn)]
      vy = [pxspeed] * self.pn
    elif (self.direc == 1):
      pxspeed = (self.speed / 100.0) * ww
      vx = [pxspeed] * self.pn
      vy = [random.uniform(-1*maxobs, maxobs) for x in range(self.pn)]
    elif (self.direc == 2):
      pxspeed = (self.speed / 100.0) * hh
      vx = [random.uniform(-1*maxobs, maxobs) for x in range(self.pn)]
      vy = [-1 * pxspeed] * self.pn
    elif (self.direc == 3):
      pxspeed = (self.speed / 100.0) * ww
      vx = [-1 * pxspeed] * self.pn
      vy = [random.uniform(-1*maxobs, maxobs) for x in range(self.pn)]

    #apply velocity
    for flake, i in zip(flakelist, range(self.pn)):
      flake.push_speed(vx[i], vy[i])
      
      #correct flake position if it goes outside image boundaries
      if (self.direc == 0):
        if (flake.y > hh):
          nx = random.uniform(1, ww)
          flake.set_coord(nx, 0)
      elif (self.direc == 1):
        if (flake.x > ww):
          ny = random.uniform(1, hh)
          flake.set_coord(0, ny)
      elif (self.direc == 2):
        if (flake.y < 0):
          nx = random.uniform(1, ww)
          flake.set_coord(nx, hh)
      elif (self.direc == 3):
        if (flake.x < 0):
          nx = random.uniform(1, hh)
          flake.set_coord(ww, nx)


#The function to be registered in GIMP
def make_animation_snowing(img, tdraw):
  ll = MainApp(img, tdraw)
  gtk.main()


#The command to register the function
register(
  "python-fu_make_snowing",
  "python-fu_make_snowing",
  "Create or edit an animation superimposing a snowing effect on an image or an existing animation",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Filters/Animation/Snow",
  "RGB*, GRAY*, INDEXED*",
  [],
  [],
  make_animation_snowing
  )

#The main function to activate the script
main()

