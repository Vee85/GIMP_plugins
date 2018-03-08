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

#This script creates an animation using the motion blur filter, starting from a base image and animating a blurring linear effect
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

import sys
import os
import gtk
import gobject
from gimpfu import *

BLURSTEPS = 10
BLURDIR = ["left", "top-left", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left"]
DEFBLURDIR = 0
FRAMETIME = 100
BIDIRBLUR = False

#Class for the customized secondary dialog interface (using gtk as GUI)
class AskDialog(gtk.Dialog):
  #constructor
  def __init__(self, *args):
    mwin = gtk.Dialog.__init__(self, *args)
    self.set_border_width(10)
    
    #Internal arguments
    self.answer = False
    
    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)

    #Designing the interface    
    qlabel = gtk.Label("Do I need to export the animated gif now?")
    self.vbox.add(qlabel)
    
    butno = gtk.Button("No")
    self.action_area.add(butno)
    butno.connect("clicked", self.on_button_clicked, False)
    
    butyes = gtk.Button("Yes")
    self.action_area.add(butyes)
    butyes.connect("clicked", self.on_button_clicked, True)
    
    self.show_all()
    return mwin
  
  #callback method for the buttons
  def on_button_clicked(self, widget, answ):
    self.answer = answ
    self.hide()
    

