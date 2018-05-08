#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  make_landmap.py
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

#This script generate or edit a regional map, can be used to generate gdr-like maps. It follows a tutorial on http://www.cartographersguild.com/
#IT IS NOT YET COMPLETED
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

#@@@ add some choice on options island (radius) e single coast (direction of the coast and amount of land)

import sys
import os
import math
import random
import gtk
import gobject
from gimpfu import *

FSG = 10


#generic function used to adjust RGB color of a color gobject
def gdkcoltorgb(gdkc):
  red = int(gdkc.red_float * 255)
  green = int(gdkc.green_float * 255)
  blue = int(gdkc.blue_float * 255)
  return (red, green, blue)

#generic function to fill a layer with a color
def colfillayer(image, layer, rgbcolor):
  oldfgcol = pdb.gimp_context_get_foreground()
  pdb.gimp_context_set_foreground(rgbcolor) #set foreground color
  pdb.gimp_edit_bucket_fill(layer, 0, 0, 100, 255, True, pdb.gimp_image_width(image)/2, pdb.gimp_image_height(image)/2) #filling the clip layer with white
  pdb.gimp_context_set_foreground(oldfgcol)


#class to set the maximum color output level of a layer
class CLevDialog(gtk.Dialog):
  #class constants (used as a sort of enumeration)
  GAMMA = 0
  INPUT_MIN = 1
  INPUT_MAX = 2
  OUTPUT_MIN = 3
  OUTPUT_MAX = 4
  ALL = 5

  #constructor
  def __init__(self, image, layer, ltext, modes, *args):
    dwin = gtk.Dialog.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments
    self.modes = modes
    self.img = image
    self.origlayer = layer
    self.reslayer = None
    self.inlow = 0 #threshold  color set to minimum (if used in the three channel (RGB) is black)
    self.inhigh = 255 #threshold  color set to maximum (if used in the three channel (RGB) is white)
    self.gamma = 1.0 #gamma value for input color
    self.outlow = 0 #threshold  color set to minimum (if used in the three channel (RGB) is black)
    self.outhigh = 255 #threshold  color set to maximum (if used in the three channel (RGB) is white)
    
    #Designing the interface
    #new row
    laba = gtk.Label(ltext)
    self.vbox.add(laba)

    labtxt = []
    adjlist = []
    hboxes = []
    labb = []
    scab = []
    spbutc = []
    
    if self.modes[0] == CLevDialog.ALL:
      self.modes = [CLevDialog.GAMMA, CLevDialog.INPUT_MIN, CLevDialog.INPUT_MAX, CLevDialog.OUTPUT_MIN, CLevDialog.OUTPUT_MAX]
    
    #creating the necessary adjustments
    for m in self.modes:
      if (m == CLevDialog.GAMMA):
        adjlist.append(gtk.Adjustment(self.gamma, 0.10, 10.00, 0.01, 0.1))
        labtxt.append("Gamma")
      if (m == CLevDialog.INPUT_MIN):
        adjlist.append(gtk.Adjustment(self.inlow, 0, 255, 1, 10))
        labtxt.append("Low Input")
      if (m == CLevDialog.INPUT_MAX):
        adjlist.append(gtk.Adjustment(self.inhigh, 0, 255, 1, 10))
        labtxt.append("High Input")
      if (m == CLevDialog.OUTPUT_MIN):
        adjlist.append(gtk.Adjustment(self.outlow, 0, 255, 1, 10))
        labtxt.append("Low Output")
      if (m == CLevDialog.OUTPUT_MAX):
        adjlist.append(gtk.Adjustment(self.outhigh, 0, 255, 1, 10))
        labtxt.append("High Output")

    #making the scale and spinbuttons for the adjustments
    for adj, ww, lt in zip(adjlist, self.modes, labtxt):
      #new row
      hboxes.append(gtk.HBox(spacing=10, homogeneous=False))
      self.vbox.add(hboxes[-1])
    
      labb.append(gtk.Label(lt))
      hboxes[-1].add(labb[-1])
      
      scab.append(gtk.HScale(adj))
      scab[-1].connect("value-changed", self.on_value_changed, ww)
      hboxes[-1].add(scab[-1])
      
      spbutc.append(gtk.SpinButton(adj, 0, 2))
      spbutc[-1].connect("output", self.on_value_changed, ww)
      hboxes[-1].add(spbutc[-1])
      
    #action area
    butok = gtk.Button("OK")
    self.action_area.add(butok)
    butok.connect("clicked", self.on_butok_clicked)
    
    self.show_all()
    return dwin

  #callback method, create the cliplayer
  def make_reslayer(self):
    #deleting the reslayer and recreating if it already exists
    if self.reslayer is not None:
      pdb.gimp_image_remove_layer(self.img, self.reslayer)
    
    pdb.gimp_item_set_visible(self.origlayer, True)
    self.reslayer = self.origlayer.copy()
    self.img.add_layer(self.reslayer, 0)
    pdb.gimp_item_set_visible(self.origlayer, False)
    
  #callback method, apply the new value
  def on_value_changed(self, widget, m):
    self.make_reslayer()

    if (m == CLevDialog.GAMMA):
      self.gamma = widget.get_value()
    if (m == CLevDialog.INPUT_MIN):
      self.inlow = widget.get_value()
    if (m == CLevDialog.INPUT_MAX):
      self.inhigh = widget.get_value()
    if (m == CLevDialog.OUTPUT_MIN):
      self.outlow = widget.get_value()
    if (m == CLevDialog.OUTPUT_MAX):
      self.outhigh = widget.get_value()
            
    pdb.gimp_levels(self.reslayer, 0, self.inlow, self.inhigh, self.gamma, self.outlow, self.outhigh) #regulating color levels, channel = #0 (second parameter) is for histogram value
    pdb.gimp_displays_flush()

  #callback method for ok button
  def on_butok_clicked(self, widget):
    rname = self.origlayer.name
    pdb.gimp_image_remove_layer(self.img, self.origlayer)
    self.reslayer.name = rname
    self.hide()


