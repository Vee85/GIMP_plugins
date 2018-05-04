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
class ClipDialog(gtk.Dialog):
  #constructor
  def __init__(self, image, ltext, namelayer, *args):
    dwin = gtk.Dialog.__init__(self, *args)
    self.set_border_width(10)
    self.img = image
    self.cliplayer = None
    self.lname = namelayer
    self.thrcol = 255 #threshold color set to maximum (if used in the three channel (RGB) is white)
    self.closed = False
    
    self.make_cliplayer()
    pdb.gimp_displays_flush()

    #Designing the interface
    #new row
    laba = gtk.Label(ltext)
    self.vbox.add(laba)
    
    genadj = gtk.Adjustment(self.thrcol, 0, 255, 1, 10)
    #new row
    scab = gtk.HScale(genadj)
    scab.connect("value-changed", self.on_value_changed)
    self.vbox.add(scab)
    
    #new row
    spbutc = gtk.SpinButton(genadj, 0, 0)
    spbutc.connect("output", self.on_value_changed)
    self.vbox.add(spbutc)
    
    #new row
    butok = gtk.Button("OK")
    self.action_area.add(butok)
    butok.connect("clicked", self.on_butok_clicked)
    
    self.show_all()
    return dwin

  #callback method, create the cliplayer
  def make_cliplayer(self):
    self.cliplayer = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, self.lname, 100, 10) #10 = lighten only mode
    self.img.add_layer(self.cliplayer, 0)
    colfillayer(self.img, self.cliplayer, (255, 255, 255)) #make foreground color white
    
  #callback method, apply the new value
  def on_value_changed(self, widget):
    #deleting the layer and recreating
    pdb.gimp_image_remove_layer(self.img, self.cliplayer)
    self.make_cliplayer()
    self.thrcol = int(widget.get_value())
    pdb.gimp_levels(self.cliplayer, 0, 0, 255, 1, 0, self.thrcol) #regulating color levels, channel = #0 (second parameter) is for histogram value
    pdb.gimp_displays_flush()

  #callback method for ok button
  def on_butok_clicked(self, widget):
    self.closed = True
    self.hide()


#base class to implement the TSL tecnnique. This class is inherited by the GUI-provided classes.
#it works as a sort of abstract class, but python does not have the concecpt of abstract classes, so it's just a normal class. 
class TLSbase(gtk.Dialog):
  #constructor
  def __init__(self, image, drawable, *args):
    mwin = gtk.Dialog.__init__(self, *args)
    self.set_border_width(10)
    
    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)
    
    #internal arguments
    self.img = image
    self.bgl = drawable
    self.noisel = None
    self.clipl = None
    self.maskl = None
    self.channelms = None
    self.thrc = 0 #will be selected later
    
    #nothing in the dialog: labels and buttons are created in the child classes
    
    return mwin
    
  #method to close the dialog at the end
  def on_job_done(self):
    pdb.gimp_displays_flush()
    self.hide()
  
  #method to generate the noise layer
  def makenoisel(self, lname, pixsize, overlay=True, turbulent=False):
    mode = 0 #normal mode
    if (overlay):
      mode = 5  #overlay mode
    
    noiselayer = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, lname, 100, mode)
    self.img.add_layer(noiselayer, 0)
    pdb.plug_in_solid_noise(self.img, noiselayer, False, turbulent, random.random() * 9999999999, 15, pixsize, pixsize)
    return noiselayer
  
  #method to generate the clip layer
  def makeclipl(self, lname, commtxt):
    cld = ClipDialog(self.img, commtxt, lname, "Set clip layer level", self, gtk.DIALOG_MODAL) #title = "max output", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    cld.run()
    cliplayer = cld.cliplayer
    self.thrc = cld.thrcol
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
    colfillayer(self.img, self.maskl, (255, 255, 255)) #make foreground color white
    self.channelms = pdb.gimp_selection_save(self.img)
    pdb.gimp_selection_none(self.img)
    
  #method to apply a channel mask to a layer 
  def addmaskp(self, layer, inverting=False, applying=False):
    maskmode = 0 #white mask (full transparent)
    if (self.channelms is not None):
      maskmode = 6 #channel mask
      pdb.gimp_image_set_active_channel(self.img, self.channelms) #setting the active channel: if there is no active channel, gimp_layer_create_mask will fail.
    
    mask = pdb.gimp_layer_create_mask(layer, maskmode)
    pdb.gimp_layer_add_mask(layer, mask)

    if (inverting):
      pdb.gimp_invert(mask)
      
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
    mwin = TLSbase.__init__(self, image, tdraw, *args)
    self.set_border_width(10)
    
    #internal arguments
    self.coastnamelist = ["no coastline", "archipelago/lakes", "simple coastline", "island", "big lake", "customized"]
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
    labc = gtk.Label("To generate a more elaborate profile, draw a gradient with the shape you wish\nand select the customized option in the dropdown menu.")
    self.vbox.add(labc)
    
    #button area
    butcanc = gtk.Button("Cancel")
    self.action_area.add(butcanc)
    butcanc.connect("clicked", gtk.main_quit)
    
    butgenpr = gtk.Button("Generate land profile")
    self.action_area.add(butgenpr)
    butgenpr.connect("clicked", self.on_butgenpr_clicked)
    
    self.show_all()
    return mwin
  
  #callback method, setting the coast type to the one in the combobox
  def on_coasttype_changed(self, widget):
    refmode = widget.get_model()
    self.coasttype = refmode.get_value(widget.get_active_iter(), 1)
  
  #callback method, generate the profile
  def on_butgenpr_clicked(self, widget):
    #Using the TSL tecnnique: shape layer
    if (self.coasttype == 0):
      pass
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
      self.noisel = self.makenoisel("noiselayer", 5)
      cmm = "The lower the selected value, the more the resulting land."
      self.clipl = self.makeclipl("cliplayer", cmm)
      self.makeprofilel("landlayer")
    
    self.on_job_done()


