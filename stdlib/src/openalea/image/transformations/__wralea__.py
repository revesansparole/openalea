# -*- python -*-
#
#       OpenAlea.StdLib
#
#       Copyright 2006 - 2008 INRIA - CIRAD - INRA  
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################


__doc__ = """ openalea.image """
__revision__ = " $Id: __wralea__.py 1586 2009-01-30 15:56:25Z cokelaer $ "


from openalea.core import *

__name__ = "openalea.image.transformations"
__alias__ = ["image.transformations"]

__version__ = '0.0.1'
__license__ = 'CECILL-C'
__authors__ = 'OpenAlea Consortium'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'PIL wrapping and utils module.'
__url__ = 'http://openalea.gforge.inria.fr'

__all__ = ["blend", "composite", "merge", "merge_rgb", "merge_rgb_data",
           "paste", "putpix", "putpixL", "fillL", "fill_rgb", "put_alpha",
           "split", "rgb2hsl", "hsl2rgb", "hue_distance", "hue_nearest",
           "levelL", "rainbow_lut", "lut2image",
           ]



from openalea.core import Factory
from openalea.core.interface import *
from openalea.image.interface import IPix

blend = Factory( name= "blend", 
                 description= "create an interpolation between two images", 
                 category = "Image", 
                 nodemodule = "image_transfo",
                 nodeclass = "blend",
                 inputs=(dict(name="Image", interface=IPix,),dict(name="Image", interface=IPix,),
                         dict(name="alpha", interface=IFloat(min=0., max=1.0),value=0.5),),
                 outputs=(dict(name="Image", interface=IPix,),),
                 )


composite = Factory( name= "composite", 
                     description= "create an interpolation between two images", 
                     category = "Image", 
                     nodemodule = "image_transfo",
                     nodeclass = "composite",
                     inputs=(dict(name="Image", interface=IPix,),
                             dict(name="Image", interface=IPix,),
                             dict(name="masklpha", interface=IPix,),),
                     outputs=(dict(name="Image", interface=IPix,),),
                     )


merge = Factory( name= "merge", 
                 description= "merge bands into a single image", 
                 category = "Image", 
                 nodemodule = "image_transfo",
                 nodeclass = "merge",
                 inputs=(dict(name="mode", interface=IStr,),
                         dict(name="bands", interface=ISequence,),),
                 outputs=(dict(name="Image", interface=IPix,),),
                 )

merge_rgb = Factory( name= "mergeRGB", 
                     description= "merge Image of channels into a single image", 
                     category = "Image", 
                     nodemodule = "image_transfo",
                     nodeclass = "merge_rgb",
                     inputs=(dict(name="R", interface=IPix,),
                             dict(name="G", interface=IPix,),
                             dict(name="B", interface=IPix,),
                             dict(name="A", interface=IPix,),),
                     outputs=(dict(name="Image", interface=IPix,),),
                     )


merge_rgb_data = Factory( name= "mergeRGBData", 
                          description= "merge sequence of R,G,B channels into a single image", 
                          category = "Image", 
                          nodemodule = "image_transfo",
                          nodeclass = "merge_rgbData",
                          inputs=(dict(name="R", interface=ISequence,),
                                  dict(name="G", interface=ISequence,),
                                  dict(name="B", interface=ISequence,),
                                  dict(name="dimX", interface=IInt(min=0, max=100000),value=100),
                                  dict(name="dimY", interface=IInt(min=0, max=100000),value=100),),
                          outputs=(dict(name="Image", interface=IPix,),),
                          )


paste = Factory( name= "paste", 
                 description= "paste an image into another", 
                 category = "Image", 
                 nodemodule = "image_transfo",
                 nodeclass = "paste",
                 inputs=(dict(name="Image", interface=IPix,),
                         dict(name="Image", interface=IPix,),
                         dict(name="x", interface=IInt,),
                         dict(name="y",interface=IInt)),
                  outputs=(dict(name="Image", interface=IPix,),),
                  )


putpix = Factory( name= "put pixel RGB", 
                  description= "set color of a pixel inside a RGB image", 
                  category = "Image", 
                  nodemodule = "image_transfo",
                  nodeclass = "put_pixel_rgb",
                  inputs=(dict(name="Image", interface=IPix,),
                          dict(name="x",interface=IInt(min=0)),
                          dict(name="y",interface=IInt(min=0)),
                          dict(name="color",interface=IRGBColor,),
                          ),
                  outputs=(dict(name="Image", interface=IPix,),),
                  )


putpixL = Factory( name= "put pixel L", 
                   description= "set color of a pixel inside a one band image", 
                   category = "Image", 
                   nodemodule = "image_transfo",
                   nodeclass = "put_pixel_rgb",
                   inputs=(dict(name="Image", interface=IPix,),
                           dict(name="x",interface=IInt(min=0)),
                           dict(name="y",interface=IInt(min=0)),
                           dict(name="color",interface=IInt(min=0, max=255),),
                           ),
                  outputs=(dict(name="Image", interface=IPix,),),
                   )


