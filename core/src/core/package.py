# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#                       Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
""" This module defines Package classes.

A Package is a deployment unit and contains factories (Node generator)
and meta informations (authors, license, doc...)
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from glob import glob
# import inspect
import os
import sys
import string
import imp
import time
import shutil

from openalea.core.pkgdict import PackageDict, protect
from openalea.core.path import path as _path
from openalea.core.vlab import vlab_object


# from openalea.core import logger

# Exceptions

class UnknownNodeError(Exception):
    def __init__(self, name):
        Exception.__init__(self)
        self.message = "Cannot find node : %s" % name  # TODO: useless, use pass instead

    def __str__(self):
        return self.message


class FactoryExistsError(Exception):
    pass


# class DynamicPackage(PackageDict):
#     """
#     Package for dynamical parsing of python file
#     """
#
#     def __init__(self, name, metainfo):
#         PackageDict.__init__(self)
#         self.metainfo = metainfo
#         self.name = name


class Package(PackageDict):
    """ A Package is a dictionary of node factories.

    Meta information are associated with a package.
    """

    # information type for drag and drop.
    mimetype = "openalea/package"

    def __init__(self, name, metainfo, pth=None):
        """ Create a Package.

        Attended keys for the metainfo are:
            - license: a string ex GPL, LGPL, Cecill, Cecill-C
            - version: a string
            - authors: a string
            - institutes: a string
            - url: a string
            - description: a string for the package description
            - publication: optional string for publications

        args:
            - name (str): used as a unique identifier for the package
                          case sensitive
            - metainfo (dict):
            - pth (str): path where the package lies: either a directory
                          or a full wralea path
        """
        PackageDict.__init__(self)

        self.name = name
        self.metainfo = metainfo

        # package directory

        if pth is None:  # TODO: usefull???
            # package directory
            import inspect
            # get the path of the file which call this function
            call_path = os.path.abspath(inspect.stack()[1][1])
            self.path = os.path.dirname(call_path)
            self.wralea_path = call_path

        # wralea.py path is specified
        else:
            if not os.path.exists(pth):  # TODO: potential trouble if pth is wralea pth
                os.mkdir(pth)

            if os.path.isdir(pth):
                self.path = pth
                self.wralea_path = os.path.join(pth, "__wralea__.py")
            else:
                self.path = os.path.dirname(pth)
                self.wralea_path = pth

                # wralea_name = name.replace('.', '_')

    def is_directory(self):
        """
        New style package.
        A package is embedded in a unique directory.
        This directory can not contain more than one package.
        Thus, you can move, copy or delete a package by acting
        on the directory without ambiguity.

        Return True if the package is embedded in a directory.
        """
        return self.wralea_path.endswith("__wralea__.py")

    def is_editable(self):
        """
        A convention (for the GUI) to ensure that the user
        can modify the package.
        """
        return False

    def get_pkg_files(self):
        """ Iterate over the names of python files in the package.
        These file names are relative to self.path

        return:
            - (list of str)
        """
        for src in glob(os.path.join(self.path, "*.py")):
            name = os.path.basename(src)
            if not name.startswith("."):
                yield name

        # assert self.is_directory()

        # ret = []
        # for name in os.listdir(self.path):
        #     src = os.path.join(self.path, name)
        #     if (os.path.isfile(src) and
        #             not name.endswith(".pyc") and
        #             not name.startswith(".")):
        #         ret.append(name)
        #
        # return ret

    def remove_files(self):
        """ Remove pkg files """
        raise NotImplementedError()

    def reload(self):
        """ Reload all python files of the package.
        """
        sources = set([os.path.abspath(os.path.join(self.path, src))
                      for src in self.get_pkg_files()])
        # sources = self.get_pkg_files()
        #
        # s = set()  # set of full path name
        # for f in sources:
        #     if f.endswith('.py'):
        #         f += 'c'
        #
        #     s.add(os.path.abspath(os.path.join(self.path, f)))

        for module in sys.modules.values():
            if module is not None:
                try:
                    module_file = os.path.abspath(module.__file__)
                    if module_file in sources:
                        if os.path.exists(module_file + "c"):
                            os.remove(module_file + "c")

                        module.oa_invalidate = True
                        reload(module)
                        print "Reloaded ", module.__name__
                except AttributeError:  # module is builtin
                    pass

    def get_wralea_path(self):
        """ Return the full path of the __wralea__.py.

         Path must have been set before.
         """
        return self.wralea_path

    def get_id(self):
        """ Return the package id.
        """
        return self.name

    def get_tip(self):
        """ Return the package description.
        """

        txt = "<b>Package:</b>%s<br/>\n" % (self.name,)
        try:
            txt += "<b>Description : </b>%s<br/>\n" % (
                self.metainfo['description'].replace('\n', '<br/>'),)
        except KeyError:
            pass
        try:
            txt += "<b>Authors :</b> %s<br/>\n" % (self.metainfo['authors'],)
        except KeyError:
            pass
        try:
            txt += "<b>Institutes :</b> %s<br/>\n" % (
                self.metainfo['institutes'],)
        except KeyError:
            pass

        try:
            txt += "<b>URL : </b>%s<br/>\n" % (self.metainfo['url'],)
        except KeyError:
            pass

        return txt

    def get_metainfo(self, key):
        """ Return a meta information.

        See the standard key in the __init__ function documentation.

        args:
            - key (str)

        return:
            - value (any) associated with the key if it exists
            - "" otherwise
        """
        return self.metainfo.get(key, "")

    def add_factory(self, factory):
        """ Add a factory in the package.

        args:
            - factory (Factory)
        """

        if factory.name in self:
            msg = "Factory %s already defined. Ignored !" % factory.name
            raise KeyError(msg)

        self[factory.name] = factory
        factory.package = self

        # Check validity  # TODO: GRUUIK
        # oops: this is a hack.
        # When the factory is a data factory that do not reference a file
        # raise an error.
        # This function return True or raise an error to have a specific
        # diagnostic.
        # try:  # TODO: removed this GRUUIK part
        #     factory.is_valid()
        # except Exception, e:
        #     factory.package = None
        #     del (self[factory.name])
        #     raise e

        # Add Aliases
        if factory.alias is not None:
            for a in factory.alias:
                self[protect(a)] = factory

    def update_factory(self, old_name, factory):
        """ Change the name of a factory.

        args:
            - old_name (str): name previously used by the factory
            - factory (Factory): new factory to use instead
        """
        if factory.name in self:
            msg = "Factory %s already defined. Ignored !" % factory.name
            raise KeyError(msg)

        old_fac = self.get_factory(old_name)
        print self.keys()
        if old_fac.alias is not None:  # TODO: to remove
            for name in old_fac.alias:
                del self[protect(name)]

        del self[old_name]

        self.add_factory(factory)

    def get_names(self):
        """ Return all the factory registered in the package.

        return:
            - (list of str): list of factory names.
        """
        return self.keys()

    def get_factory(self, name):
        """ Return the factory associated with a name.

        args:
            - name (str): unique identifier for a factory
        """

        try:
            return self[name]
        except KeyError:
            raise UnknownNodeError("%s.%s" % (self.name, name))