#base class to implement the TSL tecnnique. This class is inherited by the GUI-provided classes.
#it works as a sort of abstract class, but python does not have the concecpt of abstract classes, so it's just a normal class. 
class TLSbase(gtk.Dialog):
  #constructor
  def __init__(self, image, drawable, layermask, channelmask, *args):
    mwin = gtk.Dialog.__init__(self, *args)
    self.set_border_width(10)
    
    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)
    
    #internal arguments
    self.img = image
    self.bgl = drawable
    self.noisel = None
    self.clipl = None
    self.maskl = layermask
    self.channelms = channelmask
    self.thrc = 0 #will be selected later
    
    #nothing in the dialog: labels and buttons are created in the child classes
    
    return mwin
    
  #method to close the dialog at the end
  def on_job_done(self):
    pdb.gimp_displays_flush()
    self.hide()
      
  #method to generate a uniformly colored layer (typically the background layer
  def makeunilayer(self, lname, lcolor=None):
    res = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, lname, 100, 0) #0 = normal mode
    self.img.add_layer(res, 0)
    if lcolor is None:      
      lcolor = (255, 255, 255) #make layer color white
    
    colfillayer(self.img, res, lcolor)
    pdb.gimp_displays_flush()
    return res
  
  #method to generate the uniformly colored background layer
  def makebgl(self, lcolor=None):
    self.bgl = self.makeunilayer("bgl", lcolor)

  #method to generate the noise layer
  def makenoisel(self, lname, pixsize, mode=NORMAL_MODE, turbulent=False):    
    noiselayer = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, lname, 100, mode)
    self.img.add_layer(noiselayer, 0)
    pdb.plug_in_solid_noise(self.img, noiselayer, False, turbulent, random.random() * 9999999999, 15, pixsize, pixsize)
    return noiselayer
  
  #method to generate the clip layer
  def makeclipl(self, lname, commtxt):
    cliplayer = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, lname, 100, 10) #10 = lighten only mode
    self.img.add_layer(cliplayer, 0)
    colfillayer(self.img, cliplayer, (255, 255, 255)) #make layer color white
    
    cld = CLevDialog(self.img, cliplayer, commtxt, [CLevDialog.OUTPUT_MAX], "Set clip layer level", self, gtk.DIALOG_MODAL) #title = "sel clip...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    cld.run()
    cliplayer = cld.reslayer
    self.thrc = cld.outhigh
    cld.destroy()
    return cliplayer

  #method to make the final layer with the profile and save it in a channel.
  #remember: white = land, black = water
  def makeprofilel(self, lname):
    pdb.gimp_context_set_sample_merged(True)
    pdb.gimp_image_select_color(self.img, 2, self.clipl, (int(self.thrc), int(self.thrc), int(self.thrc))) #2 = selection replace
    pdb.gimp_context_set_sample_merged(False)
    pdb.gimp_selection_invert(self.img) #inverting selection
    self.maskl = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, lname, 100, 0) #0 (last) = normal mode
    self.img.add_layer(self.maskl, 0)
    colfillayer(self.img, self.maskl, (255, 255, 255)) #make layer color white
    self.channelms = pdb.gimp_selection_save(self.img)
    pdb.gimp_selection_none(self.img)
    
  #method to apply a channel mask to a layer 
  def addmaskp(self, layer, inverting=False, applying=False):
    if pdb.gimp_layer_get_mask(layer) is None:
      maskmode = 0 #white mask (full transparent)
      if (self.channelms is not None):
        maskmode = 6 #channel mask
        if (pdb.gimp_image_get_active_channel(self.img) is None): #checking if there is already an active channel
          pdb.gimp_image_set_active_channel(self.img, self.channelms) #setting the active channel: if there is no active channel, gimp_layer_create_mask will fail.
      
      mask = pdb.gimp_layer_create_mask(layer, maskmode)
      pdb.gimp_layer_add_mask(layer, mask)

      if (inverting):
        pdb.gimp_invert(mask)
    
    else:
      #mask already present, hence it is removed with the MASK_APPLY option
      applying = True
        
    if (applying):
      pdb.gimp_layer_remove_mask(layer, 0) #0 = MASK_APPLY
      return None
    else:
      return mask
  
  #method to apply a color gradient map to a layer (layer colors are scaled through the gradient)
  def cgradmap(self, layer, darkc, lightc):
    oldfgcol = pdb.gimp_context_get_foreground()
    pdb.gimp_context_set_foreground(darkc) #set foreground color
    oldbgcol = pdb.gimp_context_get_background()
    pdb.gimp_context_set_background(lightc) #set background color
    
    #command to make the gradient map
    pdb.gimp_context_set_gradient('Da pp a sf (RGB)')
    pdb.plug_in_gradmap(self.img, layer)
    
    pdb.gimp_context_set_foreground(oldfgcol)
    pdb.gimp_context_set_background(oldbgcol)


