#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stroke_vectors_options.py
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

#This script strokes a path by using a list of arguments, similar to what the GIMP command stroke path can do.
#It is intended to be used mainly by other scripts which need to replicate those features.
#This script must be placed in ~/.gimp-n.m/plug-ins
#where n.m is the gimp version (e.g. 2.8)

import sys
import os
from gimpfu import *


class VectorStroker:
  """Class to stroke a vector"""
  #constructor
  def __init__(self, image, tdraw, vector, pixsize, tstroke):
    self.img = image
    self.layer = tdraw
    self.vector = vector
    self.pxs = pixsize
    self.tstroke = int(tstroke)
    self.dashl = 10 * pixsize
    self.factorlist = [0.7, 0.5, 0.3]
    self.factorlistb = [0.6, 0.5]
    self.ndotsperunilist = [2, 3, 5, 10]
    self.dotspace = 0.2

    self.oldbrush = pdb.gimp_context_get_brush()
    self.oldbrushsize = pdb.gimp_context_get_brush_size()

  def checkvector(self):
    """Checking the presence of a vector"""
    res = True
    if self.vector is None:
      res = False
    return res

  def drawdash(self, sid, start, stop, fd):
    """Draw a single dash segment on the vector path with id 'sid' starting from 'start' and terminating at 'stop'
    'start' and 'stop' are measured on the path, and only the first 'fd' part is actually drawn.
    """

    if stop > start:
      ltodraw = (stop - start) * fd
      steps = (2*ltodraw) / self.pxs
      dp = [start + ((i * ltodraw)/steps) for i in range(int(steps)+1)]

      length = pdb.gimp_vectors_stroke_get_length(self.vector, sid, 0.1)
      points = [pdb.gimp_vectors_stroke_get_point_at_dist(self.vector, sid, dd, 0.1)[0:2] for dd in dp if dd < length]
      strokes = list(sum(points, ())) #this flatten the list of tuples
      
      pdb.gimp_paintbrush_default(self.layer, len(strokes), strokes)
    else:
      pdb.gimp_message("Error! drawdash 'stop' argument is lesser than 'start' argument!")

  def drawdotted(self, sid, start, stop, np):
    """Draw equally spaced 'np' dots on the vector path with id 'sid' starting from 'start' and terminating at 'stop'
    'start' and 'stop' are measured on the path, and the spacing considers that at the 'stop' point there is an extra undrawn dot
    """

    if stop > start:
      ltodraw = (stop - start)
      dp = [start + ((i * ltodraw)/(np)) for i in range(int(np))]

      length = pdb.gimp_vectors_stroke_get_length(self.vector, sid, 0.1)
      points = [pdb.gimp_vectors_stroke_get_point_at_dist(self.vector, sid, dd, 0.1)[0:2] for dd in dp if dd < length]

      for strokes in points:
        pdb.gimp_paintbrush_default(self.layer, 2, strokes)

    else:
      pdb.gimp_message("Error! drawdotted 'stop' argument is lesser than 'start' argument!")

  def stroking(self):
    """Stroking the vector path according to the parameters in the object attributes"""
    if not self.checkvector():
      pdb.gimp_message("You have to create and select a path!")
      return None
      
    pdb.gimp_image_undo_group_start(self.img)

    #setting the brush
    pdb.gimp_context_set_brush('2. Hardness 100')
    pdb.gimp_context_set_brush_size(self.pxs)

    #checking the vector
    _, stroke_ids = pdb.gimp_vectors_get_strokes(self.vector)

    #drawing
    if self.tstroke == 0: #solid line
      pdb.gimp_edit_stroke_vectors(self.layer, self.vector)
    elif self.tstroke in [1, 2, 3]: #long, medium, short dashed line
      factor = self.factorlist[self.tstroke-1]
      for ids in stroke_ids:
        length = pdb.gimp_vectors_stroke_get_length(self.vector, ids, 0.1)
        ndash = length/self.dashl
        for i in range(int(ndash)+1):
          self.drawdash(ids, i * self.dashl, (i+1) * self.dashl, factor)
        
    elif self.tstroke in [4, 5, 6, 7]: #sparse, normal, dense dotted, stippled line
      ndotsperuni = self.ndotsperunilist[self.tstroke-4]
      for ids in stroke_ids:
        length = pdb.gimp_vectors_stroke_get_length(self.vector, ids, 0.1)
        ns = (ndotsperuni * length) / self.dashl
        self.drawdotted(ids, 0, length, ns+1)

    elif self.tstroke in [8, 9]: #dash dotted, dash dot dotted line
      factor = self.factorlistb[self.tstroke-8]
      for ids in stroke_ids:
        length = pdb.gimp_vectors_stroke_get_length(self.vector, ids, 0.1)
        ndash = length/self.dashl
        for i in range(int(ndash)+1):
          sta = i * self.dashl
          end = (i+1) * self.dashl
          stb = (i + factor + self.dotspace) * self.dashl
          self.drawdash(ids, sta, end, factor)
          if self.tstroke == 8:
            self.drawdotted(ids, stb, end, 1)
          if self.tstroke == 9:
            self.drawdotted(ids, stb, end, 2)

    pdb.gimp_context_set_brush(self.oldbrush)
    pdb.gimp_context_set_brush_size(self.oldbrushsize)
    pdb.gimp_image_undo_group_end(self.img)


#The function to be registered in gimp
def python_strokevectors(img, tdraw, vector, pixsize, tstroke):
  vs = VectorStroker(img, tdraw, vector, pixsize, tstroke)
  vs.stroking()


#The command to register the function
register(
  "python-fu-stroke-vectors",
  "python-fu-stroke-vectors",
  "Stroke a path by using a list of arguments, similar to what the GIMP command stroke path can do. \
This script is intended to be used mainly by other scripts which need to repplicate those features.",
  "Valentino Esposito",
  "Valentino Esposito",
  "2018",
  "<Image>/Edit/StrokeVector",
  "RGB*, GRAY*",
  [
    (PF_VECTORS, "vector", "The path to be stroked", None),
    (PF_INT32, "pixsize", "Size in pixel of the stroke", 5),
    (PF_SPINNER, "tstroke", "Line: Solid (0); Long dashed (1); Medium dashed (2); Short dashed (3); Sparse dotted (4);\n \
Normal dotted (5); Dense dotted (6); Stipples (7); Dash dotted (8); Dash dot dotted (9)", 0, (0, 9, 1)),
  ],
  [ ],
  python_strokevectors
  )

#The main function to activate the script
main()
