# -*- python -*-
#
#       image.gui : spatial nd images
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Eric Moscardi <eric.moscardi@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""
This module provide a 2D QPixmap view on spatial images
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

__all__ = ["PixmapView","PixmapStackView",
           "ScalableLabel","ScalableGraphicsView"]

from numpy import array,uint32
from PyQt4.QtCore import Qt,SIGNAL
from PyQt4.QtGui import (QImage,QPixmap,QTransform,QMatrix,
                         QLabel,QGraphicsView)
from pixmap import to_img, to_pix

class PixmapView (object) :
	"""Base class for 2D views on spatial images
	
	Provide a QPixmap when asked to
	"""
	
	def __init__ (self, img = None, palette = None) :
		"""Constructor
		
		:Parameters:
		 - `img` (array) - a more than 3D array
		 - `palette` (array of qRgba) - see set_palette
		"""
		self._palette = None
		self._img = None
		self._transform = 0
		
		if palette is not None :
			self.set_palette(palette)
		
		if img is not None :
			self.set_image(img)
	
	########################################
	#
	#	accessors
	#
	########################################
	def image (self) :
		"""Get currently displayed image
		
		:Returns Type: `array`
		"""
		return self._img
	
	def set_image (self, img) :
		"""Set an image to display
		
		:Parameters:
		 - `im` (array)
		"""
		self._img = img
	
	def palette (self) :
		"""Palette used to associate a color with info contains in a voxel
		
		:Returns Type: array of qRgba
		"""
		return self._palette
	
	def set_palette (self, palette) :
		"""Set the palette
		
		.. warning:: will cast color value to uint32
		
		:Parameters:
		 - `palette` (list of int)
		"""
		self._palette = array(palette,uint32)
	
	def pixmap (self) :
		"""Return a pixmap representation of the spatial image
		"""
		raise NotImplementedError("TO subclass")
	
	def resolution (self) :
		"""Return resolution of the pixmap
		
		:Returns Type: float,float
		"""
		if self._img is None : return
		return getattr(self._img,"resolution",(1,1) )[:2]
	
	def pixmap_real_size (self) :
		"""Return the spatial extension of the pixmap
		
		:Returns Type: float,float
		"""
		res = self.resolution()
		if res is None : return
		
		pix = self.pixmap()
		if pix is None : return
		
		return pix.width() * res[0],pix.height() * res[1]
	
	########################################
	#
	#	view transformation
	#
	########################################
	def rotate (self, orient) :
		"""Rotate view 90 degrees
		
		:Parameters:
		 - `orient` (int) - orientation of rotation
		    - if orient == 1, rotation clockwise
		    - if orient == -1, rotation counterclockwise
		"""
		self._transform = (self._transform + orient * 90) % 360
	
	def data_coordinates (self, x_pix, y_pix) :
		"""Convert coordinates expressed in the pixmap into
		coordinates expressed as indices in the data space.
		
		:Parameters:
		 - `x_pix` (int)
		 - `y_pix` (int)
		
		:Returns Type: int,int
		"""
		raise NotImplementedError("TO subclass")
	
	def image_coordinates (self, x_pix, y_pix) :
		"""Convert coordinates expressed in the pixmap into
		coordinates expressed in the image space.
		
		:Parameters:
		 - `x_pix` (int)
		 - `y_pix` (int)
		
		:Returns Type: float,float
		"""
		inds = self.data_coordinates(x_pix,y_pix)
		
		try :
			res = self._img.resolution
			coords = array(res) * inds
		except AttributeError :
			coords = inds
		
		return coords
	
	def pixmap_coordinates (self, inds) :
		"""Convert coordinates expressed in data space into a point in the
		pixmap space
		
		:Parameters:
		 - `inds` (tuple of int) - coordinate of a point in data space
		                           e.g. i,j or i,j,k
		
		:Returns Type: int,int
		"""
		raise NotImplementedError("TO subclass")


