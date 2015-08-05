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

# import imp
# import inspect
# import os
# import sys
# import string
# import types
from copy import copy  # , deepcopy
from weakref import ref, proxy  # TODO: GRUUIK to remove

# from signature import get_parameters
# import signature as sgn
from observer import Observed  # , AbstractListener
# from actor import IActor
from metadatadict import HasAdHoc  # , MetaDataDict
# from interface import TypeNameInterfaceMap
from openalea.core.node_port import InputPort, OutputPort


# Exceptions
class RecursionError(Exception):
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

        self.__id = None  # TODO: GRUUIK
        # Internal Data (caption...)
        self.internal_data = {}
        self.factory = None  # TODO: change to self._factory

        # -- the ugly back reference -- # TODO: remove this
        # !! Christophe, don't look at this one.
        # proxy to higher level structure, aka CompositeNode.
        # This is currently only used by the "wrap_method" node
        # that needs to modify the topology of the graph.
        self._composite_node = None

        # The default layout
        self.view = None
        self.user_application = None
        self.__inError = False  # TODO: GRUUIK

    def get_id(self):
        """ Return node id.
        """
        return self.__id

    def set_id(self, node_id):
        """ Set id of the node.
        """
        self.__id = node_id
        self.internal_data["id"] = self.__id  # TODO: remove duplication

    def _init_internal_data(self, d):
        self.internal_data.update(d)

    # -- the ugly back reference --
    def set_compositenode(self, upper):  # TODO: remove GRUUIK
        self._composite_node = proxy(upper)

    def set_data(self, key, value, notify=True):
        """ Associate a data with the node.

        args:
            - key (any): key for the dict of properties.
            - value (any): value to associate to the key.
            - notify (bool): tell the node to notify listeners.
        """
        self.internal_data[key] = value

        if notify:
            self.notify_listeners(("data_modified", key, value))

    def close(self):  # TODO: when is this method called
        self.notify_listeners(("close", self))

    def reset(self):  # TODO: useless?? remove?
        """ Reset Node """
        pass

    def reload(self):  # TODO: useless?? remove?
        """ Reset Node """
        pass

    def invalidate(self):  # TODO: it needs to be in the algo not in the node
        """ Invalidate Node """
        pass

    def set_factory(self, factory):
        """ Associate a factory to the node.

        args:
            - factory (NodeFactory): factory to associate.
        """
        self.factory = factory

    def get_factory(self):
        """ Return a factory able to produce this node.

        return:
            - (NodeFactory) or None if no factory associated.
        """
        return self.factory

    def get_raise_exception(self):  # TODO: WTF!!!
        return self.__inError

    def set_raise_exception(self, val):  # TODO: WTF!!!
        self.__inError = val
        self.notify_listeners(("exception_state_changed", val))

    raise_exception = property(get_raise_exception, set_raise_exception)
    # TODO: double WTF!!