#class to generate random land profile
class LandProfile(TLSbase):
  #constructor
  def __init__(self, image, tdraw, *args):
    mwin = TLSbase.__init__(self, image, tdraw, None, None, *args)
    
    #internal arguments
    self.genonce = False
    self.coastnamelist = ["no water", "archipelago/lakes", "simple coastline", "island", "big lake", "customized"]
    self.coasttypelist = range(len(self.coastnamelist))
    self.coasttype = 0 #will be reinitialized in GUI costruction
    
    #new row
    labb = gtk.Label("In the final result: white represent land and black represent water.")
    self.vbox.add(labb)
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxa)
    
    laba = gtk.Label("Select coastline type")
    hbxa.add(laba)
    
    boxmodela = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(self.coastnamelist, self.coasttypelist):
      irow = boxmodela.append(None, [i, j])

    self.coasttype = self.coasttypelist[0]

    cboxa = gtk.ComboBox(boxmodela)
    rendtexta = gtk.CellRendererText()
    cboxa.pack_start(rendtexta, True)
    cboxa.add_attribute(rendtexta, "text", 0)
    cboxa.set_entry_text_column(0)
    cboxa.set_active(0)
    cboxa.connect("changed", self.on_coasttype_changed)
    hbxa.add(cboxa)
    
    #new row
    labtext = "To generate a more elaborate profile, draw a gradient with the shape you wish\n"
    labtext += "and select the customized option in the dropdown menu.\n"
    labtext += "Press again Generate land profile if you want to regenerate the profile.\n"
    labtext += "Press Next step to continue." 
    labc = gtk.Label(labtext)
    self.vbox.add(labc)
    
    #button area
    butgenpr = gtk.Button("Generate land profile")
    self.action_area.add(butgenpr)
    butgenpr.connect("clicked", self.on_butgenpr_clicked)
    
    butnext = gtk.Button("Next step")
    self.action_area.add(butnext)
    butnext.connect("clicked", self.on_butnext_clicked)
    
    self.show_all()
    return mwin
  
  #callback method, setting the coast type to the one in the combobox
  def on_coasttype_changed(self, widget):
    refmode = widget.get_model()
    self.coasttype = refmode.get_value(widget.get_active_iter(), 1)
  
  #callback method, regenerate the land profile
  def on_butnext_clicked(self, widget):
    if not self.genonce:
      if (self.coasttype == 0):
        self.on_job_done()
      else:
        #dialog telling to press the other button first
        infodi = gtk.Dialog(title="Warning", parent=self)
        ilabel = gtk.Label("You cannot go to the next step until you generate a land profile.\nPress the \"Generate land profile\" button first.")
        infodi.vbox.add(ilabel)
        ilabel.show()
        infodi.add_button("Ok", gtk.RESPONSE_OK)
        infodi.run()
        infodi.destroy()
        
    else:
      self.on_job_done()
    
  
  #callback method, generate the profile
  def on_butgenpr_clicked(self, widget):
    #removing previous layers if we are regenerating
    if (self.genonce):
      if self.bgl is not None:
        pdb.gimp_image_remove_layer(self.img, self.bgl)
        self.bgl = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, "Sfondo", 100, 0) #0 = normal mode
        self.img.add_layer(self.bgl, 0)
        colfillayer(self.img, self.bgl, (255, 255, 255)) #make layer full white
      if self.noisel is not None:
        pdb.gimp_image_remove_layer(self.img, self.noisel)
      if self.clipl is not None:
        pdb.gimp_image_remove_layer(self.img, self.clipl)
      if self.maskl is not None:
        pdb.gimp_image_remove_layer(self.img, self.maskl)
      if self.channelms is not None:
        pdb.gimp_image_remove_channel(self.img, self.channelms)
      
    #Using the TSL tecnnique: shape layer
    if (self.coasttype == 0): #no need of a coast, skip everything
      self.genonce = True
    else:
      if (self.coasttype == 1): #to generate archipelago
        #setting the layer to a light gray color
        colfillayer(self.img, self.bgl, (128, 128, 128)) #rgb notation for a 50% gray
      elif (self.coasttype > 1 and self.coasttype < 5):
        if (self.coasttype == 2): #to generate a coastline
          gradtype = 0 #linear
          x1 = random.random() * (pdb.gimp_image_width(self.img) / FSG)
          y1 = random.random() * (pdb.gimp_image_height(self.img) / FSG)
          x2 = pdb.gimp_image_width(self.img) - (random.random() * (pdb.gimp_image_width(self.img) / FSG))
          y2 = pdb.gimp_image_height(self.img) - (random.random() * (pdb.gimp_image_height(self.img) / FSG))
        elif (self.coasttype == 3 or self.coasttype == 4): #to generate a circular island or lake
          gradtype = 2 #radial
          x1 = pdb.gimp_image_width(self.img)/2
          y1 = pdb.gimp_image_height(self.img)/2
          aver = (x1 + y1)/2.0
          x2 = aver + (aver * (0.75 + random.random()/2.0))
          y2 = y1
        
        #drawing the gradients
        pdb.gimp_edit_blend(self.bgl, 0, 0, gradtype, 100, 0, 0, False, False, 1, 0, True, x1, y1, x2, y2) #0 (first) = normal mode, 0 (second) linear gradient
        if (self.coasttype == 3): #inverting the gradient
          pdb.gimp_invert(self.bgl)
        
      elif (self.coasttype == 5):
        pass
      
      #making the other steps
      self.noisel = self.makenoisel("noiselayer", 5, OVERLAY_MODE)
      cmm = "The lower the selected value, the more the resulting land."
      self.clipl = self.makeclipl("cliplayer", cmm)
      self.makeprofilel("landlayer")
      self.genonce = True
      
      pdb.gimp_displays_flush()


