from openalea.release import Formula
from openalea.release.utils import sh
from openalea.release.formula.boost import boost
from openalea.release.formula.mingw import mingw
from os.path import join as pj

class cgal(Formula):
    license = "GNU Lesser Public License"
    authors = "CGAL, Computational Geometry Algorithms Library"
    description = "Windows gcc libs and includes of CGAL"
    py_dependent   = False
    arch_dependent = True  
    homepage = "http://www.cgal.org/"
    download_url = "https://gforge.inria.fr/frs/download.php/30390/CGAL-4.0.zip"
    #download_url = "https://gforge.inria.fr/frs/download.php/32358/CGAL-4.2.zip"
    download_name  = "cgal_src.zip"
    required_tools = ["cmake"]
    version = "4.0"
    DOWNLOAD = UNPACK = CONFIGURE = MAKE = MAKE_INSTALL = EGGIFY = True
    
    def setup(self):
        return dict( 
                    VERSION          = self.version,
                    LIB_DIRS         = {'lib' : pj(self.sourcedir,'lib') },
                    INC_DIRS         = {'include' : pj(self.sourcedir,'include') },
                    BIN_DIRS         = {'bin' : pj(self.sourcedir,'bin') },
                    ) 
    def configure(self):
        compiler = mingw().get_path()
        boost_ = boost()
        db_quote = lambda x: '"'+x+'"'
        options = " ".join(['-DCMAKE_INSTALL_PREFIX='+db_quote(self.installdir),
                            '-DCMAKE_CXX_COMPILER:FILEPATH='+db_quote(pj(compiler,"bin","g++.exe")),
                            '-DBOOST_ROOT='+db_quote(boost_.installdir),
                            '-DGMP_INCLUDE_DIR='+db_quote( pj(compiler, "include") ),
                            '-DMPFR_INCLUDE_DIR='+db_quote( pj(compiler, "include") ),
                            '-DZLIB_INCLUDE_DIR='+db_quote(pj(compiler, "include")),
                            '-DZLIB_LIBRARY='+db_quote(pj(compiler, "lib", "libz.a")),
                            #'-DOPENGL_LIBRARIES='+db_quote(pj(compiler,"..", "lib", "libglu32.a")),
                            ])
        options=options.replace("\\", "/") #avoid "escape sequence" errors with cmake
        cmd = 'cmake -G"MinGW Makefiles" '+options+' . '
        print cmd
        print ""
        return sh(cmd) == 0   