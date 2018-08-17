#!/bin/bash
#
#  install.sh
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

#setting names
mainscript="make_landmap.py"
mainfolder="make_landmap_brushes"
ausscript="stroke_vectors_options.py"

echo "$mainscript installation script, working on linux systems.\n"
echo "This script copies the main script and the other relevant files in the GIMP user directories."
echo "It assumes that your GIMP user directory is in your home. It this is not the case, give the path as first argument."

if [ -z $1 ]; then
  #looking for GIMP version
  gimpv=`gimp --version` 
  fullnumver=`echo $gimpv | cut -f6- -d\ `
  numver=`echo $fullnumver | cut -f-2 -d.`

  if [ -z $gimpv]; then
    echo "It seems you do not have a command line for GIMP. Please give the full path of your user directory as argument."
    instdir=""
  else
    instdir="$HOME/.gimp-$numver"
  fi
else
  instdir=$1
fi

if [ -d "$instdir" ]; then
  echo "Your GIMP user folder is: $instdir"
else
  echo "Cannot find your GIMP folder."
  echo "Try again typing 'install.sh path/of/your/GIMP/folder' and be sure that the path is correct."
  exit 1
fi

echo "Copying $mainscript..."
cp $mainscript $instdir/plug-ins

echo "Copying $ausscript..."
cp $ausscript $instdir/plug-ins

if [ ! -d "$instdir/plug-ins/$mainfolder" ]; then
  echo "Creating $mainfolder directory..."
  mkdir $instdir/plug-ins/$mainfolder
else
  echo "$mainfolder directory already present. Files will be overwritten."
fi


cd $mainfolder
echo "Copying png icons..."
cp *.png $instdir/plug-ins/$mainfolder
echo "Copying brushes..."
cp *.gbr $instdir/brushes