#class to generate the water mass profile (sea, ocean, lakes)
class WaterProfile(TLSbase):
  #constructor
  def __init__(self, image, tdraw, layermask, channelmask, *args):
    mwin = TLSbase.__init__(self, image, tdraw, layermask, channelmask, *args)
    self.seal = None
    self.shorel = None

    #internal parameters
    self.smoothnamelist = ["none", "small", "medium", "large"]
    self.smoothtypelist = [0, 20, 40, 60] #is a percentage
    self.smooth = 0 #will be reinitialized in GUI costruction
    self.addshore = True
    
    self.colorwaterdeep = (37, 50, 95) #a deep blue color
    self.colorwaterlight = (241, 244, 253) #a very light blue color almost white
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxa)
    
    laba = gtk.Label("Smoothing parameter for water deepness")
    hbxa.add(laba)
    
    boxmodela = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    #filling the model for the combobox
    for i, j in zip(self.smoothnamelist, self.smoothtypelist):
      irow = boxmodela.append(None, [i, j])

    self.smooth = self.smoothtypelist[1]

    cboxa = gtk.ComboBox(boxmodela)
    rendtexta = gtk.CellRendererText()
    cboxa.pack_start(rendtexta, True)
    cboxa.add_attribute(rendtexta, "text", 0)
    cboxa.set_entry_text_column(0)
    cboxa.set_active(1)
    cboxa.connect("changed", self.on_smooth_type_changed)
    hbxa.add(cboxa)
    
    #new row
    hbxb = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxb)
    
    chbb = gtk.CheckButton("Add shore effect")
    chbb.set_active(self.addshore)
    chbb.connect("toggled", self.on_chb_toggled)
    hbxb.add(chbb)

    #button area
    butcanc = gtk.Button("Cancel")
    self.action_area.add(butcanc)
    butcanc.connect("clicked", gtk.main_quit)
    
    butgenpr = gtk.Button("Generate water profile")
    self.action_area.add(butgenpr)
    butgenpr.connect("clicked", self.on_butgenpr_clicked)

    self.show_all()
    return mwin
    
  #callback method, setting smooth parameter
  def on_smooth_type_changed(self, widget):
    refmode = widget.get_model()
    self.smooth = refmode.get_value(widget.get_active_iter(), 1)
  
  #callback method, setting shore parameter
  def on_chb_toggled(self, widget):
    self.addshore = widget.get_active()
  
  #callback method, generate water profile
  def on_butgenpr_clicked(self, widget):
    if (self.smooth > 0):
      pix = (self.smooth / 100.0) * ((self.img.width + self.img.height) / 2.0)
      pdb.plug_in_gauss(self.img, self.bgl, pix, pix, 0)
      pdb.gimp_displays_flush()
    
    self.noisel = self.makenoisel("seanoise", 4, OVERLAY_MODE)
    self.bgl = pdb.gimp_image_merge_down(self.img, self.noisel, 0)

    #copy noise layer into a new layer 
    self.seal = self.bgl.copy()
    self.seal.name = "sea"
    self.img.add_layer(self.seal, 0)
    
    self.addmaskp(self.seal, True, True)
    pdb.plug_in_normalize(self.img, self.seal)
    pdb.gimp_image_select_item(self.img, 2, self.seal) #this selects the transparent region of the layer, #2 = replace selection
    pdb.gimp_selection_invert(self.img) #inverting the selection
    colfillayer(self.img, self.seal, (255, 255, 255)) #filling selected area with white
    pdb.gimp_selection_none(self.img)

    #smoothing near the coast and apply color
    pdb.plug_in_gauss(self.img, self.seal, 20, 20, 0)
    self.cgradmap(self.seal, self.colorwaterdeep, self.colorwaterlight)
    
    #adding shore
    if (self.addshore):
      self.shorel = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, "seashore", 100, 0) #0 (last) = normal mode
      self.img.add_layer(self.shorel, 0)
      colfillayer(self.img, self.shorel, self.colorwaterlight)
      maskshore = self.addmaskp(self.shorel, False, False)
      pxpar = 0.01 * (self.img.width + self.img.height)/2.0
      if (pxpar < 5):
        pxpar = 5.0
      
      pdb.plug_in_gauss(self.img, maskshore, pxpar, pxpar, 0)
    
    self.on_job_done()


