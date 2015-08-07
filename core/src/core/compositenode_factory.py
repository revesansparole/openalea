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
##############################################################################
""" A CompositeNodeFactory instance is a factory that build CompositeNode
instances. Different instances of the same factory can coexist and can be
modified in a dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import json
import string
import pprint
import copy

from openalea.core.node import RecursionError, Node
from openalea.core.node_factory import AbstractFactory
from openalea.core.pkgmanager import PackageManager, UnknownPackageError
from openalea.core.package import UnknownNodeError
from openalea.core.metadatadict import MetaDataDict
from openalea.core.compositenode import CompositeNode


class CompositeNodeFactory(AbstractFactory):
    """ The CompositeNodeFactory is able to create CompositeNode instances
    Each node has an unique id : the element id (elt_id)
    """

    mimetype = "openalea/compositenodefactory"

    def __init__(self, *args, **kargs):
        """ CompositeNodeFactory accept more optional parameters:

        args:
            - inputs: list of dict(name = '', interface='', value='')
            - outputs: list of dict(name = '', interface='', value='')
            - doc: documentation
            - elt_factory: map of elements with its corresponding factory
            - elt_connections: map of (src_id,output_port):(dst_id , input_port)
            - elt_data: Dictionary containing associated data
            - elt_value: Dictionary containing Lists of 2-uples (port, value)
        """
        # Init parent (name, description, category, doc, node, widget=None)
        AbstractFactory.__init__(self, *args, **kargs)
        # A CompositeNode is composed by a set of element indexed by an elt_id
        # Each element is associated to NodeFactory
        # Each element will generate a node instance in the real CompositeNode

        # Dict mapping elt_id with its corresponding factory
        # the factory is identified by its unique id (package_id, factory_id)
        self.elt_factory = kargs.get("elt_factory", {})

        # Dictionnary which contains tuples describing connection
        # ( source_vid , source_port ) : ( target_vid, target_port )
        self.connections = kargs.get("elt_connections", {})

        self.elt_data = kargs.get("elt_data", {})
        self.elt_value = kargs.get("elt_value", {})
        self.elt_ad_hoc = kargs.get("elt_ad_hoc", {})
        # from openalea.core.algo.dataflow_evaluation import DefaultEvaluation
        # self.eval_algo = kargs.get("eval_algo", DefaultEvaluation.__name__)  # TODO: use "default" instead
        self.eval_algo = kargs.get("eval_algo", "default")

        # Documentation
        self.doc = kargs.get('doc', "")  # TODO: why duplicate
        self.__doc__ = self.doc  # TODO: what for????

    def is_composite_node(self):
        return True

    def get_documentation(self):
        return self.__doc__

    def clear(self):
        """ Clear all elements in composite node"""
        self.elt_factory.clear()
        self.connections.clear()
        self.elt_data.clear()
        self.elt_value.clear()

    def copy(self, **args):  # TODO: use named arguments instead
        """
        Copy factory.

        :param path: new search path
        :param replace_pkg: old and new package names.

        When replace package is set, change the package id for all the
        elt factories.
        """

        ret = AbstractFactory.copy(self, **args)

        # Replace old pkg name to new pkg name
        old_pkg, new_pkg = args['replace_pkg']

        for k, v in ret.elt_factory.iteritems():
            pkg_id, factory_id = v

            if pkg_id == old_pkg.get_id():
                pkg_id = new_pkg.get_id()
                ret.elt_factory[k] = pkg_id, factory_id

        return ret

    def get_writer(self):
        """ Return the writer class """

        return PyCNFactoryWriter(self)

    def instantiate(self, call_stack=None):
        """ Create a CompositeNode instance and allocate all elements
        This function overrides default implementation of NodeFactory

        args:
            - call_stack (list of factory id): a list of node factories
                               already in call stack (in order to avoid
                               infinite recursion)
        """
        if call_stack is None:
            call_stack = []

        # Test for infinite loop
        if self.get_id() in call_stack:
            raise RecursionError()

        call_stack.append(self.get_id())

        new_df = CompositeNode(self.inputs, self.outputs)
        new_df.factory = self
        new_df.__doc__ = self.doc
        new_df.set_caption(self.get_id())
        new_df.eval_algo = self.eval_algo

        cont_eval = set()  # continuous evaluated nodes

        # Instantiate the node with each factory
        for vid in self.elt_factory:
            try:
                node = self.instantiate_node(vid, call_stack)

                # Manage continuous eval
                if node.user_application:
                    cont_eval.add(vid)

            except (UnknownNodeError, UnknownPackageError):
                print "WARNING : The graph is not fully operational "
                print "-> Cannot find '%s:%s'" % self.elt_factory[vid]
                node = self.create_fake_node(vid)
                node.raise_exception = True
                node.notify_listeners(('data_modified', None, None))

            new_df.add_node(node, vid, False)

        # Set IO internal data
        try:  # TODO: GRUUIK remove too broad
            self.load_ad_hoc_data(new_df.node(new_df.id_in),
                                  copy.deepcopy(self.elt_data["__in__"]),
                                  copy.deepcopy(
                                      self.elt_ad_hoc.get("__in__", None)))
            self.load_ad_hoc_data(new_df.node(new_df.id_out),
                                  copy.deepcopy(self.elt_data["__out__"]),
                                  copy.deepcopy(
                                      self.elt_ad_hoc.get("__out__", None)))
        except:
            pass

        # Create the connections
        for eid, link in self.connections.iteritems():
            source_vid, source_port, target_vid, target_port = link

            # Replace id for in and out nodes
            if source_vid == '__in__':
                source_vid = new_df.id_in
            if target_vid == '__out__':
                target_vid = new_df.id_out

            new_df.connect(source_vid, source_port, target_vid, target_port)

        # Set continuous evaluation
        for vid in cont_eval:
            new_df.set_continuous_eval(vid, True)

        # Set call stack to its original state
        call_stack.pop()

        # Properties
        new_df.lazy = self.lazy
        new_df.graph_modified = False  # Graph is not modified

        return new_df

    def create_fake_node(self, vid):
        """ Return an empty node with the correct number of inputs
        and output """

        # Count in and out needed
        ins = 0
        outs = 0

        for eid, link in self.connections.iteritems():
            source_vid, source_port, target_vid, target_port = link

            if source_vid == vid:
                outs = max(outs, source_port)
            elif target_vid == vid:
                ins = max(ins, target_port)

        node = Node()

        attributes = copy.deepcopy(self.elt_data[vid])
        ad_hoc = copy.deepcopy(self.elt_ad_hoc.get(vid, None))
        self.load_ad_hoc_data(node, attributes, ad_hoc)

        # copy node input data if any
        values = copy.deepcopy(self.elt_value.get(vid, ()))

        for p in range(ins + 1):
            node.add_input(name="In" + str(p))

        for p in range(outs + 1):
            node.add_output(name="Out" + str(p))

        for vs in values:
            try:  # TODO: GRUUIK too broad
                # the two first elements are the historical
                # values : port Id and port value
                # beyond that are extensions added by gengraph:
                # the ad_hoc_dict representation is third.
                port, v = vs[:2]
                node.set_input(port, eval(v))
                if len(vs) > 2:
                    d = MetaDataDict(vs[2])
                    node.input_desc[port].get_ad_hoc_dict().update(d)
            except:
                continue

        return node

    def paste(self, cnode, data_modifiers=(), call_stack=None, meta=False):
        """ Add an instantiation of this factory
        into an existing CompositeNode instance.

        args:
            - cnode (CompositeNode): composite node instance
            - data_modifiers (tuple of (str, func)): list of function to
                       apply to node internal data.
            - call_stack (list of factory id): a list of node factories
                               already in call stack (in order to avoid
                               infinite recursion)
            - meta (bool): WTFF???

        return:
            - (list of vid): ids of created nodes
        """
        # map to convert id
        idmap = {}

        # Instantiate the node with each factory
        for vid in self.elt_factory:
            n = self.instantiate_node(vid, call_stack)

            # Apply modifiers (if callable)
            for key, func in data_modifiers:
                try:
                    if callable(func):
                        if meta:
                            func(n)
                        else:
                            n.set_data(key, func(n.get_data(key)))
                    else:
                        n.set_data(key, func)
                except:
                    pass

            idmap[vid] = cnode.add_node(n, None)

        # Create the connections
        for eid, link in self.connections.iteritems():
            source_vid, source_port, target_vid, target_port = link

            # convert id
            source_vid = idmap[source_vid]
            target_vid = idmap[target_vid]

            cnode.connect(source_vid, source_port, target_vid, target_port)

        return idmap.values()

    def load_ad_hoc_data(self, node, elt_data, elt_ad_hoc=None):
        if elt_ad_hoc and len(elt_ad_hoc):
            # reading 0.8+ files.
            d = MetaDataDict(dict=elt_ad_hoc)
            node.get_ad_hoc_dict().update(d)
        else:
            # extracting ad hoc data from old files.
            # we parse the Node class' __ad_hoc_from_old_map__
            # which defines conversions between new ad_hoc_dict keywords
            # and old internal_data keywords.
            # These dictionaries are used to extend ad_hoc_dict of a node with
            # the data that views expect.
            # See node.initialise_standard_metadata() for an example.
            if hasattr(node, "__ad_hoc_from_old_map__"):
                for newKey, oldKeys in node.__ad_hoc_from_old_map__.iteritems():
                    data = []  # list that stores the new values
                    _type, default = node.__ad_hoc_slots__.get(newKey)
                    for key in oldKeys:
                        data.append(elt_data.pop(key, None))
                    if len(data) == 1:
                        data = data[0]
                    if (data is None or
                            (isinstance(data, list) and None in data)):  # ?
                        data = default
                    if data is None:
                        continue
                    node.get_ad_hoc_dict().set_metadata(newKey, _type(data))

        # finally put the internal data (elt_data)
        # where it has always been expected.
        node.update_internal_data(elt_data)

    #        node.internal_data.update(elt_data)

    def instantiate_node(self, vid, call_stack):
        """ Partial instantiation

        instantiate only elt_id in CompositeNode

        :param call_stack: a list of parent id (to avoid infinite recursion)
        """
        package_id, factory_id = self.elt_factory[vid]
        pkgmanager = PackageManager()  # TODO: remove this reference to PackageManager
        pkg = pkgmanager[package_id]
        factory = pkg.get_factory(factory_id)
        node = factory.instantiate(call_stack)

        attributes = copy.deepcopy(self.elt_data[vid])
        ad_hoc = copy.deepcopy(self.elt_ad_hoc.get(vid, None))
        self.load_ad_hoc_data(node, attributes, ad_hoc)

        # copy node input data if any
        values = copy.deepcopy(self.elt_value.get(vid, ()))

        for vs in values:
            try:  # TODO: GRUUIK too broad
                # the two first elements are the historical
                # values : port Id and port value
                # the values beyond are not used.
                port, v = vs[:2]
                node.set_input(port, eval(v))
                d = node.input_desc[port].get_ad_hoc_dict()
                d.set_metadata("hide", node.is_port_hidden(port))
            except:
                continue

        return node

    #########################################################
    # This shouldn't be here, it is related to visual stuff #
    #########################################################
    def instantiate_widget(self, node=None, parent=None,
                           edit=False, autonomous=False):
        """
        Return the corresponding widget initialised with node

        If node is None, the node is allocated else a composite
        widget composed with the node sub widget is returned.

        """
        if edit:
            from openalea.visualea.dataflowview import GraphicalGraph
            return GraphicalGraph(node).create_view(parent)

        if node is None:
            node = self.instantiate()

        from openalea.visualea.compositenode_widget import DisplayGraphWidget
        return DisplayGraphWidget(node, parent, autonomous)


class PyCNFactoryWriter(object):
    """ CompositeNodeFactory python Writer """

    sgfactory_template = """