class PixmapStackView (PixmapView) :
	"""Pixmap view of a spatial image as a stack of images
	"""
	def __init__ (self, img = None, palette = None, order='C') :
		"""Constructor
		
		:Parameters:
		 - `img` (array) - a more than 3D array
		 - `palette` (array of qRgba) - see set_palette
		"""
		self._pixmaps = []
		self._current_slice = 0
		self.order = order

		PixmapView.__init__(self,img,palette)
	
	def _reconstruct_pixmaps (self) :
		pal = self.palette()
		data = self.image()
		
		#rotation
		tr = QTransform()
		tr.rotate(self._transform)
		
		#construct pixmaps
		pix = []
		for z in xrange(data.shape[2]) :
			#dat = pal[data[:,:,z] ].flatten('F')
			dat = pal[ uint32(data[:,:,z]) ]
			#img = QImage(dat,
			#             data.shape[0],
			#             data.shape[1],
			#             QImage.Format_ARGB32)
                        dat = to_pix (dat,self.order)
			pix.append(dat.transformed(tr) )
		
		self._pixmaps = pix
		self._current_slice = min(max(self._current_slice,0),len(pix) - 1)

	########################################
	#
	#	accessors
	#
	########################################
	def nb_slices (self) :
		"""Number of slices in the stack
		
		:Returns Type: int
		"""
		return len(self._pixmaps)
	
	def current_slice (self) :
		"""Index of the currently displayed slice
		
		:Returns Type: int
		"""
		return self._current_slice
	
	def set_current_slice (self, ind) :
		"""Change current displayed slice
		
		:Parameters:
		 - `ind` (int) - index of the slice in the data array
		"""
		self._current_slice = ind
	
	def pixmap (self) :
		"""Return a pixmap representation of the spatial image
		"""
		if self._current_slice < len(self._pixmaps) :
			return self._pixmaps[self._current_slice]
		else :
			return None
	
	def set_palette (self, palette) :
		"""Set the palette
		
		.. warning:: will cast color value to uint32
		
		:Parameters:
		 - `palette` (list of int)
		"""
		PixmapView.set_palette(self,palette)
		
		if self.image() is not None :
			self._reconstruct_pixmaps()
	
	def set_image (self, img) :
		"""Set an image to display
		
		:Parameters:
		 - `im` (array)
		"""
		PixmapView.set_image(self,img)
		
		if self.palette() is not None :
			self._reconstruct_pixmaps()
	
	########################################
	#
	#	view transformation
	#
	########################################
	def rotate (self, orient) :
		"""Rotate view 90 degrees
		
		:Parameters:
		 - `orient` (int) - orientation of rotation
		    - if orient == 1, rotation clockwise
		    - if orient == -1, rotation counterclockwise
		"""
		PixmapView.rotate(self,orient)
		
		tr = QTransform()
		tr.rotate(orient * 90)
		self._pixmaps = [pix.transformed(tr) for pix in self._pixmaps]
	
	def data_coordinates (self, x_pix, y_pix) :
		"""Convert coordinates expressed in the pixmap into
		coordinates expressed as indices in the data space.
		
		:Parameters:
		 - `x_pix` (int)
		 - `y_pix` (int)
		
		:Returns Type: int,int
		"""
		if len(self._pixmaps) == 0 :
			raise UserWarning("no image loaded")
		
		w,h = self.image().shape[:2]
		w_pix = self.pixmap().width()
		h_pix = self.pixmap().height()
		if self._transform == 0 :
			i = x_pix * w / w_pix
			j = y_pix * h / h_pix
		elif self._transform == 90 :
			i = y_pix * h / h_pix
			j = (w_pix - x_pix) * w / w_pix
			#i = (h_pix - y_pix) * h / h_pix
			#j = x_pix * w / w_pix
		elif self._transform == 180 :
			i = (w_pix - x_pix) * w / w_pix
			j = (h_pix - y_pix) * h / h_pix
		elif self._transform == 270 :
			i = (h_pix - y_pix) * h / h_pix
			j = x_pix * w / w_pix
			#i = y_pix * h / h_pix
			#j = (w_pix - x_pix) * w / w_pix
		return i,j,self._current_slice
	
	def pixmap_coordinates (self, i, j) :
		"""Convert coordinates expressed in data space into a point in the
		pixmap space
		
		:Parameters:
		 - `inds` (tuple of int) - coordinate of a point in data space
		                           e.g. i,j or i,j,k
		
		:Returns Type: int,int
		"""
		w,h = self.image().shape[:2]
		w_pix = self.pixmap().width()
		h_pix = self.pixmap().height()
		if self._transform == 0 :
		        x_pix = i * w_pix / w
			y_pix = j * h_pix / h
		elif self._transform == 90 :
			y_pix = i * h / h_pix
			x_pix = (w_pix - j) * w_pix / w
			#i = (h_pix - y_pix) * h / h_pix
			#j = x_pix * w / w_pix
		elif self._transform == 180 :
			x_pix = (w_pix - i) * w_pix / w
			y_pix = (h_pix - j) * h_pix / h
		elif self._transform == 270 :
			y_pix = (h_pix - i) * h_pix / h
			x_pix = j * w_pix / w
			#i = y_pix * h / h_pix
			#j = (w_pix - x_pix) * w / w_pix
		return x_pix,y_pix