#class to generate the base land (color and mask of the terrain)
class BaseDetails(TLSbase):
  #constructor
  def __init__(self, image, tdraw, layermask, channelmask, *args):
    mwin = TLSbase.__init__(self, image, tdraw, layermask, channelmask, *args)
    self.bumpmapl = None
    self.basebumpsl = None
    
    #internal parameters
    #@@@ ideally all of these: grassland, desert, arctic, underdark || these should be smaller regions rendered in other ways: forest, mountain, swamp, coast 
    self.regionlist = ["grassland", "desert", "arctic"]
    self.regiontype = ["grass", "sand", "ice"]
    self.region = self.regiontype[0] #will be reinitialized in GUI costruction

    #~ self.desertlist = ["no", "manually", "randomly"]
    #~ self.deserttype = range(len(self.desertlist))
    #~ self.desertdo = 0 #will be reinitialized in GUI costruction
    
    #color couples to generate gradients
    self.colorgrassdeep = (76, 83, 41) #a dark green color, known as ditch
    self.colorgrasslight = (149, 149, 89) #a light green color, known as high grass
    self.colordesertdeep = (150, 113, 23) #a relatively dark brown, known as sand dune
    self.colordesertlight = (244, 164, 96) #a light brown almost yellow, known as sandy brown
    self.colorarcticdeep = (128, 236, 217) #a clear blue
    self.colorarcticlight = (232, 232, 232) #a dirty white
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxa)
    
    laba = gtk.Label("Select type of region")
    hbxa.add(laba)
    
    boxmodela = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
    #filling the model for the combobox
    for i, j in zip(self.regionlist, self.regiontype):
      irow = boxmodela.append(None, [i, j])

    self.region = self.regiontype[0]

    cboxa = gtk.ComboBox(boxmodela)
    rendtexta = gtk.CellRendererText()
    cboxa.pack_start(rendtexta, True)
    cboxa.add_attribute(rendtexta, "text", 0)
    cboxa.set_entry_text_column(0)
    cboxa.set_active(0)
    cboxa.connect("changed", self.on_region_changed)
    hbxa.add(cboxa)
    
    #button area
    butcanc = gtk.Button("Cancel")
    self.action_area.add(butcanc)
    butcanc.connect("clicked", gtk.main_quit)
    
    butgenpr = gtk.Button("Generate land details")
    self.action_area.add(butgenpr)
    butgenpr.connect("clicked", self.on_butgendet_clicked)

    self.show_all()
    return mwin
    
  #callback method, setting base region parameter 
  def on_region_changed(self, widget):
    refmode = widget.get_model()
    self.region = refmode.get_value(widget.get_active_iter(), 1)
    
  #callback method, generate land details
  def on_butgendet_clicked(self, widget):
    #base color for grass
    self.addmaskp(self.bgl)
    self.bgl.name = self.region    
    if (self.bgl.name == "grass"):
      self.cgradmap(self.bgl, self.colorgrassdeep, self.colorgrasslight)
    elif (self.bgl.name == "sand"):
      self.cgradmap(self.bgl, self.colordesertdeep, self.colordesertlight)
    elif (self.bgl.name == "ice"):
      self.cgradmap(self.bgl, self.colorarcticdeep, self.colorarcticlight)
      
    self.noisel = self.makenoisel(self.bgl.name + "texture", 3, OVERLAY_MODE)
    self.addmaskp(self.noisel)
    
    #create an embossing effect using a bump map
    self.bumpmapl = self.makenoisel(self.bgl.name + "bumpmap", 15, NORMAL_MODE, True)
    pdb.gimp_item_set_visible(self.bumpmapl, False)
    self.basebumpsl = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, self.bgl.name + "bumps", 100, OVERLAY_MODE)
    self.img.add_layer(self.basebumpsl, 0)
    colfillayer(self.img, self.basebumpsl, (128, 128, 128)) #make layer 50% gray

    pdb.plug_in_bump_map_tiled(self.img, self.basebumpsl, self.bumpmapl, 120, 45, 3, 0, 0, 0, 0, True, False, 2) #2 = sinusoidal
    self.addmaskp(self.basebumpsl)
    
    self.on_job_done()