class UserPackage(Package):  # TODO: bof, a way to get rid of write
    """ Package user editable and persistent.
    """

    def __init__(self, name, metainfo, path=None):
        """ Create a Package.

        Attended keys for the metainfo are:
            - license: a string ex GPL, LGPL, Cecill, Cecill-C
            - version: a string
            - authors: a string
            - institutes: a string
            - url: a string
            - description: a string for the package description
            - publication: optional string for publications

        args:
            - name (str): used as a unique identifier for the package
            - metainfo (dict):
            - path (str): path where the package lies: either a directory
                          or a full wralea path
        """
        if path is None:
            import inspect
            # get the path of the file which call this function
            path = os.path.abspath(inspect.stack()[1][1])

        Package.__init__(self, name, metainfo, path)

    def is_editable(self):
        return True

    def remove_files(self):
        """ Remove pkg files.
        """
        assert self.is_directory()

        self.clear()
        shutil.rmtree(self.path, ignore_errors=True)  # TODO: GRUUIK

    def clone_from_package(self, pkg):
        """ Copy the contents of pkg in self.

        args:
            - pkg (Package): another package to copy
        """
        assert self.is_directory()

        # Copy icon
        if 'icon' not in self.metainfo or self.metainfo['icon'] is None:
            self.metainfo['icon'] = pkg.metainfo['icon']

        # Copy files
        sources = pkg.get_pkg_files()

        for name in sources:
            src = os.path.join(pkg.path, name)
            dst = os.path.join(self.path, name)
            shutil.copyfile(src, dst)

        # Copy deeply all the factory
        for k, v in pkg.iteritems():
            self[k] = v.copy(replace_pkg=(pkg, self),
                             path=self.path)

            # self.update(copy.deepcopy(pkg))

        self.write()

    def write(self):
        """ Write the package into a wralea file.
        """
        writer = PyPackageWriter(self)

        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        print "Writing", self.wralea_path

        writer.write_wralea(self.wralea_path)

        # create a __init__.py if necessary
        init_path = os.path.join(self.path, '__init__.py')

        if not os.path.exists(init_path):
            f = open(init_path, 'w')
            f.close()

    # Convenience function  # TODO: external file

    def create_user_node(self, name, category, description,
                         inputs, outputs):
        """
        Return a new user node factory
        This function create a new python module in the package directory
        The factory is added to the package
        and the package is saved.
        """

        if name in self:
            raise FactoryExistsError()

        localdir = self.path
        classname = name.replace(' ', '_')

        # build function parameters
        ins = []
        in_names = []
        for input in inputs:
            in_name = input['name'].replace(' ', '_').lower()
            in_names.append(in_name)
            in_value = input['value']
            if in_value is not None:
                arg = '%s=%s' % (in_name, repr(in_value))
            else:
                arg = '%s' % (in_name,)
            ins.append(arg)
        in_args = ', '.join(ins)

        # build output
        out_values = ""
        return_values = []
        for output in outputs:
            arg = output['name'].replace(' ', '_').lower()
            # if an input arg is equal to an output one,
            # change its name.
            while arg in in_names:
                arg = 'out_' + arg
            out_values += '%s = None; ' % (arg,)
            return_values.append('%s' % (arg,))

        if return_values:
            return_values = ', '.join(return_values) + ','
        # Create the module file
        my_template = """
def %s(%s):
    '''
    %s
    '''
    %s
    # write the node code here.

    # return outputs
    return %s
""" % (classname, in_args, description, out_values, return_values)

        module_path = os.path.join(localdir, "%s.py" % classname)

        f = open(module_path, 'w')
        f.write(my_template)
        f.close()

        from openalea.core.node_factory import NodeFactory

        factory = NodeFactory(name=name,
                              category=category,
                              description=description,
                              inputs=inputs,
                              outputs=outputs,
                              nodemodule=classname,
                              nodeclass=classname,
                              authors='',
                              search_path=[localdir])

        self.add_factory(factory)
        self.write()

        return factory

    # Convenience function  # TODO: external file to avoid circular dependencies
    def create_user_compositenode(self, name, category, description,
                                  inputs, outputs):
        """
        Add a new user composite node factory to the package
        and save the package.
        Returns the cn factory.
        """
        # Avoid cyclic import:
        # composite node factory import package...
        from compositenode import CompositeNodeFactory

        newfactory = CompositeNodeFactory(name=name,
                                          description=description,
                                          category=category,
                                          inputs=inputs,
                                          outputs=outputs,
                                          )
        self.add_factory(newfactory)
        self.write()

        return newfactory

    def add_data_file(self, filename, description=''):  # TODO: external file
        """ Add a file in the package.

        Copy file in the directory

        args:
            - filename (str): valid path of actual location of the data
            - description (str): optional description of the data
        """
        from openalea.core.data import DataFactory

        bname = os.path.basename(filename)
        src = os.path.abspath(filename)
        dst = os.path.join(self.path, bname)

        try:
            if src != dst:
                shutil.copyfile(src, dst)
        except shutil.Error:
            if not os.path.exists(dst):  # TODO: GRUUIK
                f = open(dst, 'w')
                f.close()

        newfactory = DataFactory(bname, description)

        self.add_factory(newfactory)
        self.write()

        return newfactory

    def set_icon(self, filename):
        """ Set package icon

        Copy filename in the package dir.

        args:
            - filename (str): valid current path of the icon.
        """

        bname = os.path.basename(filename)
        src = os.path.abspath(filename)
        dst = os.path.join(self.path, bname)

        # try:  # TODO: avoid try catch
        if src != dst:
            shutil.copyfile(src, dst)
        self.metainfo['icon'] = bname
        self.write()
        # except IOError:
        #     pass

    # def add_factory(self, factory):
    #     """ Write change on disk """
    #
    #     Package.add_factory(self, factory)

    # def __delitem__(self, key):
    #     """ Write change on disk """
    #
    #     Package.__delitem__(self, key)
    #     # self.write()


