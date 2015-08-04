# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
"""Node and NodeFactory classes.

A Node is generalized functor which is embeded in a dataflow.
A Factory build Node from its description. Factories instantiate
Nodes on demand for the dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import imp
import inspect
import os
import sys
import string
import types
from copy import copy, deepcopy
from weakref import ref, proxy

# from signature import get_parameters
import signature as sgn
from observer import Observed, AbstractListener
from actor import IActor
from metadatadict import MetaDataDict, HasAdHoc
from interface import TypeNameInterfaceMap
from openalea.core.node_port import InputPort, OutputPort

# Exceptions
class RecursionError (Exception):
    """todo"""
    pass


class InstantiationError(Exception):
    """todo"""
    pass


########################
# Node related classes #
########################
class AbstractNode(Observed, HasAdHoc):
    """
    An AbstractNode is the atomic entity in a dataflow.

    internal_data contains properties specified by users.
    They can be extended and the number is not fixed.
    We use a dict to distinguish these public properties to the others
    which are used for protected management.

    .. todo::
        - rename internal_data into attributes.
    """

    mimetype = "openalea/node"

    def __init__(self):
        """
        Default Constructor
        Create Internal Data dictionnary
        """
        HasAdHoc.__init__(self)
        Observed.__init__(self)

        self.__id = None
        # Internal Data (caption...)
        self.internal_data = {}
        self.factory = None

        # -- the ugly back reference --
        # !! Christophe, don't look at this one.
        # proxy to higher level structure, aka CompositeNode.
        # This is currently only used by the "wrap_method" node
        # that needs to modify the topology of the graph.
        self._composite_node = None

        # The default layout
        self.view = None
        self.user_application = None
        self.__inError = False

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id
        self.internal_data["id"] = self.__id

    def _init_internal_data(self, d):
        self.internal_data.update(d)

    # -- the ugly back reference --
    def set_compositenode(self, upper):
        self._composite_node = proxy(upper)

    def set_data(self, key, value, notify=True):
        """ Set internal node data """
        self.internal_data[key] = value
        if(notify):
            self.notify_listeners(("data_modified", key, value))

    def close(self):
        self.notify_listeners(("close", self))

    def reset(self):
        """ Reset Node """
        pass

    def reload(self):
        """ Reset Node """
        pass

    def invalidate(self):
        """ Invalidate Node """
        pass

    def set_factory(self, factory):
        """ Set the factory of the node (if any) """
        self.factory = factory

    def get_factory(self):
        """ Return the factory of the node (if any) """
        return self.factory

    def get_raise_exception(self):
        return self.__inError

    def set_raise_exception(self, val):
        self.__inError = val
        self.notify_listeners(("exception_state_changed", val))

    raise_exception = property(get_raise_exception, set_raise_exception)


class Node(AbstractNode):
    """
    It is a callable object with typed inputs and outputs.
    Inputs and Outpus are indexed by their position or by a name (str)
    """

    @staticmethod
    def is_deprecated_event(event):
        evLen = len(event)
        conversionTxt = None
        retEvent = event
        if evLen == 2:
            if event[0] == "caption_modified":
                retEvent = "data_modified", "caption", event[1]
                conversionTxt = "('data_modified', 'caption', caption)"
        elif evLen == 3:
            if event[0] == "data_modified":
                if event[1] == "delay":
                    retEvent = "internal_state_changed", "delay", event[2]
                    conversionTxt = "('internal_state_changed', 'delay', delay)"
            elif event[0] == "internal_data_changed":
                retEvent = ('internal_state_changed', event[1], event[2])
                conversionTxt = "('internal_state_changed', 'key', value)"
        return conversionTxt, retEvent

    def __init__(self, inputs=(), outputs=()):
        """

        :param inputs: list of dict(name='X', interface=IFloat, value=0)
        :param outputs: list of dict(name='X', interface=IFloat)

        .. note::
            if IO names are not a string, they will be converted with str()
        """

        AbstractNode.__init__(self)
        self.clear_inputs()
        self.clear_outputs()
        self.set_io(inputs, outputs)

        # Node State
        self.modified = True

        # Internal Data
        self.internal_data["caption"] = '' # str(self.__class__.__name__)
        self.internal_data["lazy"] = True
        self.internal_data["block"] = False # Do not evaluate the node
        self.internal_data["priority"] = 0
        self.internal_data["hide"] = True # hide in composite node widget
        self.internal_data["port_hide_changed"] = set()
        # Add delay
        self.internal_data["delay"] = 0

        # Observed object to notify final nodes wich are continuously evaluated
        self.continuous_eval = Observed()

    def notify_listeners(self, event):
        txt, trevent = Node.is_deprecated_event(event)
        if txt:
            Observed.notify_listeners(self, trevent)
            Observed.notify_listeners(self, event)
        else:
            Observed.notify_listeners(self, event)

    def __call__(self, inputs=()):
        """ Call function. Must be overriden """
        raise NotImplementedError()

    def get_tip(self):
        return self.__doc__

    def copy_to(self, other):
        # we copy some attributes.
        self.transfer_listeners(other)
        # other.internal_data.update(self.internal_data)
        other.get_ad_hoc_dict().update(self.get_ad_hoc_dict())
        for portOld, portNew in zip(self.input_desc + self.output_desc,
                                    other.input_desc + other.output_desc):
            portOld.copy_to(portNew)

    def get_process_obj(self):
        """ Return the process obj """
        return self

    # property
    process_obj = property(get_process_obj)

    def set_factory(self, factory):
        """ Set the factory of the node (if any)
        and uptdate caption """
        self.factory = factory
        if factory:
            self.set_caption(factory.name)

    def get_input_port(self, name=None):
        """Gets port by name.

        Long description of the function functionality.

        :param name: the name of the port
        :type name: string
        :returns: Input port characterized by name
        :rtype: InputPort

        """
        index = self.map_index_in[name]
        return self.input_desc[index]

    ##############
    # Properties #
    ##############
    def get_lazy(self):
        """todo"""
        return self.internal_data.get("lazy", True)

    def is_lazy(self):
        return self.get_lazy()

    def set_lazy(self, data):
        """todo"""
        self.internal_data["lazy"] = data
        self.notify_listeners(("internal_data_changed", "lazy", data))

    lazy = property(get_lazy, set_lazy)

    def get_delay(self):
        """todo"""
        return self.internal_data.get("delay", 0)

    def set_delay(self, delay):
        """todo"""
        self.internal_data["delay"] = delay
        self.notify_listeners(("internal_data_changed", "delay", delay))

    delay = property(get_delay, set_delay)

    def get_block(self):
        """todo"""
        return self.internal_data.get("block", False)

    def set_block(self, data):
        """todo"""
        self.internal_data["block"] = data
        self.notify_listeners(("internal_data_changed", "blocked", data))

    block = property(get_block, set_block)

    def get_user_application(self):
        """todo"""
        return self.internal_data.get("user_application", False)

    def set_user_application(self, data):
        """todo"""
        self.internal_data["user_application"] = data
        self.notify_listeners(("internal_data_changed", "user_application", data))

    user_application = property(get_user_application, set_user_application)

    def set_caption(self, newcaption):
        """ Define the node caption """
        self.internal_data['caption'] = newcaption
        self.notify_listeners(("caption_modified", newcaption))

    def get_caption(self):
        """ Return the node caption """
        return self.internal_data.get('caption', "")

    caption = property(get_caption, set_caption)

    def is_port_hidden(self, index_key):
        """ Return the hidden state of a port """
        index = self.map_index_in[index_key]
        s = self.input_desc[index].is_hidden() # get('hide', False)
        changed = self.internal_data["port_hide_changed"]

        c = index in changed

        if(index in changed):
            return not s
        else:
            return s

    def set_port_hidden(self, index_key, state):
        """
        Set the hidden state of a port.

        :param index_key: the input port index.
        :param state: a boolean value.
        """
        index = self.map_index_in[index_key]
        s = self.input_desc[index].is_hidden() # get('hide', False)

        changed = self.internal_data["port_hide_changed"]

        if (s != state):
            changed.add(index)
            self.input_desc[index].get_ad_hoc_dict().set_metadata("hide", state)
            self.notify_listeners(("hiddenPortChange",))
        elif(index in changed):
            changed.remove(index)
            self.input_desc[index].get_ad_hoc_dict().set_metadata("hide", state)
            self.notify_listeners(("hiddenPortChange",))


    # Status
    def unvalidate_input(self, index_key, notify=True):
        """
        Unvalidate node and notify listeners.

        This method is called when the input value has changed.
        """
        self.modified = True
        index = self.map_index_in[index_key]
        if(notify):
            self.notify_listeners(("input_modified", index))
            self.continuous_eval.notify_listeners(("node_modified",))

    # Declarations
    def set_io(self, inputs, outputs):
        """
        Define the number of inputs and outputs

        :param inputs: list of dict(name='X', interface=IFloat, value=0)
        :param outputs: list of dict(name='X', interface=IFloat)
        """

        # # Values
        if(inputs is None or len(inputs) != len(self.inputs)):
            self.clear_inputs()
            if inputs:
                for d in inputs:
                    self.add_input(**d)

        if(outputs is None or len(outputs) != len(self.outputs)):
            self.clear_outputs()
            if outputs:
                for d in outputs:
                    self.add_output(**d)

        # to_script
        self._to_script_func = None

    def clear_inputs(self):
        # Values
        self.inputs = []
        # Description (list of dict (name=, interface=, ...))
        self.input_desc = []
        # translation of name to id or id to id (identity)...
        self.map_index_in = {}
        # Input states : "connected", "hidden"
        self.input_states = []
        self.notify_listeners(("cleared_input_ports",))

    def clear_outputs(self):
        # Values
        self.outputs = []
        # Description (list of dict (name=, interface=, ...))
        self.output_desc = []
        # translation of name to id or id to id (identity)...
        self.map_index_out = {}
        self.notify_listeners(("cleared_output_ports",))


    def add_input(self, **kargs):
        """ Create an input port """

        # Get parameters
        name = str(kargs['name'])
        interface = kargs.get('interface', None)

        # default value
        if(interface and not kargs.has_key('value')):
            if isinstance(interface, str):
                # Create mapping between interface name and interface class
                from openalea.core.interface import TypeNameInterfaceMap
                interface = TypeNameInterfaceMap()[interface]
                kargs['interface'] = interface

            value = interface.default()
        else:
            value = kargs.get('value', None)

        value = copy(value)

        name = str(name) # force to have a string
        self.inputs.append(None)

        port = InputPort(self)
        port.update(kargs)
        self.input_desc.append(port)

        self.input_states.append(None)
        index = len(self.inputs) - 1
        self.map_index_in[name] = index
        self.map_index_in[index] = index
        port.set_id(index)

        self.set_input(name, value, False)
        port.get_ad_hoc_dict().set_metadata("hide",
                                            kargs.get("hide", False))
        self.notify_listeners(("input_port_added", port))
        return port

    def add_output(self, **kargs):
        """ Create an output port """

        # Get parameters
        name = str(kargs['name'])
        self.outputs.append(None)

        port = OutputPort(self)
        port.update(kargs)
        self.output_desc.append(port)
        index = len(self.outputs) - 1
        self.map_index_out[name] = index
        self.map_index_out[index] = index
        port.set_id(index)
        self.notify_listeners(("output_port_added", port))
        return port

    # I/O Functions

    def set_input(self, key, val=None, notify=True):
        """
        Define the input value for the specified index/key
        """
        index = self.map_index_in[key]

        changed = True
        if(self.lazy):
            # Test if the inputs has changed
            try:
                changed = (cmp(self.inputs[index], val) != 0)
            except:
                pass

        if(changed):
            self.inputs[index] = val
            self.unvalidate_input(index, notify)

    def set_output(self, key, val):
        """
        Define the input value for the specified index/key
        """

        index = self.map_index_out[key]
        self.outputs[index] = val
        self.notify_listeners(("output_modified", key, val))

    def output(self, key):
        return self.get_output(key)

    def get_input(self, index_key):
        """ Return the input value for the specified index/key """
        index = self.map_index_in[index_key]
        return self.inputs[index]

    def get_output(self, index_key):
        """ Return the output for the specified index/key """
        index = self.map_index_out[index_key]
        return self.outputs[index]

    def get_input_state(self, index_key):
        index = self.map_index_in[index_key]
        return self.input_states[index]

    def set_input_state(self, index_key, state):
        """ Set the state of the input index/key (state is a string) """

        index = self.map_index_in[index_key]
        self.input_states[index] = state
        self.unvalidate_input(index)

    def get_nb_input(self):
        """ Return the nb of input ports """
        return len(self.inputs)

    def get_nb_output(self):
        """ Return the nb of output ports """
        return len(self.outputs)

    # Functions used by the node evaluator

    def eval(self):
        """
        Evaluate the node by calling __call__
        Return True if the node needs a reevaluation
        and a timed delay if the node needs a reevaluation at a later time.
        """
        # lazy evaluation
        if self.block and self.get_nb_output() != 0 and self.output(0) is not None:
            return False
        if (self.delay == 0 and self.lazy) and not self.modified:
            return False

        self.notify_listeners(("start_eval",))

        # Run the node
        outlist = self.__call__(self.inputs)

        # Copy outputs
        # only one output
        if len(self.outputs) == 1:
            try:
                if hasattr(outlist, "__getitem__") and len(outlist) == 1:
                    self.outputs[0] = outlist[0]
                else:
                    self.outputs[0] = outlist
            except TypeError:
                self.outputs[0] = outlist

            self.output_desc[0].notify_listeners(("tooltip_modified",))

        else: # multi output
            if(not isinstance(outlist, tuple) and
               not isinstance(outlist, list)):
                outlist = (outlist,)

            for i in range(min(len(outlist), len(self.outputs))):
                self.output_desc[i].notify_listeners(("tooltip_modified",))
                self.outputs[i] = outlist[i]

        # Set State
        self.modified = False
        self.notify_listeners(("stop_eval",))

        if self.delay == 0:
            return False
        return self.delay

    def __getstate__(self):
        """ Pickle function : remove not saved data"""

        odict = self.__dict__.copy()
        odict.update(AbstractNode.__getstate__(self))

        odict['modified'] = True


        outputs = range(len(self.outputs))
        for i in range(self.get_nb_output()):
            try:
                outputs[i] = copy(self.outputs[i])
            except:
                outputs[i] = None
        odict['outputs'] = outputs

        inputs = range(self.get_nb_input())
        for i in range(self.get_nb_input()):
            try:
                inputs[i] = copy(self.inputs[i])
            except:
                inputs[i] = None
        odict['inputs'] = inputs

        in_ports = []
        out_ports = []

        for i, port in enumerate(self.input_desc):
            port.vertex = None
            in_ports.append(copy(port))
            port.vertex = ref(self)

        for i, port in enumerate(self.output_desc):
            port.vertex = None
            out_ports.append(copy(port))
            port.vertex = ref(self)

        odict['input_desc'] = in_ports
        odict['output_desc'] = out_ports

        return odict

    def __setstate__(self, dict):
        self.__dict__.update(dict)

        for port in self.input_desc:
            port.vertex = ref(self)
        for port in self.output_desc:
            port.vertex = ref(self)

    def reload(self):
        """ Reset ports """
        for i in range(self.get_nb_output()):
            self.outputs[i] = None

        i = self.get_nb_input()
        for i in xrange(i):
            # if(not connected or self.input_states[i] is "connected"):
            self.set_input(i, self.input_desc[i].get('value', None))

        if(i > 0):
            self.invalidate()

    def reset(self):
        """ Reset ports """
        for i in range(self.get_nb_output()):
            self.outputs[i] = None

        i = self.get_nb_input()

        if(i > 0):
            self.invalidate()

    def invalidate(self):
        """ Invalidate node """

        self.modified = True
        self.notify_listeners(("input_modified", -1))

        self.continuous_eval.notify_listeners(("node_modified", self))

# X     @property
# X     def outputs(self):
# X         return [self.output(i) for i in range(self.get_nb_output())]

    def to_script (self):
        """Script translation of this node.
        """
        if self._to_script_func is None :
            return "#node %s do not define any scripting\n" % self.factory.name
        else :
            return self._to_script_func(self.inputs, self.outputs)


class FuncNode(Node):
    """ Node with external function or function """

    def __init__(self, inputs, outputs, func):
        """
        :param inputs: list of dict(name='X', interface=IFloat, value=0)
        :param outputs: list of dict(name='X', interface=IFloat)
        :param func: A function
        """

        Node.__init__(self, inputs, outputs)
        self.func = func
        self.__doc__ = func.__doc__

    def __call__(self, inputs=()):
        """ Call function. Must be overriden """
        if(self.func):
            return self.func(*inputs)

    def get_process_obj(self):
        """ Return the process obj """

        return self.func

    process_obj = property(get_process_obj)


# Utility functions
def gen_port_list(size):
    """ Generate a list of port description """
    mylist = []
    for i in range(size):
        mylist.append(dict(name='t' + str(i), interface=None, value=i))
    return mylist


def initialise_standard_metadata():
    """Declares the standard keys used by the Node structures. Called at the end of this file"""
    # we declare what are the node model ad hoc data we require:
    AbstractNode.extend_ad_hoc_slots("position", list, [0, 0], "posx", "posy")
    Node.extend_ad_hoc_slots("userColor", list, None, "user_color")
    Node.extend_ad_hoc_slots("useUserColor", bool, True, "use_user_color",)


initialise_standard_metadata()