#class to generate the dirt on the terrain
class DirtDetails(TLSbase):
  #constructor
  def __init__(self, image, tdraw, layermask, channelmask, *args):
    mwin = TLSbase.__init__(self, image, tdraw, layermask, channelmask, *args)
    self.bumpmapl = None
    self.basebumpsl = None
    self.smp = 50
    
    #colors
    self.colordirt = (128, 107, 80) #med dirt, a moderate brown

    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxa)
    
    laba = gtk.Label("Adding dirt to the map?")
    hbxa.add(laba)
    
    #button area
    butcanc = gtk.Button("No")
    self.action_area.add(butcanc)
    butcanc.connect("clicked", self.on_butcanc_clicked)
    
    butgendrt = gtk.Button("Yes")
    self.action_area.add(butgendrt)
    butgendrt.connect("clicked", self.on_butgendrt_clicked)

    self.show_all()
    return mwin

  #method to make the more complex noise for dirt: should be combined with the land profile to have dirt close to the coast if a coast is present
  def makedirtnoisel(self, lname, pixsize):
    #preparing the noiselayer generation
    if self.maskl is not None:
      masklcopy = self.maskl.copy()
      self.img.add_layer(masklcopy, 0)
      pdb.plug_in_gauss(self.img, masklcopy, self.smp, self.smp, 0)
    
      #adding the noise layer mixed with the copy mask
      self.noisel = self.makenoisel(lname, pixsize, DIFFERENCE_MODE)
      self.noisel = pdb.gimp_image_merge_down(self.img, self.noisel, 0)
      pdb.gimp_invert(self.noisel)
      
    else:
      #just generating a normal noise layer
      self.noisel = self.makenoisel(lname, pixsize, NORMAL_MODE)
      
    self.noisel.name = "dirtnoisemask"


    #correcting the mask color levels
    commtxt = "Set minimum, maximum and gamma to edit the B/W ratio in the image.\n"
    commtxt += "The white regions will be covered by dirt."
    cld = CLevDialog(self.img, self.noisel, commtxt, [CLevDialog.INPUT_MIN, CLevDialog.GAMMA, CLevDialog.INPUT_MAX], "Set input levels", self, gtk.DIALOG_MODAL)
    cld.run()
    resl = cld.reslayer
    cld.destroy()
    return resl

  #callback method, skipping the dirt adding
  def on_butcanc_clicked(self, widget):
    self.on_job_done()

  #callback method, generate the layers to create the dirt
  def on_butgendrt_clicked(self, widget):
    self.makebgl(self.colordirt)
    self.bgl.name = "dirt"
    
    #adding some effect to the layer to make it like dirt
    pdb.plug_in_hsv_noise(self.img, self.bgl, 4, 11, 10, 22)
    pdb.plug_in_bump_map_tiled(self.img, self.bgl, self.bgl, 120, 45, 3, 0, 0, 0, 0, True, False, 2) #2 = sinusoidal
    
    oknoise = True
    while oknoise:
      self.noisel = self.makedirtnoisel("dirtnoise", 16)
      
      #dialog checking that the user is satisfied with the result
      infodi = gtk.Dialog(title="Checking dialod", parent=self)
      ilabel = gtk.Label("Press OK if you are satisfied with the current mask.\nPress Cancel to generate a new mask for the dirt.")
      infodi.vbox.add(ilabel)
      ilabel.show()
      infodi.add_button("Cancel", gtk.RESPONSE_CANCEL)
      infodi.add_button("OK", gtk.RESPONSE_OK)
      useransw = infodi.run()
      
      if (useransw == gtk.RESPONSE_OK):
        oknoise = False
      elif (useransw == gtk.RESPONSE_CANCEL):
        pdb.gimp_image_remove_layer(self.img, self.noisel)

      infodi.destroy()
    
    #applying some masks
    self.addmaskp(self.bgl, False, True)
    maskbis = self.addmaskp(self.bgl, False, False) #readding but not applying, we need to work on the second mask

    noisemask = self.addmaskp(self.noisel)
    pdb.plug_in_gauss(self.img, self.noisel, 10, 10, 0)
    pdb.plug_in_spread(self.img, self.noisel, 10, 10)    
    self.addmaskp(self.noisel) #here called again to apply the mask
    
    #applying the mask, final step
    if self.maskl is not None:
      masklcopy = self.maskl.copy()
      self.img.add_layer(masklcopy, 1)      
      self.noisel = pdb.gimp_image_merge_down(self.img, self.noisel, 0)

    pdb.gimp_edit_copy(self.noisel)
    flsel = pdb.gimp_edit_paste(maskbis, False)
    pdb.gimp_floating_sel_anchor(flsel)

    pdb.gimp_item_set_visible(self.noisel, False)
    pdb.gimp_layer_set_opacity(self.bgl, 55)
    
    self.on_job_done()

  