class ScalableLabel (QLabel) :
	"""Scalable label that respect the ratio of the pixmap it display
	"""
	def __init__ (self, parent = None) :
		QLabel.__init__(self,parent)
		self.setScaledContents(True)
		
		self._ratio = 1.
		self._resolution = (1.,1.)
	
	def _compute_ratio (self) :
		pix = self.pixmap()
		if pix is not None :
			vx,vy = self._resolution
			self._ratio = (pix.height() * vy) / (pix.width() * vx)
	
	def set_resolution (self, x_scale, y_scale) :
		"""Set the resolution of the image
		
		:Parameters:
		 - `x_scale` (float) - size of a pixel in x direction
		 - `y_scale` (float) - size of a pixel in y direction
		"""
		self._resolution = (x_scale,y_scale)
		self._compute_ratio()
	
	def pixmap_coordinates (self, x_screen, y_screen) :
		"""Compute pixmaps coordinates that map the given point on the screen
		
		:Parameters:
		 - `x_screen` (int)
		 - `y_screen` (int)
		"""
		pix = self.pixmap()
		if pix is None :
			return None
		
		x_pix = x_screen * pix.width() / self.width()
		y_pix = y_screen * pix.height() / self.height()
		
		return x_pix,y_pix
	
	def resizeEvent (self, event) :
		if event.oldSize() != event.size() :
			w = event.size().width()
			h = event.size().height()
			if int(w * self._ratio) <= h :
				self.resize(w,w * self._ratio)
			else :
				self.resize(h / self._ratio,h)
	
	def setPixmap (self, pix) :
		QLabel.setPixmap(self,pix)
		self._compute_ratio()

	
	def mousePressEvent (self, event) :
		self.emit(SIGNAL("mouse_press"),event)
	
	def mouseMoveEvent (self, event) :
		self.emit(SIGNAL("mouse_move"),event)


class ScalableGraphicsView (QGraphicsView) :
    """Graphics View that always zoom to fit it's content
    """
	
    def __init__ (self, *args, **kwargs) :
        QGraphicsView.__init__(self,*args,**kwargs)
	self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	
    def resizeEvent (self, event) :
	sc = self.scene()
	if sc is not None and event.oldSize() != event.size() :
            if sc.width() > 0 and sc.height() > 0 :
		s = min(event.size().width() / sc.width(),
			event.size().height() / sc.height() )
			
	        t = QMatrix()
	        t.scale(s,s)
	        self.setMatrix(t)

    def mousePressEvent (self, event) :
	self.emit(SIGNAL("mouse_press"),event.pos(),self)
	
    def mouseMoveEvent (self, event) :
    	self.emit(SIGNAL("mouse_move"),event)
