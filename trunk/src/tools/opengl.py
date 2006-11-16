# -*-python-*-
# OpenGL configure environment
# Author: Christophe Pradal ( christophe.pradal@cirad.fr )
# Licence: GPL

import os, sys
from sconsx.config import *


class OpenGL:
   def __init__( self, config ):
      self.name= 'opengl'
      self.config= config
      self._default= {}


   def default( self ):

      if isinstance( platform, Win32 ):
         MVSdir = r'C:\Program Files\Microsoft Visual Studio\VC98'
         self._default[ 'include' ]= pj( MVSdir, 'Include' )
         self._default[ 'lib' ]= pj( MVSdir, 'Lib' )
      elif isinstance( platform, Posix ):
         self._default[ 'include' ]= '/usr/X11R6/include'
         self._default[ 'lib' ]= '/usr/X11R6/lib'


   def option(  self, opts ):

      self.default()

      opts.AddOptions( 
         PathOption( 'gl_includes', 'GL include files', 
          self._default[ 'include' ]),

         PathOption( 'gl_lib', 'GL library path', 
         self._default[ 'lib' ] )
         )


   def update( self, env ):
      """ Update the environment with specific flags """
      env.AppendUnique( CPPPATH= [ env['gl_includes'] ] )
      env.AppendUnique( LIBPATH= [ env['gl_lib'] ] )

      if isinstance( platform, Cygwin ):
         env.AppendUnique( LIBS= [ 'opengl32','glu32', 'glut32' ] )
      elif isinstance( platform, Posix ):
         env.AppendUnique( LIBS= [ 'GLU', 'glut' ] )
      elif isinstance( platform, Win32 ):
         env.AppendUnique( LIBS= [ 'opengl32','GLU32', 'glut32' ] )


   def configure( self, config ):
      if not config.conf.CheckLibWithHeader('GL',[ 'GL/gl.h', 'GL/glu.h' ], 'c++', autoadd= 0 ):
         print "Error: gl.h not found, probably failure in automatic opengl detection"
         sys.exit(-1)


def create( config ):
   " Create opengl tool "
   opengl= OpenGL( config )

   return opengl