class AbstractPackageReader(object):
    """ Abstract class for package readers.

    A package reader takes a stream, parse it into a
    package description and add the package in the package manager.
    """
    def __init__(self, filename):
        """
        Build a package from a specification file.
        filename may be a __wralea__.py file for instance.
        """
        self.filename = filename

    def register_packages(self, pkgmanager):
        """ Create and add a package in the package manager.
        """
        raise NotImplementedError()


class PyPackageReader(AbstractPackageReader):
    """ Build packages from wralea file.

    Use 'register_package' function
    """

    def filename_to_module(self, filename):
        """ Transform a filename ending with .py to the module name.
        """
        start_index = 0
        end_index = len(filename)

        # delete the .py at the end
        if filename.endswith('.py'):
            end_index = -3
        # Windows case (e.g. C:/...)
        if filename[1] == ':':
            start_index = 2

        modulename = filename[start_index:end_index]

        return modulename.replace(os.path.sep, '.')

    def get_pkg_name(self):
        """ Return the OpenAlea (unique) full package name.
        """
        m = self.filename_to_module(self.filename)
        return m.replace(".", "_")

    def register_packages(self, pkgmanager):
        """ Execute Wralea.py """

        pkg = None

        basename = os.path.basename(self.filename)
        basedir = os.path.abspath(os.path.dirname(self.filename))

        modulename = self.get_pkg_name()
        base_modulename = self.filename_to_module(basename)

        # Adapt sys.path
        sys.path.append(basedir)

        if modulename in sys.modules:
            del sys.modules[modulename]

        f, pathname, desc = imp.find_module(base_modulename, [basedir])
        # try:  # TODO: removed broad try
        wraleamodule = imp.load_module(modulename, f, pathname, desc)
        pkg = self.build_package(wraleamodule, pkgmanager)

        # except Exception, e:
        #     try:
        #         pkgmanager.log.add('%s is invalid : %s' % (self.filename, e))
        #     except Exception, e:
        #         print '%s is invalid : %s' % (self.filename, e)
        #         pass
        #
        # except:  # Treat all exception
        #     pkgmanager.add('%s is invalid :' % (self.filename,))

        if not f.closed:
            f.close()

        # Recover sys.path
        sys.path.pop()

        return pkg

    def build_package(self, wraleamodule, pkgmanager):
        """ Build package and update pkgmanager """

        try:
            wraleamodule.register_packages(pkgmanager)

        except AttributeError:
            # compatibility issue between two types of reader
            reader = PyPackageReaderWralea(self.filename)
            reader.build_package(wraleamodule, pkgmanager)


