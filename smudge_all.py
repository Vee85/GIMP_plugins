#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  smudge_all.py
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
import math
import random
from gimpfu import *

#The function to be registered in gimp
def python_smudgeall(img, tdraw, smudgefreq):
  brs = int(pdb.gimp_context_get_brush_size())
  gimp.progress_init("python-fu-smudgeall")
  
  #searching for active selection and limit pixel coordinates to its bounding box if present, it saves time
  non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(img)
  if (non_empty):
    xll = [x for x in range(x1+(brs/4), x2-(brs/4), brs/2)]
    yll = [y for y in range(y1+(brs/4), y2-(brs/4), brs/2)]
  #if there is no active selection, go for the full image
  else:
    xll = [x for x in range(0+(brs/4), img.width-(brs/4), brs/2)]
    yll = [y for y in range(0+(brs/4), img.height-(brs/4), brs/2)]

  #apply smudge to all the coordinates
  gimp.progress_update(0.0)
  for cx, i in zip(xll, range(len(xll))):
    for cy in yll:
      rang = 2 * math.pi * random.random()
      rsin = math.sin(rang) * brs
      rcos = math.cos(rang) * brs
      pdb.gimp_smudge(tdraw, smudgefreq, 4, [cx, cy, cx+rsin, cy+rcos])
    
    #Updating percentage bar
    gimp.progress_update(float(i)/len(xll))


#The command to register the function
register(
  "python-fu-smudgeall",
  "python-fu-smudgeall",
  "Smudge image in randomatic direction",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Filters/SmudgeAll",
  "RGB*, GRAY*",
  [
    (PF_INT32, "smudgefreq", "Smudge pressure (0 <= pressure <= 100)", 50),
  ],
  [],
  python_smudgeall
  )

#The main function to activate the script
main()
