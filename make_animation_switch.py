#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  make_animation_switch.py
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

#This scripts creates an animated gif which shows two images alternating with a dissolvence between them
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

import sys
import os
from gimpfu import *

defsavename = "/myanimated.gif"

#The function to be registered in GIMP
def python_make_switchgif(timg, tdrawable, fn_imagebg, fn_imagetransp, savepath, frdelay, longtime):
  image = pdb.gimp_file_load(fn_imagebg, fn_imagebg)
  trlayer = pdb.gimp_file_load_layer(image, fn_imagetransp)
  trlayer.name = "upimage"
  bglayer = image.layers[0]
  bglayer.name = "downimage"
  image.add_layer(trlayer, 1)

  #creating the first phase of layers, setting a set of opacity and merging the paired layers
  for i in range(1, 10):
    bglayertt = bglayer.copy()
    trlayertt = trlayer.copy()
    pdb.gimp_layer_set_opacity(trlayertt, i*10)
    image.add_layer(trlayertt, 2)
    image.add_layer(bglayertt, 3)
    merglayer = pdb.gimp_image_merge_down(image, trlayertt, 0)
    merglayer.name = "phase" + str(i*10)
  
  pdb.gimp_image_lower_item_to_bottom(image, bglayer)

  #creating the second phase of layers with reversed opacity order
  allph = image.layers[1:-1]
  for ll in allph[::-1]: #this reverses the list
    nl = len(image.layers)
    newl = ll.copy()
    newl.name = ll.name + "d"
    image.add_layer(newl, nl)
  
  closel = trlayer.copy()
  image.add_layer(closel, len(image.layers))
  
  #adjusting names for timing frame
  closel.name = trlayer.name + "bis(" + str(longtime/2) + "ms)"
  trlayer.name = trlayer.name + " (" + str(longtime/2) + "ms)"
  bglayer.name = bglayer.name + " (" + str(longtime) + "ms)"

  #preparing exporting to gif
  if (len(savepath) == 0):
    savepath = os.getcwd() + defname
  elif (savepath[-4:] != ".gif"):
    savepath = savepath + ".gif"

  pdb.gimp_image_convert_indexed(image, 0, 0, 100, 1, 1, "ignored")
  pdb.file_gif_save(image, tdrawable, savepath, savepath, 0, 1, frdelay, 0)


#The command to register the function
register(
  "python-fu_make_switchgif",
  "python-fu_make_switchgif",
  "Create an animated gif which switches between two images with a dissolvence between them",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Image/MakeAnimationSwitchGif...",
  "RGB*, GRAY*",
  [
    (PF_FILE, "imagebg", "Image1", ""),
    (PF_FILE, "imagetransp", "Image2", ""),
    (PF_FILE, "savepath", "Destination", os.getcwd() + defsavename),
    (PF_INT32, "frdelay", "Base delay between frames (ms)", 100),
    (PF_INT32, "longtime", "Longer delay for basic frames (ms)", 2000),
  ],
  [],
  python_make_switchgif
  )

#The main function to activate the script
main()