class PyPackageReaderWralea(PyPackageReader):
    """ Build a package from  a __wralea__.py

    Use module variable
    """

    def build_package(self, wraleamodule, pkgmanager):
        """ Build package and update pkgmanager """

        name = wraleamodule.__dict__.get('__name__', None)
        edit = wraleamodule.__dict__.get('__editable__', False)

        # Build Metainfo
        metainfo = dict(
            version='',
            license='',
            authors='',
            institutes='',
            description='',
            url='',
            icon='',
            alias=[], )

        for k, v in wraleamodule.__dict__.iteritems():
            if k.startswith('__') and k.endswith('__'):
                k = k[2:-2]

                if k in metainfo:  # update value
                    metainfo[k] = v

            # if not (k.startswith('__') and k.endswith('__')):
            #     continue
            # k = k[2:-2]  # remove __
            # if k not in metainfo:
            #     continue
            # metainfo[k] = v

        # Build Package
        path = wraleamodule.__file__
        if path.endswith('.pyc'):
            path = path.replace('.pyc', '.py')

        if edit:
            p = UserPackage(name, metainfo, path)
        else:
            p = Package(name, metainfo, path)

        # Add factories
        factories = wraleamodule.__dict__.get('__all__', [])
        for fname in factories:
            f = wraleamodule.__dict__.get(fname, None)
            # try:  # TODO: removed broad try
            if f is not None:
                p.add_factory(f)
            # except Exception, e:
            #     pkgmanager.log.add(str(e))

        pkgmanager.add_package(p)

        # Add Package Aliases
        palias = wraleamodule.__dict__.get('__alias__', [])
        for name in palias:
            if protect(name) in pkgmanager:
                alias_pkg = pkgmanager[protect(name)]
                for fname, factory in p.iteritems():
                    pkg_name = alias_pkg.name + '.' + fname
                    if fname not in alias_pkg and pkg_name not in pkgmanager:
                        alias_pkg[fname] = factory
            else:
                pkgmanager[protect(name)] = p


