#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  copy_layer_to_channel.py
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

#This script save the content of a layer in a new channel selection mask, converting the gray scale into a selection
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)


from gimpfu import *

#The function to be registered in gimp
def python_copytochannel(img, tdraw, pos, name, delete_layer):
  channel = pdb.gimp_channel_new(img, img.width, img.height, name, 100, (0, 0, 0))
  img.add_channel(channel, pos)
  
  pdb.gimp_selection_all(img)
  if not pdb.gimp_edit_copy(tdraw):
    pdb.gimp_image_remove_channel(img, channel)
    raise RuntimeError("An error as occurred while copying from the layer!")
    
  flsel = pdb.gimp_edit_paste(channel, True)
  pdb.gimp_floating_sel_anchor(flsel)
  pdb.gimp_item_set_visible(channel, False)
  if delete_layer:
    pdb.gimp_image_remove_layer(img, tdraw)
    
  return channel
  

#The command to register the function
register(
  "python-fu-copy-layer-to-channel",
  "python-fu-copy-layer-to-channel",
  "Copy a layer in a new channel selection mask, converting the gray scale into a selection",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Layer/Copy to Channel",
  "RGB*, GRAY*",
  [
    (PF_INT32, "pos", "channel position in the list", 0),
    (PF_STRING, "name", "channel name", "channelmask"),
    (PF_BOOL, "delete_layer", "Delete the original layer?", False),
  ],
  [
    (PF_CHANNEL, "channel", "The new created channel."),
  ],
  python_copytochannel
  )

#The main function to activate the script
main()