#class to generate the water mass profile (sea, ocean, lakes)
class WaterProfile(TLSbase):
  #constructor
  def __init__(self, image, tdraw, channelmask, *args):
    mwin = TLSbase.__init__(self, image, tdraw, *args)
    self.set_border_width(10)
    self.channelms = channelmask
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
    
    self.noisel = self.makenoisel("seanoise", 4)
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


#class to generate the land details (grass and so on)
class LandDetails(TLSbase):
  #constructor
  def __init__(self, image, tdraw, channelmask, *args):
    mwin = TLSbase.__init__(self, image, tdraw, *args)
    self.set_border_width(10)
    self.channelms = channelmask
    self.bumpmapl = None
    self.grassbumpsl = None
    
    #internal parameters
    #@@@ ideally all of these: grassland, desert, arctic, underdark || these should be smaller regions rendered in other ways: forest, mountain, swamp, coast 
    self.regionlist = ["grassland", "desert", "arctic"]
    self.regiontype = range(len(self.regionlist))
    self.region = 0 #will be reinitialized in GUI costruction

    #~ self.desertlist = ["no", "manually", "randomly"]
    #~ self.deserttype = range(len(self.desertlist))
    #~ self.desertdo = 0 #will be reinitialized in GUI costruction
    
    #color couples to generate gradients
    self.colorgrassdeep = (76, 83, 41) #a dark green color, known as ditch
    self.colorgrasslight = (149, 149, 89) #a light green color, known as high grass
    self.colordesertdeep = (150, 113, 23) #a relatively dark brown, known as sand dune
    self.colordesertlight = (244, 164, 96) #a light brown almost yellow, known as sandy brown
    self.colorarcticdeep = (128, 236, 217) #a clear blue
    self.colorarcticlight = (196, 223, 225) #a light blue
    
    #new row
    hbxa = gtk.HBox(spacing=10, homogeneous=True)
    self.vbox.add(hbxa)
    
    laba = gtk.Label("Select type of region")
    hbxa.add(laba)
    
    boxmodela = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
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
    if (self.region == 0):
      self.cgradmap(self.bgl, self.colorgrassdeep, self.colorgrasslight)
    elif (self.region == 1):
      self.cgradmap(self.bgl, self.colordesertdeep, self.colordesertlight)
    elif (self.region == 2):
      self.cgradmap(self.bgl, self.colorarcticdeep, self.colorarcticlight)
      
    self.noisel = self.makenoisel("grasstexture", 3)
    self.addmaskp(self.noisel)
    
    #create an embossing effect using a bump map
    self.bumpmapl = self.makenoisel("grassbumpmap", 15, False, True)
    pdb.gimp_item_set_visible(self.bumpmapl, False)
    self.grassbumpsl = pdb.gimp_layer_new(self.img, self.img.width, self.img.height, 0, "grassbumps", 100, 5) #5 = overlay mode
    self.img.add_layer(self.grassbumpsl, 0)
    colfillayer(self.img, self.grassbumpsl, (128, 128, 128)) #make foreground 50% gray

    pdb.plug_in_bump_map_tiled(self.img, self.grassbumpsl, self.bumpmapl, 120, 45, 3, 0, 0, 0, 0, True, False, 2) #2 = sinusoidal
    self.addmaskp(self.grassbumpsl)
        
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
    channelmask = land.channelms
    
    landbg = self.drawab
    #create a copy of the landmass to use as base layer for the watermass
    if (land.coasttype > 0):
      waterbg = land.maskl.copy()
      waterbg.name = "seashape"
      self.img.add_layer(waterbg, 0)
      
      water = WaterProfile(self.img, waterbg, channelmask, "Building water mass", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
      water.run()

      #create a copy of the landmass to use as base layer for the landmass decoration      
      landbg = water.bgl.copy()
      self.img.add_layer(landbg, 0)

    landbg.name = "grass"    
    landdet = LandDetails(self.img, landbg, channelmask, "Building land details", self, gtk.DIALOG_MODAL) #title = "building...", parent = self, flag = gtk.DIALOG_MODAL, they as passed as *args
    landdet.run()
    
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
