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

#This scripts creates an animated gif which shows two images alternating with a blurring dissolvence between them
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

import sys
import os
import copy
from gimpfu import *

defsavename = "/myanimated.gif"

#The function to be registered in GIMP
def python_make_switchgif(image, tdrawable, savepath, frdelay, longtime, rescale, midstart):
  if (len(image.layers) < 2):
    errmess = "The SwitchImages animation need at least two source layers!"
    pdb.gimp_message(errmess)
    raise RuntimeError(errmess)

  #Saving a copy of the original layers reference, so that altering the image.layers does not affect later references
  baselayers = copy.copy(image.layers)
  zeroname = baselayers[0].name
  
  #Resizing layers if requested
  if (rescale):
    wd = image.width
    he = image.height
    for ly in baselayers:
      if (ly.width != wd or ly.height != he):
        pdb.gimp_layer_scale(ly, wd, he, False)
  
  intersteps = range(1, 10)
  
  #Selecting the two contiguous layers between which the dissolvence is made
  for ll in range(len(baselayers)):
    bglayer = baselayers[ll]
    try:
      trlayer = baselayers[ll+1]
    except IndexError:
      trlayer = baselayers[0]
      
    #creating the phase of dissolvence between layers, setting a set of opacity and merging the paired layers
    for i in intersteps:
      abspos = ll * (len(intersteps)+1) + i
      bglayertt = bglayer.copy()
      trlayertt = trlayer.copy()
      pdb.gimp_layer_set_opacity(trlayertt, i*10)
      image.add_layer(trlayertt, abspos)
      image.add_layer(bglayertt, abspos+1)
      merglayer = pdb.gimp_image_merge_down(image, trlayertt, 0)
      merglayer.name = "ph" + str(ll) + "phase" + str(i*10)
    
    #adjusting names for timing frame
    if (ll == 0 and midstart):
      bglayer.name = bglayer.name + " (" + str(longtime/2) + "ms)"
    else:
      bglayer.name = bglayer.name + " (" + str(longtime) + "ms)"
      
  #adding final layer if midstart is requested
  if (midstart):
    finallayer = baselayers[0].copy()
    image.add_layer(finallayer, len(image.layers))
    finallayer.name = zeroname + "copy (" + str(longtime/2) + "ms)"

  #reversing the layer order: the gif shows the frames from bottom to top, so we have to reverse them
  pdb.script_fu_reverse_layers(image, image.layers[0])
  
  #preparing exporting to gif
  if (len(savepath) == 0):
    savepath = os.getcwd() + defname
  elif (savepath[-4:] != ".gif"):
    savepath = savepath + ".gif"

  pdb.gimp_image_convert_indexed(image, 1, 0, 256, False, False, "ignored") # 1 in second argument: use dithering
  pdb.file_gif_save(image, tdrawable, savepath, savepath, 0, 1, frdelay, 0)


#The command to register the function
register(
  "python-fu_make_switchgif",
  "python-fu_make_switchgif",
  "Create an animated gif which switches between two or more images with a dissolvence between them.\n\
In the gif, images follow the layer order (top to bottom of the layer list).",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Filters/Animation/SwitchImages",
  "RGB*, GRAY*",
  [
    (PF_FILE, "savepath", "Destination", os.getcwd() + defsavename),
    (PF_INT32, "frdelay", "Base delay between frames (ms)", 100),
    (PF_INT32, "longtime", "Longer delay for basic frames (ms)", 2000),
    (PF_BOOL, "rescale", "Does images have to be rescaled to the image size?", True),
    (PF_BOOL, "midstart", "Does animation have to start in the middle of a longer delay?", True),
  ],
  [],
  python_make_switchgif
  )

#The main function to activate the script
main()
