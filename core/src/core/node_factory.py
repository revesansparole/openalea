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
""" A Factory build Node from its description. Factories instantiate
Nodes on demand for the dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


import inspect
import os
import sys
import types
from weakref import ref

from openalea.core.node import AbstractNode, FuncNode
from openalea.core.observer import Observed
from openalea.core import signature as sgn


class AbstractFactory(Observed):
    """ Abstract Factory is Factory base class.
    """

    mimetype = "openalea/nodefactory"

    def __init__(self,
                 name,
                 description='',
                 category='',
                 inputs=(),
                 outputs=(),
                 lazy=True,
                 delay=0,
                 view=None,
                 alias=None,
                 authors=None,
                 **kargs):
        """
        Create a factory.

        :param name: user name for the node (must be unique) (String)
        :param description: description of the node (String)
        :param category: category of the node (String)
        :param inputs: inputs description
        :param outputs: outputs description, value=0
        :param lazy: enable lazy evaluation (default = False)
        :param view: custom view (default = None)
        :param alias: list of alias name
        :param authors: authors of the node. If Node, it should be replaced by the package authors.

        .. note:: inputs and outputs parameters are list of dictionnary such

        inputs = (dict(name='x', interface=IInt, value=0,)
        outputs = (dict(name='y', interface=IInt)
        """
        Observed.__init__(self)

        # Factory info
        self.name = name
        self.description = description
        self.category = category

        self.__pkg__ = None
        self.__pkg_id__ = None

        self.inputs = inputs
        self.outputs = outputs

        self.lazy = lazy
        self.view = view
        self.delay = delay
        self.alias = alias
        self.authors = authors
    # Package property

    def set_pkg(self, port):
        """
        An openalea package contains factories.
        The factory has a link to this package (weakref).
        The package id is the name of the package when the package is the
        Python object.
        """
        if(not port):
            self.__pkg__ = None
            self.__pkg_id = None
        else:
            self.__pkg__ = ref(port)
            self.__pkg_id__ = port.get_id()

        return port

    def get_pkg(self):
        """todo"""
        if(self.__pkg__):
            port = self.__pkg__()
        else:
            port = None
        # Test if pkg has been reloaded
        # In this case the weakref is not valid anymore
        if(not port and self.__pkg_id__):
            from openalea.core.pkgmanager import PackageManager
            port = self.set_pkg(PackageManager()[self.__pkg_id__])
        return port

    package = property(get_pkg, set_pkg)

    def is_valid(self):
        """
        Return True if the factory is valid
        else raise an exception
        """
        return True

    def get_id(self):
        """ Returns the node factory Id """
        return self.name

    def get_documentation(self):
        return ""

    def get_python_name(self):
        """
        Returns a valid python variable as name.
        This is used to store the factory into a python list (i.e. __all__).
        """

        name = self.name

        if(not name.isalnum()):
            name = '_%s' % (id(self))
        return name

    def get_authors(self):
        """returns node authors

        if no authors is found within the node, then it takes the authors field
        found in its package.
        """
        if self.authors == None or self.authors == '':
            authors = self.package.metainfo['authors'] + ' (wralea authors)'
        else:
            authors = self.authors
        return authors

    def get_tip(self, asRst=False):
        """ Return the node description

        if no authors is found within the node, then it takes the authors field
        found in its package.
        """


        if not asRst:
            return "<b>Name:</b> %s<br/>" % (self.name,) + \
                   "<b>Category:</b> %s<br/>" % (self.category,) + \
                   "<b>Package:</b> %s<br/>" % (self.package.name,) + \
                   "<b>Authors:</b> %s<br/>" % (self.get_authors(),) + \
                   "<b>Description:</b> %s<br/>" % (self.description,)
        else:
            return "**Name:** %s\n\n" % (self.name,) + \
                   "**Category:** %s\n\n" % (self.category,) + \
                   "**Package:** %s\n\n" % (self.package.name,) + \
                   "**Authors:** %s\n\n" % (self.get_authors(),) + \
                   "**Description:** %s\n\n" % (self.description,)

    def instantiate(self, call_stack=[]):
        """ Return a node instance

        :param call_stack: the list of NodeFactory id already in call stack
            (in order to avoir infinite recursion)
        """
        raise NotImplementedError()

    def instantiate_widget(self, node=None, parent=None, edit=False,
        autonomous=False):
        """ Return the corresponding widget initialised with node"""
        raise NotImplementedError()

    def get_writer(self):
        """ Return the writer class """
        raise NotImplementedError()

    def copy(self, **args):
        """ Copy factory """

        # Disable package before copy
        pkg = self.package
        self.package = None

        ret = deepcopy(self)
        self.packageg = pkg

        old_pkg, new_pkg = args['replace_pkg']

        ret.package = new_pkg
        return ret

    def clean_files(self):
        """ Remove files depending of factory """
        pass

    def is_data(self):
        return False

    def is_node(self):
        return False

    def is_composite_node(self):
        return False

    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        odict['__pkg__'] = None # remove weakref reference
        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.get_pkg()


def Alias(factory, name):
    """ Create an alias for factory.
    """
    if(factory.alias is None):
        factory.alias = [name]
    else:
        factory.alias.append(name)


class NodeFactory(AbstractFactory):
    """ A Node factory is able to create nodes on demand,
    and their associated widgets.
    """

    def __init__(self,
                 name,
                 description='',
                 category='',
                 inputs=None,
                 outputs=None,
                 nodemodule='',
                 nodeclass=None,
                 widgetmodule=None,
                 widgetclass=None,
                 search_path=None,
                 authors=None,
                 **kargs):
        """Create a node factory.

        :param name: user name for the node (must be unique) (String)
        :param description: description of the node (String)
        :param category: category of the node (String)
        :param inputs: inputs description
        :param outputs: outputs description
        :param nodemodule: python module to import for node (String)
        :param nodeclass:  node class name to be created (String)
        :param widgetmodule: python module to import for widget (String)
        :param widgetclass: widget class name (String)
        :param search_path: list of directories where to search for
            module

        :note: inputs and outputs parameters are list of dictionnary such

        inputs = (dict(name='x', interface=IInt, value=0,)
        outputs = (dict(name='y', interface=IInt)
        """
        AbstractFactory.__init__(self, name, description, category,
                                 inputs, outputs, authors=authors, **kargs)

        # Factory info
        self.nodemodule_name = nodemodule
        self.nodeclass_name = nodeclass
        self.widgetmodule_name = widgetmodule
        self.widgetclass_name = widgetclass

        self.toscriptclass_name = kargs.get("toscriptclass_name", None)

        # Cache
        self.nodeclass = None
        self.src_cache = None

        # Module path, value=0
        self.nodemodule_path = None
        if(not search_path):
            self.search_path = []
        else:
            self.search_path = search_path

        self.module_cache = None

        # Context directory
        # inspect.stack()[1][1] is the caller python module
        caller_dir = os.path.dirname(os.path.abspath(inspect.stack()[1][1]))
        if(not caller_dir in self.search_path):
            self.search_path.append(caller_dir)


    def is_node(self):
        return True

    def get_python_name(self):
        """ Return a python valid name """

        module_name = self.nodemodule_name
        module_name = module_name.replace('.','_')
        return "%s_%s" % (self.nodemodule_name, self.nodeclass_name)

    def __getstate__(self):
        """ Pickle function """
        odict = self.__dict__.copy()
        odict['nodemodule_path'] = None
        odict['nodemodule'] = None
        odict['nodeclass'] = None
        odict['module_cache'] = None
        odict['__pkg__'] = None # remove weakref reference

        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.get_pkg()

    def copy(self, **args):
        """ Copy factory
        :param path: new search path
        """

        ret = AbstractFactory.copy(self, **args)
        ret.search_path = [args['path']]
        return ret

    def get_classobj(self):
        module = self.get_node_module()
        classobj = module.__dict__.get(self.nodeclass_name, None)
        return classobj

    def get_documentation(self):
        return self.get_classobj().__doc__

    def instantiate(self, call_stack=[]):
        """
        Returns a node instance.
        :param call_stack: the list of NodeFactory id already in call stack
        (in order to avoir infinite recursion)
        """

        # The module contains the node implementation.
        module = self.get_node_module()
        classobj = module.__dict__.get(self.nodeclass_name, None)

        if classobj is None:
            raise Exception("Cannot instantiate '" + \
                self.nodeclass_name + "' from " + str(module))

        # If class is not a Node, embed object in a Node class
        if(not hasattr(classobj, 'mro') or not AbstractNode in classobj.mro()):

            # Check inputs and outputs
            if(self.inputs is None):
                sign = sgn.Signature(classobj)
                self.inputs = sign.get_parameters()
            if(self.outputs is None):
                self.outputs = (dict(name="out", interface=None),)


            # Check and Instantiate if we have a functor class
            if((type(classobj) == types.TypeType)
               or (type(classobj) == types.ClassType)):

                _classobj = classobj()
                if callable(_classobj):
                    classobj = _classobj

            node = FuncNode(self.inputs, self.outputs, classobj)

        # Class inherits from Node
        else:
            try:
                node = classobj(self.inputs, self.outputs)
            except TypeError, e:
                node = classobj()

        # Properties
        try:
            node.factory = self
            node.lazy = self.lazy
            if(not node.caption):
                node.set_caption(self.name)

            node.delay = self.delay
        except:
            pass

        # to script
        if self.toscriptclass_name is not None :
            node._to_script_func = module.__dict__.get(self.toscriptclass_name, None)

        return node

    def instantiate_widget(self, node=None, parent=None,
                            edit=False, autonomous=False):
        """ Return the corresponding widget initialised with node """

        # Code Editor
        if(edit):
            from openalea.visualea.code_editor import get_editor
            w = get_editor()(parent)
            try:
                w.edit_module(self.get_node_module(), self.nodeclass_name)
            except Exception, e:
                # Unable to load the module
                # Try to retrieve the file and open the file in an editor
                src_path = self.get_node_file()
                print "instantiate widget exception:", e
                if src_path:
                    w.edit_file(src_path)
            return w

        # Node Widget
        if(node == None):
            node = self.instantiate()

        modulename = self.widgetmodule_name
        if(not modulename):
            modulename = self.nodemodule_name

        # if no widget declared, we create a default one
        if(not modulename or not self.widgetclass_name):

            from openalea.visualea.node_widget import DefaultNodeWidget
            return DefaultNodeWidget(node, parent, autonomous)

        else:
            # load module
            (file, pathname, desc) = imp.find_module(modulename,
                self.search_path + sys.path)

            sys.path.append(os.path.dirname(pathname))
            module = imp.load_module(modulename, file, pathname, desc)
            sys.path.pop()

            if(file):
                file.close()

            widgetclass = module.__dict__[self.widgetclass_name]
            return widgetclass(node, parent)

    def get_writer(self):
        """ Return the writer class """

        return PyNodeFactoryWriter(self)

    def get_node_module(self):
        """
        Return the python module object (if available)
        Raise an Import Error if no module is associated
        """
        LOCAL_IMPORT = False

        if not self.nodemodule_name:
            self.nodemodule_name = '__builtin__'

        # Test if the module is already in sys.modules
        if (self.nodemodule_path and
            self.module_cache and
            not hasattr(self.module_cache, 'oa_invalidate')):
            return self.module_cache

        sav_path = sys.path
        sys.path = self.search_path + sav_path
        # print 'SEARCH PATH ', self.search_path
        try:
            # load module

            # Delete the module from the sys.modules if another local exists and
            # has the same name
            if LOCAL_IMPORT:
                if self.nodemodule_name in sys.modules:
                    del sys.modules[self.nodemodule_name]
            __import__(self.nodemodule_name)
            nodemodule = sys.modules[self.nodemodule_name]
            try:
                self.nodemodule_path = inspect.getsourcefile(nodemodule)
            except TypeError, type_error:
                self.nodemodule_path = None
                print type_error

            self.module_cache = nodemodule
            sys.path = sav_path
            return nodemodule

        except ImportError, import_error:
            sys.path = sav_path
            print self.nodemodule_name
            raise import_error
        else:
            sys.path = sav_path

    def get_node_file(self):
        """
        Return the path of the python module.

        """

        if self.nodemodule_path or self.module_cache:
            return self.nodemodule_path
        elif self.nodemodule_name:
            self.get_node_module()
            return self.nodemodule_path


    def get_node_src(self, cache=True):
        """
        Return a string containing the node src
        Return None if src is not available
        If cache is False, return the source on the disk
        """

        # Return cached source if any
        if(self.src_cache and cache):
            return self.src_cache

        module = self.get_node_module()

        import linecache
        # get the code
        linecache.checkcache(self.nodemodule_path)
        cl = module.__dict__[self.nodeclass_name]
        return inspect.getsource(cl)

    def apply_new_src(self, newsrc):
        """
        Execute new src and store the source into the factory.
        """
        module = self.get_node_module()

        # Run src
        exec newsrc in module.__dict__

        # save the current newsrc
        self.src_cache = newsrc

    def save_new_src(self, newsrc):
        """
        Execute the new source and replace the text into the old file
        containing the source.
        """
        module = self.get_node_module()
        nodesrc = self.get_node_src(cache=False)

        # Run src
        exec newsrc in module.__dict__

        # get the module code
        import inspect
        modulesrc = inspect.getsource(module)

        # Pass if no modications
        if(nodesrc == newsrc):
            return

        # replace old code with new one
        modulesrc = modulesrc.replace(nodesrc, newsrc)


        # write file
        myfile = open(self.nodemodule_path, 'w')
        myfile.write(modulesrc)
        myfile.close()

        # reload module
        if(self.module_cache):
            self.module_cache.invalidate_oa = True

        self.src_cache = None
        m = self.get_node_module()
        # reload(m)
        # Recompile
        # import py_compile
        # py_compile.compile(self.nodemodule_path)


# Class Factory:
Factory = NodeFactory


class PyNodeFactoryWriter(object):
    """ NodeFactory python Writer """

    nodefactory_template = """

$NAME = Factory(name=$PNAME,
                authors=$AUTHORS,
                description=$DESCRIPTION,
                category=$CATEGORY,
                nodemodule=$NODEMODULE,
                nodeclass=$NODECLASS,
                inputs=$LISTIN,
                outputs=$LISTOUT,
                widgetmodule=$WIDGETMODULE,
                widgetclass=$WIDGETCLASS,
               )

"""

    def __init__(self, factory):
        self.factory = factory

    def __repr__(self):
        """ Return the python string representation """
        f = self.factory
        fstr = string.Template(self.nodefactory_template)
        
        name = f.get_python_name()
        name = name.replace('.', '_')
        result = fstr.safe_substitute(NAME=name,
                                      AUTHORS=repr(f.get_authors()),
                                      PNAME=repr(f.name),
                                      DESCRIPTION=repr(f.description),
                                      CATEGORY=repr(f.category),
                                      NODEMODULE=repr(f.nodemodule_name),
                                      NODECLASS=repr(f.nodeclass_name),
                                      LISTIN=repr(f.inputs),
                                      LISTOUT=repr(f.outputs),
                                      WIDGETMODULE=repr(f.widgetmodule_name),
                                      WIDGETCLASS=repr(f.widgetclass_name),)
        return result

# Utility functions
def gen_port_list(size):
    """ Generate a list of port description """
    mylist = []
    for i in range(size):
        mylist.append(dict(name='t' + str(i), interface=None, value=i))
    return mylist
