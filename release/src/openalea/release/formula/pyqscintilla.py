from openalea.release import Formula
from openalea.release.utils import sh, pj
from openalea.release.formula.qt4 import qt4
from openalea.release.formula.qscintilla import qscintilla
from openalea.release.formula.pyqt4 import pyqt4
import sys

class pyqscintilla(Formula):
    download_url = None # shares the same as qscintilla
    download_name  = "qscintilla_src.zip"
    CONFIGURE = MAKE = MAKE_INSTALL = EGGIFY = True

    def __init__(self, *args, **kwargs):
        super(pyqscintilla, self).__init__(*args, **kwargs)
        # define installation paths
        qsci = qscintilla()
        qt4_ = qt4()
        pyqt = pyqt4()
        self.install_paths = pj(qsci.sourcedir,"release"), pj(qt4_.installdir, "qsci"), \
                             qsci.sourcedir, pj(pyqt.install_site_dir, "PyQt4"), \
                             pyqt.install_sip_dir
        self.qsci_dir = self.install_paths[1]        

    def configure(self):
        # we want pyqscintilla to install itself where pyqt4 installed itself.
        # -- The -S flag is needed or else configure.py
        # sees any existing sip installation and can fail. --
        pyqt = pyqt4()
        config_filename = pj(pyqt.sourcedir,"configure.py")
        cmd = sys.executable + " -S " + config_filename +\
                " -o %s -a %s -n %s -d %s -v %s"%self.install_paths 
        print cmd
        return sh(cmd) == 0