#class for the customized GUI
class MainApp(gtk.Window):
  #constructor
  def __init__(self, image, drawab, *args):
    mwin = gtk.Window.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments
    self.img = image
    self.drawab = drawab
    
    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)
    
    #Designing the interface
    vbx = gtk.VBox(spacing=10, homogeneous=True)
    self.add(vbx)
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    vbx.add(hbxa)
    
    butgenmap = gtk.Button("Generate map randomly")
    hbxa.add(butgenmap)
    butgenmap.connect("clicked", self.on_butgenmap_clicked)

    butusemap = gtk.Button("Use current image as base map")
    hbxa.add(butusemap)
    butusemap.connect("clicked", self.on_butusemap_clicked)

    self.show_all()
    return mwin
    
  #callback method to generate the map randomly
  def on_butgenmap_clicked(self, widget):
    pdb.gimp_context_set_foreground((0, 0, 0)) #set foreground color to black
    pdb.gimp_context_set_background((255, 255, 255)) #set background to white
    
    land = LandProfile(self.img, self.drawab, "Building land mass", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    land.run()
    layermask = land.maskl
    channelmask = land.channelms
        
    landbg = self.drawab
    if (land.coasttype > 0):
      #create a copy of the landmass to use as base layer for the watermass
      waterbg = land.maskl.copy()
      waterbg.name = "seashape"
      self.img.add_layer(waterbg, 0)
      
      water = WaterProfile(self.img, waterbg, layermask, channelmask, "Building water mass", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
      water.run()

      #create a copy of the landmass to use as base layer for the landmass decoration      
      landbg = water.bgl.copy()
      self.img.add_layer(landbg, 0)

    landbg.name = "base"
    landdet = BaseDetails(self.img, landbg, layermask, channelmask, "Building land details", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    landdet.run()
    
    dirtd = DirtDetails(self.img, None, layermask, channelmask, "Building dirt", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    dirtd.run()
    
  #callback method to use current image as map
  def on_butusemap_clicked(self, widget):
    pass


#The function to be registered in GIMP
def python_make_landmap(img, tdraw):
  mapp = MainApp(img, tdraw)
  gtk.main()


#The command to register the function
register(
  "python-fu_make_landmap",
  "python-fu_make_landmap",
  "Generate or edit a regional map. Start from an image with a single layer with white background: pop up dialogs appear to guide the user in the process.",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Tools/LandMap",
  "RGB*, GRAY*, INDEXED*",
  [],
  [],
  python_make_landmap
  )

#The main function to activate the script
main()