class PyPackageReaderVlab(AbstractPackageReader):
    """
    Build a package from  a vlab specification file.
    """

    def register_packages(self, pkgmanager):
        raise DeprecationWarning()
        # """ Create and add a package in the package manager. """
        # fn = _path(self.filename).abspath()
        # pkg_path = fn.dirname()
        #
        # spec_file = fn.basename()
        # assert 'specification' in spec_file
        #
        # vlab_package = vlab_object(pkg_path, pkgmanager)
        # pkg = vlab_package.get_package()
        # pkgmanager.add_package(pkg)


# TODO
class PyPackageWriter(object):
    """ Write a wralea python file """

    wralea_template = """
# This file has been generated at $TIME

from openalea.core import *

$PKG_DECLARATION

"""

    pkg_template = """
$PKGNAME

$METAINFO

$ALL

$FACTORY_DECLARATION
"""

    def __init__(self, package):
        """ Package to write """

        self.package = package

    def get_factories_str(self):
        """ Return a dict of (name:repr) of all factory"""

        # generate code for each factory
        result_str = {}
        for f in self.package.values():
            writer = f.get_writer()
            if writer:
                name = f.get_python_name()
                result_str[name] = str(writer)

        return result_str

    def __repr__(self):
        """ Return a string with the package declaration """

        fdict = self.get_factories_str()

        keys = fdict.keys()

        fstr = '\n'.join(fdict.values())

        pstr = string.Template(self.pkg_template)

        editable = isinstance(self.package, UserPackage)

        metainfo = '__editable__ = %s\n' % (repr(editable))

        for (k, v) in self.package.metainfo.iteritems():
            key = "__%s__" % k
            val = repr(v)
            metainfo += "%s = %s\n" % (key, val)

        result = pstr.safe_substitute(
            PKGNAME="__name__ = %s" % (repr(self.package.name)),
            METAINFO=metainfo,
            ALL="__all__ = %s" % repr(keys),
            FACTORY_DECLARATION=fstr,
        )

        return result

    def get_str(self):
        """ Return string to write """

        pstr = repr(self)
        wtpl = string.Template(self.wralea_template)

        result = wtpl.safe_substitute(
            TIME=time.ctime(),
            PKG_DECLARATION=pstr)

        return result

    def write_wralea(self, full_filename):
        """ Write the wralea.py in the specified filename """

        try:
            result = self.get_str()
        except Exception, e:
            print e
            print "FILE HAS NOT BEEN SAVED !!"
            return

        handler = open(full_filename, 'w')
        handler.write(result)
        handler.close()

        # Recompile
        import py_compile
        py_compile.compile(full_filename)