fillL = Factory( name= "fill L", 
                 description= "fill a rectangle with a 0-255 (L) color", 
                 category = "Image", 
                 nodemodule = "image_transfo",
                 nodeclass = "fill",
                 inputs=(dict(name="Image", interface=IPix,),
                         dict(name="color", interface=IInt(min=0,max=255), value=0),
                         dict(name="xmin", interface=IInt,),
                         dict(name="xmax",interface=IInt),
                         dict(name="ymin",interface=IInt),
                         dict(name="ymax",interface=IInt)),
                 outputs=(dict(name="Image", interface=IPix,),),
                 )

fill_rgb = Factory( name= "fillRGB", 
                    description= "fill a rectangle with a RGB color", 
                    category = "Image", 
                    nodemodule = "image_transfo",
                    nodeclass = "fill",
                    inputs=(dict(name="Image", interface=IPix,),
                            dict(name="color", interface=IRGBColor, value=(0,0,0)),
                            dict(name="xmin", interface=IInt,),
                            dict(name="xmax",interface=IInt),
                            dict(name="ymin",interface=IInt),
                            dict(name="ymax",interface=IInt)),
                    outputs=(dict(name="Image", interface=IPix,),),
                    )


put_alpha = Factory( name= "put_alpha", 
                     description= "add an alpha mask to an image", 
                     category = "Image", 
                     nodemodule = "image_transfo",
                     nodeclass = "put_alpha",
                     inputs=(dict(name="Image", interface=IPix,),
                             dict(name="alpha", interface=IPix,),),
                     outputs=(dict(name="Image", interface=IPix,),),
                     )


split = Factory( name= "split", 
                 description= "split bands of an image", 
                 category = "Image", 
                 nodemodule = "image_transfo",
                 nodeclass = "split",
                 inputs=(dict(name="Image", interface=IPix,),),
                 outputs=(dict(name="R", interface=IPix,),
                          dict(name="G", interface=IPix,),
                          dict(name="B", interface=IPix,),
                          dict(name="A", interface=IPix,),),
                 )

    
rgb2hsl = Factory( name= "rgb2hsl",
                   description= "Transformation of colour space",
                   category = "Image",
                   nodemodule = "image_transfo",
                   nodeclass = "rgb2hsl",
                   inputs=(dict(name="Image", interface=IPix,),),
                   outputs=(dict(name="H", interface=ISequence,),
                            dict(name="S", interface=ISequence,),
                            dict(name="L", interface=ISequence,),),
                   )


hsl2rgb = Factory( name= "hsl2rgb",
                   description= "Transformation of colour space",
                   category = "Image",
                   nodemodule = "image_transfo",
                   nodeclass = "hsl2rgb",
                   inputs=(dict(name="H", interface=ISequence,),
                           dict(name="S", interface=ISequence,),
                           dict(name="L", interface=ISequence,),),
                   outputs=(dict(name="R", interface=IPix,),
                            dict(name="G", interface=ISequence,),
                            dict(name="B", interface=ISequence,),),
                   )


hue_distance = Factory( name= "hueDistance",
                        description= "Distance to a reference hue",
                        category = "Image",
                        nodemodule = "image_transfo",
                        nodeclass = "hue2RefDistance",
                        inputs=(dict(name="Image", interface=IPix,),
                                dict(name="ReferenceHue", interface=IFloat(min=0, max=1.0),value=0.5),),
                        outputs=(dict(name="Image", interface=IPix,),),
                        )



hue_nearest = Factory( name= "hueNearest",
                       description= "Enlight the hue near to the reference",
                       category = "Image",
                       nodemodule = "image_transfo",
                       nodeclass = "hue2RefNearest",
                       inputs=(dict(name="Image", interface=IPix,),
                               dict(name="ReferenceHue", interface=IFloat(min=0, max=1.0),value=0.5),),
                       outputs=(dict(name="Image", interface=IPix,),),
                       )


levelL = Factory( name= "levels L", 
                  description= "change pixels lower than min and higher than max on one band image", 
                  category = "Image", 
                  nodemodule = "image_transfo",
                  nodeclass = "seuillage",
                  inputs=(dict(name="Image", interface=IPix,),
                          dict(name="Low", interface=IInt(min=0, max=255),value=100),
                          dict(name="High", interface=IInt(min=0, max=255),value=100),
                          ),
                  outputs=(dict(name="Thresholded pix", interface=IPix,),),
                  )


rainbow_lut = Factory( name= "rainbow_lut", 
                       description= "Create a new rainbow lut expanding from 0 to max_index", 
                       category = "Image", 
                       nodemodule = "lut",
                       nodeclass = "create_rainbow_LUT",
                       inputs=(dict(name="N_max", interface=IInt(min=1, max=16000000),value=255),
                               ),
                       outputs=(dict(name="Rainbow_LUT", interface=None,),),
                       )


lut2image = Factory( name= "lut2image", 
              description= "Create an image from a LUT and allows its visualization", 
              category = "Image", 
              nodemodule = "lut",
              nodeclass = "rainbow_lut2image",
              inputs=(dict(name="LUT", interface=None),
                      ),
              outputs=(dict(name="Rainbow_LUT_Image", interface=IPix,),),
              )

