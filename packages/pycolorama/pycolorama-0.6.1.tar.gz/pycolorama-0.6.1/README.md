PyColorama
==========

This is a simple package to handle easily various colors in either the PyGame (RGB) format or the OpenCV (BGR) format. 
Default mode is PyGame.


Example
-------


Just use like that :

**example for PyGame color**

`import pycolorama as pc`

`COLOR = pc.COLOR(pc.PYGAME)` 

`print(COLOR.WHITE)`

Will return : (0,0,255)


**example for OpenCV color**

`import pycolorama as pc`

`COLOR = pc.COLOR(pc.OPENCV)`

`print(COLOR.BLUE)`

Will return : (255,0,0)