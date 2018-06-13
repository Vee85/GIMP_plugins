# GIMP_plugins
### Plug-ins for GIMP (in python), released under GPL 3.
#### On the Linux version of GIMP, these scripts must be placed in ~/.gimp-n.m/plug-ins where n.m is the gimp version (e.g. 2.8)

* **copy_layer_to_channel.py**:
  Copy a layer in a channel selection mask, converting the gray scale into a selection. Useful to create complex selection areas, an alternative way to the QuickMask.

* **make_animation_blurring.py**:
  Set up the animation of the base image using the motion blur filter. A set of directions can be chosen, the animation can be performed by the script or by the user at a later time.

* **make_animation_snowing.py**:
  Create an animation superimposing a snowing effect on an image. The snow can fall in any direction and various parameters can be set in order to control the number of snow flakes, their size, their falling speed.

* **make_animation_switch.py**:
  Create an animated gif which switches between two o more images with a blurring dissolvence between them. In case more images are provided, the switching is performed passing by an image to the next one, closing the loop with the first image.

* **smudge_all.py**:
  Smudge the full layer or a selection area in randomatic directions, creating a random smudge effect. The smudging pressure can be chosen.
