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

* **make_landmap.py**:
  Generate a regional map. Start from an image with a single layer with white background: pop up dialogs appear to guide the user in the process. Or continue working map partially drawn. _The plug-in is not yet complete: up to now can be used to create a map with coasts, mountains, forests, rivers, towns/cities, roads. Future adding: labels._

* **smudge_all.py**:
  Smudge the full layer or a selection area in randomatic directions, creating a random smudge effect. The smudging pressure can be chosen.

* **stroke_vector_options.py**
  Stroke a path by using a list of arguments, similar to what the GIMP command stroke path can do. It is intended to be used mainly by other scripts which need to replicate those features. Currently it does not allow a custom stroking line, only a set of prebuilded lines.