#Class for the customized main panel interface (using gtk as GUI)
class MainWin(gtk.Window):
  #constructor
  def __init__(self, image, layer, *args):
    mwin = gtk.Window.__init__(self, *args)
    self.set_border_width(10)
    
    #internal arguments
    self.img = image
    self.layer = layer
    self.numblursteps = BLURSTEPS
    self.blurdir = 0 #will be reinitialized in GUI construction
    self.savepath = os.getcwd() #will be updated by user choice
    self.frametime = FRAMETIME
    self.bidblur = BIDIRBLUR

    #Obey the window manager quit signal:
    self.connect("destroy", gtk.main_quit)

    #Designing the interface
    vbx = gtk.VBox(spacing=10, homogeneous=False)
    self.add(vbx)

    hbxini = gtk.HBox(spacing=10, homogeneous=False)
    vbx.add(hbxini)
    topmess = "You should have maximum two layers. The first one will be animated.\n"
    topmess += "If there is a second one, will be the unanimated background.\n"
    topmess += "In this case, be sure that the first one has some transparency."
    labini = gtk.Label(topmess)
    hbxini.add(labini)
    
    hbxa = gtk.HBox(spacing=10, homogeneous=False)
    vbx.add(hbxa)
    
    laba = gtk.Label("Blurring steps")
    hbxa.add(laba)
    
    butaadj = gtk.Adjustment(BLURSTEPS, 2, 10, 1, 5)
    spbuta = gtk.SpinButton(butaadj, 0, 0)
    spbuta.connect("output", self.on_blurstep_change)
    hbxa.add(spbuta)
    
    hbxc = gtk.HBox(spacing=10, homogeneous=False)
    vbx.add(hbxc)
    
    labc = gtk.Label("Delay between frames")
    hbxc.add(labc)
    
    butcadj = gtk.Adjustment(FRAMETIME, 50, 2000, 1, 20)
    spbutc = gtk.SpinButton(butcadj, 0, 0)
    spbutc.connect("output", self.on_frametime_change)
    hbxc.add(spbutc)
    
    hbxb = gtk.HBox(spacing=10, homogeneous=False)
    vbx.add(hbxb)
    
    labb = gtk.Label("Blur direction")
    hbxb.add(labb)
    
    boxmodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    
    #filling the model for the combobox
    for i, j in zip(BLURDIR, range(len(BLURDIR))):
      irow = boxmodel.append(None, [i, j])
      if (j == DEFBLURDIR):
        self.blurdir = j

    cbox = gtk.ComboBox(boxmodel)
    rendtext = gtk.CellRendererText()
    cbox.pack_start(rendtext, True)
    cbox.add_attribute(rendtext, "text", 0)
    cbox.set_entry_text_column(0)
    cbox.set_active(self.blurdir)
    cbox.connect("changed", self.on_cbox_changed)
    hbxb.add(cbox)
    
    butch = gtk.CheckButton("Bidirectional blurring")
    vbx.add(butch)
    butch.set_active(BIDIRBLUR)
    butch.connect("toggled", self.on_butch_toggled)
    
    butok = gtk.Button("OK")
    vbx.add(butok)
    butok.connect("clicked", self.on_butok_clicked)

    self.show_all()

    return mwin
    
  #callback method, setting the step number value to the one in the spinbutton
  def on_blurstep_change(self, widget):
    self.numblursteps = widget.get_value()
    
  #callback method, setting the delay between frames value to the one in the spinbutton
  def on_frametime_change(self, widget):
    self.frametime = widget.get_value()
    
  #callback method, setting the blurring direction value to the one in the combobox
  def on_cbox_changed(self, widget):
    refmode = widget.get_model()
    self.blurdir = refmode.get_value(widget.get_active_iter(), 1)
    
  #callback method, setting the boolean value if bidirectional blurring to the one in the checkbutton
  def on_butch_toggled(self, widget):
    self.bidblur = widget.get_active()
    
  #callback method, do the blurring and optionally export the gif
  def on_butok_clicked(self, widget):
    if (len(self.img.layers) > 2):
      txtmess = "The BlurMotion animation need maximut two source layers.\nIf two layers are provided, the first one will be animated.\n"
      txtmess += "Be sure it has an alpha channel. The second one will be the unanimated background."
      pdb.gimp_message(txtmess)

    else:
      #defining blurring parameters
      blrang = self.blurdir * 45
      
      refblurlayer = self.img.layers[0]
      mergbg = False
      if (len(self.img.layers) == 2):
        refbglayer = self.img.layers[1]
        mergbg = True
      
      #creating the layers with different blurring
      for i in range(1, int(self.numblursteps)):
        blurlayer = refblurlayer.copy()
        self.img.add_layer(blurlayer, 0)
        pdb.plug_in_mblur(self.img, blurlayer, 0, 5*i, blrang, 0, 0)
        
        #performing bidirectional blurring
        if (self.bidblur):
          bilayer = refblurlayer.copy()
          self.img.add_layer(bilayer, 0)
          pdb.plug_in_mblur(self.img, bilayer, 0, 5*i, (blrang + 180), 0, 0)
          blurlayer = pdb.gimp_image_merge_down(self.img, bilayer, 0)

        #merging with background image if present
        if (mergbg):
          bglayer = refbglayer.copy()
          self.img.add_layer(bglayer, 1)
          blurlayer = pdb.gimp_image_merge_down(self.img, blurlayer, 0)
          
        blurlayer.name = refblurlayer.name + "_" + str(i)
        blurlayer.flush()
      
      #merging the original layers if needed
      if (mergbg):
        lastlayer = pdb.gimp_image_merge_down(self.img, refblurlayer, 0)
        lastlayer.flush()
      
      pdb.gimp_displays_flush()
      dial = AskDialog("Exporting", self, gtk.DIALOG_MODAL)
      dial.run()
      
      #asking if the gif should be exported now
      if (dial.answer):
        #creating the file chooser dialog
        ffilter = gtk.FileFilter()
        ffilter.set_name("Animated Graphic Interface Format (gif)")
        ffilter.add_mime_type("image/gif")
        filechooser = gtk.FileChooserDialog(title="Choose file", parent=self, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=None, backend=None)
        filechooser.add_filter(ffilter)
        filechooser.add_button("Cancel", gtk.RESPONSE_CANCEL)
        filechooser.add_button("Save", gtk.RESPONSE_OK)
        
        respfc = filechooser.run()

        #export the animated gif      
        if (respfc == gtk.RESPONSE_OK):
          self.savepath = filechooser.get_filename()        
          pdb.gimp_image_convert_indexed(self.img, 0, 0, 100, False, False, "ignored")
          pdb.file_gif_save(self.img, self.img.layers[0], self.savepath, self.savepath, 0, 1, self.frametime, 0)

      dial.destroy()


#The function to be registered in GIMP
def python_make_blurring(img, layer):
  ll = MainWin(img, layer)
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