$NAME = CompositeNodeFactory(name=$PNAME,
                             description=$DESCRIPTION,
                             category=$CATEGORY,
                             doc=$DOC,
                             inputs=$INPUTS,
                             outputs=$OUTPUTS,
                             elt_factory=$ELT_FACTORY,
                             elt_connections=$ELT_CONNECTIONS,
                             elt_data=$ELT_DATA,
                             elt_value=$ELT_VALUE,
                             elt_ad_hoc=$ELT_AD_HOC,
                             lazy=$LAZY,
                             eval_algo=$EVALALGO,
                             )

"""

    def __init__(self, factory):
        self.factory = factory

    def pprint_repr(self, obj, indent=3):
        """ Pretty print repr """
        return pprint.pformat(obj, indent=indent)

    def __repr__(self):
        """ Return the python string representation """

        f = self.factory
        fstr = string.Template(self.sgfactory_template)

        name = f.get_python_name()
        name = name.replace('.', '_')
        result = fstr.safe_substitute(NAME=name,
                                      PNAME=self.pprint_repr(f.name),
                                      DESCRIPTION=self.pprint_repr(
                                          f.description),
                                      CATEGORY=self.pprint_repr(f.category),
                                      DOC=self.pprint_repr(f.doc),
                                      INPUTS=self.pprint_repr(f.inputs),
                                      OUTPUTS=self.pprint_repr(f.outputs),
                                      ELT_FACTORY=self.pprint_repr(
                                          f.elt_factory),
                                      ELT_CONNECTIONS=self.pprint_repr(
                                          f.connections),
                                      ELT_DATA=self.pprint_repr(f.elt_data),
                                      ELT_VALUE=self.pprint_repr(f.elt_value),
                                      ELT_AD_HOC=self.pprint_repr(f.elt_ad_hoc),
                                      LAZY=self.pprint_repr(f.lazy),
                                      EVALALGO=self.pprint_repr(f.eval_algo),
                                      )
        return result


class JSONCNFactoryWriter(PyCNFactoryWriter):
    def __repr__(self):
        f = self.factory

        # minx = min(f.elt_ad_hoc.itervalues(),
        #            key=lambda x: x["position"][0])["position"][0]
        # miny = min(f.elt_ad_hoc.itervalues(),
        #            key=lambda x: x["position"][1])["position"][1]
        minx = min(it["position"][0] for it in f.elt_ad_hoc.itervalues())
        miny = min(it["position"][1] for it in f.elt_ad_hoc.itervalues())

        print minx, miny

        for elt in f.elt_ad_hoc.itervalues():
            elt["position"][0] -= minx
            elt["position"][1] -= miny

        d = dict(type="CompositeNodeFactory",
                 name=f.name,
                 description=f.description,
                 category=f.category,
                 doc=f.doc,
                 # inputs=f.inputs,
                 # outputs=f.outputs,
                 # elt_factory=f.elt_factory,
                 elt_connections=list(f.connections.itervalues()),
                 # elt_data=f.elt_data,
                 # elt_value=f.elt_value,
                 elt_ad_hoc=f.elt_ad_hoc,
                 lazy=f.lazy,
                 eval_algo=f.eval_algo,
                 )
        return json.dumps(d)
