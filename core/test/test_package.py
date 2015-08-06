__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises
import os
import shutil

from openalea.core.node_factory import Factory
from openalea.core.package import UnknownNodeError, Package, UserPackage


# Utility functions
def gen_port_list(size):
    """ Generate a list of port description """
    mylist = []
    for i in range(size):
        mylist.append(dict(name='t' + str(i), interface=None, value=i))
    return mylist

def get_pkg():
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.gforge.inria.fr',
                'icon': ''}

    return Package("Test", metainfo)


def test_package_init():
    pkg = get_pkg()
    assert pkg is not None


def test_package_is_directory():  # TODO: improve test
    pkg = get_pkg()
    assert not pkg.is_directory()


def test_package_get_pkg_files():
    pkg = Package("Test", {}, "pkg")
    files = tuple(pkg.get_pkg_files())

    assert sorted(files) == ["__init__.py", "__wralea__.py", "nodes.py"]


def test_package_reload():
    pkgname = "takatik"
    # create new python package 'pkgname'
    print 1, os.getcwd()
    print os.listdir('.')
    if not os.path.exists(pkgname):
        print 2
        os.mkdir(pkgname)  # TODO: potential troubles here if someone
                          # else uses toto outside

    print 3
    f = open("%s/__init__.py" % pkgname, 'w')
    f.close()

    f = open("%s/test_reload.py" % pkgname, 'w')
    f.write("""# toto

def func():
    return 4
""")
    f.close()

    exec "import %s.test_reload as toto" % pkgname
    assert toto.func() == 4

    # rewrite python module in package
    f = open("%s/test_reload.py" % pkgname, 'w')
    f.write("""# toto

def func():
    return 5
""")
    f.close()

    pkg = Package("Test", {}, pkgname)
    pkg.reload()
    assert toto.func() == 5

    #clean up toto package
    shutil.rmtree(pkgname)


def test_package_get_wralea_path():  # TODO: improve test with non working cases
    pkg = Package("Test", {}, "pkg")

    w_path = os.path.normpath(pkg.get_wralea_path())
    assert w_path == os.path.normpath("pkg/__wralea__.py")


def test_package_get_id():
    pkg = Package("Test", {})

    assert pkg.get_id() == "Test"


def test_package_get_tip():
    pkg = Package("Test", {})
    assert len( pkg.get_tip()) > 0


def test_package_get_metainfo():
    pkg = get_pkg()

    assert pkg.get_metainfo('version') == '0.0.1'
    assert pkg.get_metainfo('dummy') == ""


def test_package_add_factory():
    pkg = get_pkg()
    fac = Factory("toto1")
    pkg.add_factory(fac)

    assert sorted(pkg.get_names()) == ["toto1"]

    assert_raises(KeyError, lambda: pkg.add_factory(fac))
    facb = Factory("toto1")
    assert_raises(KeyError, lambda: pkg.add_factory(facb))

    fac2 = Factory("toto2", alias=["tutu2"])
    pkg.add_factory(fac2)

    assert "toto1" in pkg.get_names()
    assert "toto2" in pkg.get_names()

    assert pkg.get_factory("toto1") == fac
    assert pkg.get_factory("toto2") == fac2
    assert pkg.get_factory("tutu2") == fac2


def test_package_update_factory():
    pkg = get_pkg()
    fac1 = Factory("toto1")
    pkg.add_factory(fac1)
    fac2 = Factory("toto2", alias=["tutu2"])
    pkg.add_factory(fac2)
    fac3 = Factory("toto3")

    pkg.update_factory("toto1", fac3)
    assert "toto1" not in pkg.get_names()
    assert_raises(KeyError, lambda: pkg.update_factory("toto2", fac3))
    assert "toto2" in pkg.get_names()

    pkg.update_factory("toto2", fac1)
    assert "toto1" in pkg.get_names()
    assert "toto2" not in pkg.get_names()
    assert_raises(UnknownNodeError, lambda: pkg.get_factory("tutu2"))


def test_package_get_names():
    pkg = get_pkg()
    for i in range(10):
        fac = Factory("toto%d" % i)
        pkg.add_factory(fac)

    assert sorted(pkg.get_names()) == ["toto%d" % i for i in range(10)]


def test_package_get_factory():
    pkg = get_pkg()
    fac = Factory("toto")
    pkg.add_factory(fac)

    assert pkg.get_factory("toto") == fac
    assert_raises(UnknownNodeError, lambda: pkg.get_factory("tutu"))


# class TestUserPackage():
#     def setUp(self):
#         os.mkdir("tstpkg")
#
#     def tearDown(self):
#         shutil.rmtree("tstpkg")
#
#     def test_case_1(self):
#         metainfo = {'version': '0.0.1',
#                     'license': 'CECILL-C',
#                     'authors': 'OpenAlea Consortium',
#                     'institutes': 'INRIA/CIRAD',
#                     'description': 'Base library.',
#                     'url': 'http://openalea.gforge.inria.fr',
#                     'icon': ''}
#
#         path = os.path.join(os.path.curdir, "tstpkg")
#         mypackage = UserPackage("DummyPkg", metainfo, path)
#
#         factory = mypackage.create_user_node("TestFact",
#                                              "category test",
#                                              "this is a test",
#                                              gen_port_list(3),
#                                              gen_port_list(2))
#         assert path in factory.search_path
#         assert len(factory.inputs) == 3
#         assert len(factory.outputs) == 2
#
#         assert os.path.exists("tstpkg/TestFact.py")
#         execfile("tstpkg/TestFact.py")
#
#         mypackage.write()
#         assert os.path.exists("tstpkg/__wralea__.py")
#         assert os.path.exists("tstpkg/__init__.py")
#         execfile("tstpkg/__wralea__.py")
#
#         # Test_clone_package
#         path = os.path.join(os.path.curdir, "clonepkg")
#         pkg2 = UserPackage("ClonePkg", metainfo, path)
#         print pkg2.wralea_path
#
#
#         # todo this is not working !!
#         from openalea.core.pkgmanager import PackageManager
#         pm = PackageManager()
#         pm.add_wralea_path(path, pm.temporary_wralea_paths)
#         pm.init()
#         pkg2.clone_from_package(mypackage)
#         pkg2.write()
#
#         assert len(pkg2) == 1
#         assert len(pkg2["TestFact"].inputs) == 3
#         assert id(pkg2["TestFact"]) != id(mypackage["TestFact"])
#         assert os.path.exists(path)
#         assert os.path.exists(os.path.join(path, '__wralea__.py'))
#         assert os.path.exists(os.path.join(path, '__init__.py'))
#         assert os.path.exists(os.path.join(path, 'TestFact.py'))