class Node(AbstractNode):
    """ A Node is a callable object with typed inputs and outputs.
    Inputs and Outpus are indexed by their position or by a name (str)
    """

    @staticmethod
    def is_deprecated_event(event):
        ev_len = len(event)
        conversion_txt = None
        ret_event = event
        if ev_len == 2:
            if event[0] == "caption_modified":
                ret_event = "data_modified", "caption", event[1]
                conversion_txt = "('data_modified', 'caption', caption)"
        elif ev_len == 3:
            if event[0] == "data_modified":
                if event[1] == "delay":
                    ret_event = "internal_state_changed", "delay", event[2]
                    conversion_txt = "('internal_state_changed', 'delay', delay)"
            elif event[0] == "internal_data_changed":
                ret_event = ('internal_state_changed', event[1], event[2])
                conversion_txt = "('internal_state_changed', 'key', value)"
        return conversion_txt, ret_event

    def __init__(self, inputs=(), outputs=()):
        """ Constructor

        args:
            - inputs (list of dict(name='X', interface=IFloat, value=0) )
            - outputs (list of dict(name='X', interface=IFloat) )

        .. note::
            if IO names are not a string, they will be converted with str()
        """
        AbstractNode.__init__(self)
        self.clear_inputs()
        self.clear_outputs()
        self.set_io(inputs, outputs)

        # Node State
        self.modified = True  # TODO: need to be in eval algo

        # Internal Data
        self.internal_data["caption"] = ''  # str(self.__class__.__name__)
        self.internal_data["lazy"] = True
        self.internal_data["block"] = False  # Do not evaluate the node
        self.internal_data["priority"] = 0
        self.internal_data["hide"] = True  # hide in composite node widget
        self.internal_data["port_hide_changed"] = set()
        # Add delay
        self.internal_data["delay"] = 0

        # Observed object to notify final nodes wich are continuously evaluated
        self.continuous_eval = Observed()  # TODO: a bit too add hoc

    def clear_inputs(self):  # TODO: transform into private method???
        # Values
        self.inputs = []
        # Description (list of dict (name=, interface=, ...))
        self.input_desc = []
        # translation of name to id or id to id (identity)...
        self.map_index_in = {}
        # Input states : "connected", "hidden"
        self.input_states = []
        self.notify_listeners(("cleared_input_ports",))

    def clear_outputs(self):  # TODO: transform into private method???
        # Values
        self.outputs = []
        # Description (list of dict (name=, interface=, ...))
        self.output_desc = []
        # translation of name to id or id to id (identity)...
        self.map_index_out = {}
        self.notify_listeners(("cleared_output_ports",))

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
        """ Return associated tooltip.

        Default to documentation of the class.

        return:
            - (str)
        """
        return self.__doc__

    def copy_to(self, other):
        """ Copy node attributes and data.
        """
        # we copy some attributes.
        self.transfer_listeners(other)
        # other.internal_data.update(self.internal_data)
        other.get_ad_hoc_dict().update(self.get_ad_hoc_dict())

        # copy input descriptions
        for port_self, port_other in zip(self.input_desc, other.input_desc):
            port_self.copy_to(port_other)

        # copy output descriptions
        for port_self, port_other in zip(self.output_desc, other.output_desc):
            port_self.copy_to(port_other)

    def get_process_obj(self):
        """ Return the process obj.
        """
        return self

    # property
    process_obj = property(get_process_obj)  # TODO: get read of properties

    def set_factory(self, factory):
        """ Associate a factory to the node.

        args:
            - factory (NodeFactory): factory to associate.
        """
        AbstractNode.set_factory(self, factory)
        if factory is not None:
            self.set_caption(factory.name)

    def get_input_port(self, name=None):
        """ Get a description of a port.

        args:
            - name(str): name of the input port

        return:
            - port (name, Interface, default_value)
        """
        index = self.map_index_in[name]  # TODO: where is this one created
        return self.input_desc[index]

    ##############
    # Properties #
    ##############
    def is_lazy(self):
        """ Check if the node allows lazy evaluation.
        """
        return self.internal_data.get("lazy", True)

    def get_lazy(self):
        """todo"""
        return self.is_lazy()

    def set_lazy(self, flag):  # TODO: no blocking of notifiers for this one?
        """ Set the node to allow lazy evaluation.

        args:
            - flag (bool)
        """
        self.internal_data["lazy"] = flag
        self.notify_listeners(("internal_data_changed", "lazy", flag))

    lazy = property(get_lazy, set_lazy)  # TODO: remove

    def get_delay(self):
        """ Retrieve associated evaluation delay.
        """
        return self.internal_data.get("delay", 0)

    def set_delay(self, delay):  # TODO: no blocking of notifiers for this one?
        """ Set minimum delay between two evaluations.

        args:
            - delay (int)
        """
        self.internal_data["delay"] = delay
        self.notify_listeners(("internal_data_changed", "delay", delay))

    delay = property(get_delay, set_delay)  # TODO: remove

    def is_block(self):
        """ Check if the node block evaluation.
        """
        return self.internal_data.get("block", False)

    def get_block(self):
        return self.is_block()

    def set_block(self, flag):
        """ Set the node to block evaluation.

        args:
            - flag (bool)
        """
        self.internal_data["block"] = flag
        self.notify_listeners(("internal_data_changed", "blocked", flag))

    block = property(get_block, set_block)  # TODO: remove

    def get_user_application(self):
        """ Retrieve user_application associated with the node.
        """
        return self.internal_data.get("user_application", False)

    def set_user_application(self, appli):  # TODO: better doc
        """ Associate a user application with the node.

        args:
            - appli (UNKNOWN):
        """
        self.internal_data["user_application"] = appli
        self.notify_listeners(("internal_data_changed",
                               "user_application",
                               appli))

    user_application = property(get_user_application,
                                set_user_application)  # TODO: remove

    def set_caption(self,
                    newcaption):  # TODO: no blocking of notifiers for this one?
        """ Define the node caption.

        args:
            - newcaption (str)
        """
        self.internal_data['caption'] = newcaption
        self.notify_listeners(("caption_modified", newcaption))

    def get_caption(self):
        """ Return the node caption.

        return:
            - caption (str)
        """
        return self.internal_data.get('caption', "")

    caption = property(get_caption, set_caption)  # TODO: remove

    def is_port_hidden(self, index_key):
        """ Check if a port is hidden.

        Only input ports can be hidden.

        args:
            - index_key (str): local name of an input port

        return:
            - (bool)
        """
        index = self.map_index_in[index_key]
        s = self.input_desc[index].is_hidden()  # get('hide', False)
        changed = self.internal_data["port_hide_changed"]  # TODO: WTF!

        if index in changed:
            return not s
        else:
            return s

    def set_port_hidden(self, index_key,
                        state):  # TODO: no blocking of notifiers for this one?
        """ Set an input port to be hidden or not.

        args:
            - index_key (str): local name of port
            - state (bool): hidden flag
        """
        index = self.map_index_in[index_key]
        s = self.input_desc[index].is_hidden()  # get('hide', False)

        changed = self.internal_data["port_hide_changed"]

        if s != state:
            changed.add(index)
            self.input_desc[index].get_ad_hoc_dict().set_metadata("hide", state)
            self.notify_listeners(("hiddenPortChange",))
        elif index in changed:
            changed.remove(index)
            self.input_desc[index].get_ad_hoc_dict().set_metadata("hide", state)
            self.notify_listeners(("hiddenPortChange",))
            # TODO: any other case?

    # Status
    def unvalidate_input(self, index_key,
                         notify=True):  # TODO: correct spelling and remove function
        """ Invalidate node and notify listeners.

        This method is called when the input value has changed.
        """
        self.modified = True
        index = self.map_index_in[index_key]
        if notify:
            self.notify_listeners(("input_modified", index))
            self.continuous_eval.notify_listeners(("node_modified",))

    # Declarations
    def set_io(self, inputs, outputs):
        """ Associate a definitions of ports with this node.

        args:
            - inputs (list of dict(name='X', interface=IFloat, value=0))
            - outputs (list of dict(name='X', interface=IFloat))
        """
        if inputs is None or len(inputs) != len(
                self.inputs):  # TODO: what for, always clear!!
            self.clear_inputs()
            if inputs is not None:  # TODO: remove, inputs=[] by default
                for d in inputs:
                    self.add_input(**d)

        if outputs is None or len(outputs) != len(
                self.outputs):  # TODO: what for, always clear!!
            self.clear_outputs()
            if outputs is not None:  # TODO: remove, outputs=[] by default
                for d in outputs:
                    self.add_output(**d)

        # to_script # TODO: remove unused
        self._to_script_func = None

    def add_input(self, **kargs):
        """ Create an input port.
        """
        # Get parameters
        name = str(kargs['name'])
        interface = kargs.get('interface', None)

        # default value
        if interface is not None and 'value' not in kargs:
            if isinstance(interface, str):
                # Create mapping between interface name and interface class
                from openalea.core.interface import TypeNameInterfaceMap
                interface = TypeNameInterfaceMap()[interface]
                kargs['interface'] = interface

            value = interface.default()
        else:
            value = kargs.get('value', None)

        value = copy(value)

        name = str(name)  # force to have a string  # TODO: done already
        self.inputs.append(None)

        port = InputPort(self)
        port.update(kargs)
        self.input_desc.append(port)

        self.input_states.append(None)
        index = len(self.inputs) - 1
        self.map_index_in[name] = index
        self.map_index_in[index] = index  # TODO: hack gruuik to remove
        port.set_id(index)

        self.set_input(name, value, False)
        port.get_ad_hoc_dict().set_metadata("hide",
                                            # TODO: use node.set_hidden instead
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

    def set_input(self, key, val=None,
                  notify=True):  # TODO: remove, data are not to be stored in the node
        """ Store a value on a specific input port.

        Define the input value for the specified index/key
        """
        index = self.map_index_in[key]

        changed = True
        if self.lazy:
            # Test if the inputs has changed
            try:
                changed = (cmp(self.inputs[index], val) != 0)
            except:
                pass

        if changed:
            self.inputs[index] = val
            self.unvalidate_input(index, notify)

    def set_output(self, key,
                   val):  # TODO: remove, data are not to be stored in the node
        """
        Define the input value for the specified index/key
        """

        index = self.map_index_out[key]
        self.outputs[index] = val
        self.notify_listeners(("output_modified", key, val))

    def output(self,
               key):  # TODO: remove, data are not to be stored in the node
        return self.get_output(key)

    def get_input(self,
                  index_key):  # TODO: remove, data are not to be stored in the node
        """ Return the input value for the specified index/key """
        index = self.map_index_in[index_key]
        return self.inputs[index]

    def get_output(self,
                   index_key):  # TODO: remove, data are not to be stored in the node
        """ Return the output for the specified index/key """
        index = self.map_index_out[index_key]
        return self.outputs[index]

    def get_input_state(self, index_key):  # TODO: What is a port state???
        index = self.map_index_in[index_key]
        return self.input_states[index]

    def set_input_state(self, index_key, state):
        """ Set the state of the input index/key (state is a string) """

        index = self.map_index_in[index_key]
        self.input_states[index] = state
        self.unvalidate_input(index)

    def get_nb_input(self):
        """ Return the nb of input ports
        """
        return len(self.inputs)

    def get_nb_output(self):
        """ Return the nb of output ports
        """
        return len(self.outputs)

    # Functions used by the node evaluator

    def eval(self):  # TODO: remove, eval has to be performed outside of node
        """
        Evaluate the node by calling __call__
        Return True if the node needs a reevaluation
        and a timed delay if the node needs a reevaluation at a later time.
        """
        # lazy evaluation
        if self.block and self.get_nb_output() != 0 and self.output(
                0) is not None:
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

        else:  # multi output
            if (not isinstance(outlist, tuple) and
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
            except:  # TODO: GRUUIK
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

    def __setstate__(self, state):
        self.__dict__.update(state)

        for port in self.input_desc:
            port.vertex = ref(self)
        for port in self.output_desc:
            port.vertex = ref(self)

    def reload(self):  # TODO: remove, data are not to be stored in the node
        """ Reset ports """
        for i in range(self.get_nb_output()):
            self.outputs[i] = None

        i = self.get_nb_input()
        for i in xrange(i):
            # if(not connected or self.input_states[i] is "connected"):
            self.set_input(i, self.input_desc[i].get('value', None))

        if i > 0:
            self.invalidate()

    def reset(self):  # TODO: remove, data are not to be stored in the node
        """ Reset ports """
        for i in range(self.get_nb_output()):
            self.outputs[i] = None

        i = self.get_nb_input()

        if i > 0:
            self.invalidate()

    def invalidate(self):  # TODO: remove, evaluation algorithm instead
        """ Invalidate node """

        self.modified = True
        self.notify_listeners(("input_modified", -1))

        self.continuous_eval.notify_listeners(("node_modified", self))

    # X     @property
    # X     def outputs(self):
    # X         return [self.output(i) for i in range(self.get_nb_output())]

    def to_script(self):  # TODO: deprecated
        """Script translation of this node.
        """
        if self._to_script_func is None:
            return "#node %s do not define any scripting\n" % self.factory.name
        else:
            return self._to_script_func(self.inputs, self.outputs)


class FuncNode(Node):
    """ Node with external function.
    """

    def __init__(self, inputs, outputs, func):
        """ Constructor

        args:
            - inputs (list of dict(name='X', interface=IFloat, value=0) )
            - outputs (list of dict(name='X', interface=IFloat) )
            - func (callable): function used to perform node evaluation

        .. note::
            if IO names are not a string, they will be converted with str()
        """
        Node.__init__(self, inputs, outputs)
        self.func = func  # TODO: makes private
        self.__doc__ = func.__doc__  # TODO: override get_tip instead??

    def __call__(self, inputs=()):
        if self.func is not None:
            return self.func(*inputs)

    def get_process_obj(self):
        """ Return the process obj """

        return self.func

    process_obj = property(
        get_process_obj)  # TODO: duplication, another reason not to use properties


class FuncNodeRaw(FuncNode):
    def __call__(self, inputs=()):
        if self.func is not None:
            return self.func(*inputs)


class FuncNodeSingle(FuncNode):
    def __call__(self, inputs=()):
        if self.func is not None:
            return self.func(*inputs),


def initialise_standard_metadata():
    """Declares the standard keys used by the Node structures.
    Called at the end of this file
    """
    # we declare what are the node model ad hoc data we require:
    AbstractNode.extend_ad_hoc_slots("position", list, [0, 0], "posx", "posy")
    Node.extend_ad_hoc_slots("userColor", list, None, "user_color")
    Node.extend_ad_hoc_slots("useUserColor", bool, True, "use_user_color", )


initialise_standard_metadata()
