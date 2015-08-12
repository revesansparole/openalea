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
"""A CompositeNode is a Node that contains other nodes connected in a directed
graph. A CompositeNodeFactory instance is a factory that build CompositeNode
instances. Different instances of the same factory can coexist and can be
modified in a dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import copy

from openalea.core.dataflow_evaluation import BruteEvaluation, LazyEvaluation
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment
from openalea.core.dataflow_state import DataflowState

from openalea.core.node import RecursionError, Node
from openalea.core.dataflow import DataFlow, InvalidEdge, PortError

import logger

quantify = False


# class IncompatibleNodeError(Exception):
#     """todo"""
#     pass


class CompositeNode(Node):
    """ A CompositeNode is a container that interconnects
    different node instances between them in directed graph.
    """

    mimetype = "openalea/compositenode"

    def __init__(self, inputs=(), outputs=()):
        """ Constructor

        args:
            - inputs (list of dict(name='X', interface=IFloat, value=0) )
            - outputs (list of dict(name='X', interface=IFloat) )

        .. note::
            if IO names are not a string, they will be converted with str()
        """
        self._dataflow = DataFlow()
        self.id_in = None
        self.id_out = None
        Node.__init__(self, inputs, outputs)

        # graph modification status
        self.graph_modified = False
        self.evaluating = False
        self.eval_algo = "default"
        self._state = DataflowState(self._dataflow)

    def node(self, vid):
        """ Convenience function """
        return self._dataflow.actor(vid)

    def __len__ (self):  # TODO: hack to ensure backward compatibility
        return len(self._dataflow)

    def nodes(self):  # TODO: hack to ensure backward compatibility
        return self._dataflow.vertices()

    def vertices(self):  # TODO: hack to ensure backward compatibility
        return self._dataflow.vertices()

    def source(self, eid):  # TODO: hack to ensure backward compatibility
        return self._dataflow.source(eid)

    def target(self, eid):  # TODO: hack to ensure backward compatibility
        return self._dataflow.target(eid)

    def local_id(self, pid):  # TODO: hack to ensure backward compatibility
        return self._dataflow.local_id(pid)

    def source_port(self, eid):  # TODO: hack to ensure backward compatibility
        return self._dataflow.source_port(eid)

    def target_port(self, eid):  # TODO: hack to ensure backward compatibility
        return self._dataflow.target_port(eid)

    def edges (self):  # TODO: hack to ensure backward compatibility
        return self._dataflow.edges()

    def copy_to(self, other):
        raise NotImplementedError

    def close(self):
        """ Close all nodes.
        """
        for vid in set(self._dataflow.vertices()):
            node = self._dataflow.actor(vid)
            node.close()
        Node.close(self)

    def reset(self):
        """ Reset all nodes.
        """
        Node.reset(self)

        for vid in set(self._dataflow.vertices()):
            node = self._dataflow.actor(vid)
            node.reset()

        # TODO: hack with state
            self._state.clear()

    def invalidate(self):
        """ Invalidate all nodes.
        """
        Node.invalidate(self)

        for vid in set(self._dataflow.vertices()):
            node = self._dataflow.actor(vid)
            node.invalidate()

        # TODO: hack with state
            self._state.clear()

    def get_eval_algo(self):
        """ Return an instance of the evaluation algorithm
        associated with this composite node.
        """
        try:
            algo = self.eval_algo.strip('"').strip("'")
            if algo is None or algo == "default":
                algo = "LambdaEvaluation"  # TODO, hack use dataflow_evaluation.default instead

            # import module
            module = __import__("algo.dataflow_evaluation",
                                globals(),
                                locals(),
                                [algo])
            classobj = getattr(module, algo)
            return classobj(self._dataflow)

        except ImportError:
            from  openalea.core.algo.dataflow_evaluation import DefaultEvaluation
            return DefaultEvaluation(self._dataflow)

    def add_node(self, node, vid=None, modify=True):  # TODO: WTF!! argument modify
        """ Add a node in the dataflow with a particular id
        if id is None, auto generate one

        args:
            - node (Node): instance of node to add
            - vid (vid), default None: id of vertex to use in the dataflow
                                       if None a new one will be created
            - modify (bool), default True: flag to tell that the composite
                                       node has been modified

        return:
            - (vid): id of vertex created
        """
        vid = self._dataflow.add_vertex(vid)
        # vid = self.add_actor(node, vid)

        node.set_id(vid)
        for local_pid in xrange(node.get_nb_input()):
            self._dataflow.add_in_port(vid, local_pid)

        for local_pid in xrange(node.get_nb_output()):
            self._dataflow.add_out_port(vid, local_pid)

        self._dataflow.set_actor(vid, node)
        self.notify_vertex_addition(node, vid)

        if modify:
            self.notify_listeners(("graph_modified",))
            self.graph_modified = True

        return vid

    def remove_node(self, vid):
        """ Remove a node from the graph.

        args:
            - vid (vid): id of vertex to remove.
        """
        node = self.node(vid)
        if vid == self.id_in:
            self.id_in = None
        elif vid == self.id_out:
            self.id_out = None
        self._dataflow.remove_vertex(vid)
        node.close()
        self.notify_vertex_removal(node)
        self.notify_listeners(("graph_modified",))
        self.graph_modified = True

    def remove_edge(self, eid):
        """ Remove an edge from the graph.

        args:
            - eid (eid): id of edge to remove.
        """
        target = self._dataflow.target(eid)
        # try:
        port = self._dataflow.port(target)
        # except PortError:  # TODO: why??? in which case this happen
        #     port = None

        self._dataflow.remove_edge(eid)
        # if port is not None:
        self.node(port.vid).set_input_state(port.local_pid,
                                                  "disconnected")
        self.notify_listeners(("edge_removed", ("default", eid)))

    def connect(self, src_id, port_src, dst_id, port_dst):  # TODO: WTF, changed signature compared to dataflow.connect
        """ Connect 2 elements

        :param src_id: source node id
        :param port_src: source output port number
        :param dst_id: destination node id
        :param port_dst: destination input port number
        """

        try:
            source_pid = self._dataflow.out_port(src_id, port_src)
            target_pid = self._dataflow.in_port(dst_id, port_dst)
            eid = self._dataflow.connect(source_pid, target_pid)
        except:
            logger.error("Enable to create the edge %s %d %d %d %d" % (
            self.get_factory().name, src_id, port_src, dst_id, port_dst))
            return

        self.node(dst_id).set_input_state(port_dst, "connected")
        self.notify_listeners(("connection_modified",))
        self.graph_modified = True

        self.update_eval_listeners(src_id)

        src_port = self.node(src_id).output_desc[port_src]  # TODO: do not access list directly
        dst_port = self.node(dst_id).input_desc[port_dst]
        edgedata = "default", eid, src_port, dst_port

        # connected ports cannot be hidden:
        # nodeSrc.set_port_hidden(port_src, False)
        self.node(dst_id).set_port_hidden(port_dst, False)
        self.notify_listeners(("edge_added", edgedata))

    def set_io(self, inputs, outputs):  # TODO: use different mechanism than using physical nodes
        """ Define inputs and outputs.

        Inputs and outputs are list of dict(name='', interface='', value='')
        """

        # I/O ports
        # Remove node if nb of input has changed
        if (self.id_in is not None and
                    len(inputs) != self.node(self.id_in).get_nb_output()):
            self.remove_node(self.id_in)
            self.id_in = None

        if (self.id_out is not None and
                    len(outputs) != self.node(self.id_out).get_nb_input()):
            self.remove_node(self.id_out)
            self.id_out = None

        # Create new io node if necessary
        if self.id_in is None:
            self.id_in = self.add_node(CompositeNodeInput(inputs))
        else:
            self.node(self.id_in).set_io((), inputs)

        if self.id_out is None:
            self.id_out = self.add_node(CompositeNodeOutput(outputs))
        else:
            self.node(self.id_out).set_io(outputs, ())

        Node.set_io(self, inputs, outputs)


    ##########################################################################
    #
    #   everything below needs to disappear
    #
    ##########################################################################
    def set_input(self, index_key, val=None, *args):
        """ Copy val into input node output ports """
        self.node(self.id_in).set_input(index_key, val)

    def get_input(self, index_key):
        """ Return the composite node input"""
        return self.node(self.id_in).get_input(index_key)

    def get_output(self, index_key):
        """ Retrieve values from output node input ports """

        return self.node(self.id_out).get_output(index_key)

    def set_output(self, index_key, val):
        """ Set a value to an output """

        return self.node(self.id_out).set_output(index_key, val)

    def eval_as_expression(self, vtx_id=None, step=False):
        """
        Evaluate a vtx_id

        if node_id is None, then all the nodes without sons are evaluated
        """
        import time
        t0 = time.time()
        if self.evaluating:  # TODO: fuck it, hadhoc gestion of multi threads!
            return

        if vtx_id is not None:
            self.node(vtx_id).modified = True

        algo = self.get_eval_algo()

        try:
            self.evaluating = True

            # TODO: HACK to switch to new eval algo
            if isinstance(algo, (BruteEvaluation, LazyEvaluation)):
                print "hack EVAL"
                # create new state
                state = DataflowState(self._dataflow)  # TODO keep state over evaluations
                # state = self._state

                # fill lonely input ports if needed
                # assume no change in dataflow at this point # TODO
                for pid in self._dataflow.in_ports():
                    if self._dataflow.nb_connections(pid) == 0:
                        if pid not in state._state: # TODO: hack access internal
                            node = self.node(self._dataflow.vertex(pid))
                            lpid = self._dataflow.local_id(pid)
                            val = node.inputs[lpid]
                            state.set_data(pid, val)

                # perform evaluation
                env = EvaluationEnvironment(0)
                algo.eval(env, state, vtx_id)

                # copy data back in nodes
                for pid in self._dataflow.out_ports():
                    node = self.node(self._dataflow.vertex(pid))
                    lpid = self._dataflow.local_id(pid)
                    val = state.get_data(pid)
                    node.set_output(lpid, val)
            else:  # old algos
                algo.eval(vtx_id, step=step)
        finally:
            self.evaluating = False

        t1 = time.time()
        if quantify:
            logger.info('Evaluation time: %s' % (t1 - t0))
            print 'Evaluation time: %s' % (t1 - t0)

    # Functions used by the node evaluator

    def eval(self, *args, **kwds):
        """
        Evaluate the graph

        Return True if the node needs a reevaluation (like generator)
        """
        self.__call__()

        self.modified = False
        self.notify_listeners(("status_modified", self.modified))

        return False

    def __call__(self, inputs=()):
        """
        Evaluate the graph
        """

        if self.id_out and self.get_nb_output() > 0:
            self.eval_as_expression(self.id_out)
        else:
            self.eval_as_expression(None)

        # return ()
        return tuple(self.get_output(k) for k in range(self.get_nb_output()))

    def to_script(self):
        """Translate the dataflow into a python script.
        """
        raise DeprecationWarning()
        # from algo.dataflow_evaluation import ToScriptEvaluation
        # algo = ToScriptEvaluation(self)
        # return algo.eval()

    def compute_external_io(self, vertex_selection, new_vid):  # TODO: too ad hoc, remove
        """
        Return the list of input and output edges to connect the composite
        node.
        """

        ins, in_edges = \
            self._compute_inout_connection(vertex_selection, is_input=True)
        outs, out_edges = \
            self._compute_inout_connection(vertex_selection, is_input=False)

        in_edges = \
            self._compute_outside_connection(vertex_selection, in_edges,
                                             new_vid, is_input=True)
        out_edges = \
            self._compute_outside_connection(vertex_selection, out_edges,
                                             new_vid, is_input=False)

        return in_edges + out_edges

    def _compute_outside_connection(self, vertex_selection, new_connections,  # TODO: same as above
                                    new_vid, is_input=True):
        """
        Return external connections of a composite node with input and output
        ports.

        :param vertex_selection: a sorted set of node.
        """
        connections = []
        selected_port = {}
        if is_input:
            ports = self._dataflow.in_ports
            get_vertex_io = self._dataflow.source
            get_my_vertex = self._dataflow.target
        else:
            ports = self._dataflow.out_ports
            get_vertex_io = self._dataflow.target
            get_my_vertex = self._dataflow.source

        # For each selected vertices
        for vid in vertex_selection:
            for pid in ports(vid):
                connected_edges = self._dataflow.connected_edges(pid)

                for e in connected_edges:
                    s = get_vertex_io(e)
                    if s not in vertex_selection:
                        pname = self._dataflow.local_id(pid)
                        selected_port.setdefault((vid, pname), []).append(e)

        for edge in new_connections:
            if is_input:
                if (edge[0] != '__in__'):
                    continue
                target_id, target_port = edge[2:]
                if (target_id, target_port) in selected_port:
                    target_edges = selected_port[(target_id, target_port)]
                    for e in target_edges:
                        vid = self._dataflow.source(e)
                        port_id = self._dataflow.local_id(self._dataflow.source_port(e))
                        connections.append((vid, port_id, new_vid, edge[1]))
            else:
                if (edge[2] != '__out__'):
                    continue

                source_id, source_port = edge[0:2]
                if (source_id, source_port) in selected_port:
                    source_edges = selected_port[(source_id, source_port)]
                    for e in source_edges:
                        vid = self._dataflow.target(e)
                        port_id = self._dataflow.local_id(self._dataflow.target_port(e))
                        connections.append((new_vid, edge[3], vid, port_id))

        return connections

    def _compute_inout_connection(self, vertex_selection, is_input=True):  # TODO: same as above
        """ Return internal connections of a composite node with input or
        output port.

            - vertex_selection is a sorted set of node.
            - is_input is a boolean indicated if connection have to be
                created with input or output ports.
        """
        nodes = []
        connections = []

        # just to select unique name
        name_port = []

        if is_input:
            ports = self._dataflow.in_ports
            get_vertex_io = self._dataflow.source
            io_desc = lambda n: n.input_desc
        else:
            ports = self._dataflow.out_ports
            get_vertex_io = self._dataflow.target
            io_desc = lambda n: n.output_desc

        # For each input port
        for vid in vertex_selection:
            for pid in ports(vid):
                connected_edges = list(self._dataflow.connected_edges(pid))

                is_io = False
                for e in connected_edges:
                    s = get_vertex_io(e)
                    if s not in vertex_selection:
                        is_io = True

                if connected_edges:
                    if not is_io:
                        continue

                pname = self._dataflow.local_id(pid)
                n = self.node(vid)
                desc = dict(io_desc(n)[pname])

                caption = '(%s)' % (n.get_caption())
                count = ''
                name = desc['name']

                while name + str(count) + caption in name_port:
                    if count:
                        count += 1
                    else:
                        count = 1

                desc['name'] = name + str(count) + caption
                name_port.append(desc['name'])

                if is_input:
                    # set default value on cn input port
                    if n.inputs[pname]:
                        v = n.inputs[pname]

                        try:
                            eval(repr(v))
                            desc['value'] = v
                        except:
                            pass

                    if 'value' not in desc:
                        if 'interface' in desc and desc['interface']:
                            desc['value'] = desc['interface'].default()

                    connections.append(('__in__', len(nodes), vid, pname))
                else:  # output
                    connections.append((vid, pname, '__out__', len(nodes)))

                nodes.append(desc)

        return (nodes, connections)

    def compute_io(self, v_list=None):
        """
        Return (inputs, outputs, connections)

        representing the free port of node
        v_list is a vertex id list
        """

        ins, in_edges = self._compute_inout_connection(v_list, is_input=True)
        outs, out_edges = \
            self._compute_inout_connection(v_list, is_input=False)
        connections = in_edges + out_edges

        return (ins, outs, connections)

    def to_factory(self, sgfactory, listid=None, auto_io=False):  # TODO: move to factory instead
        """
        Update CompositeNodeFactory to fit with the graph

        listid is a list of element to export. If None, select all id.
        if auto_io is true :  inputs and outputs are connected to the free
        ports
        """

        # Clear the factory
        sgfactory.clear()

        # Properties
        sgfactory.lazy = self.lazy
        sgfactory.eval_algo = self.eval_algo
        # print self.eval_algo
        # I / O
        if (auto_io):
            (ins, outs, sup_connect) = self.compute_io(listid)
            sgfactory.inputs = ins
            sgfactory.outputs = outs
        else:
            sgfactory.inputs = [dict(val) for val in self.input_desc]
            sgfactory.outputs = [dict(val) for val in self.output_desc]
            sup_connect = []

        if listid is None:
            listid = set(self._dataflow.vertices())

        # Copy Connections
        for eid in self._dataflow.edges():

            src = self._dataflow.source(eid)
            tgt = self._dataflow.target(eid)

            if ((src not in listid) or (tgt not in listid)):
                continue
            if (src == self.id_in):
                src = '__in__'
            if (tgt == self.id_out):
                tgt = '__out__'

            source_port = self._dataflow.local_id(self._dataflow.source_port(eid))
            target_port = self._dataflow.local_id(self._dataflow.target_port(eid))
            sgfactory.connections[id(eid)] = \
                (src, source_port, tgt, target_port)

        # Add supplementary connections
        for e in sup_connect:
            sgfactory.connections[id(e)] = e

        # Copy node
        for vid in listid:

            node = self.node(vid)
            kdata = node.internal_data

            # Do not copy In and Out
            if (vid == self.id_in):
                vid = "__in__"
            elif (vid == self.id_out):
                vid = "__out__"
            else:
                pkg_id = node.get_factory().package.get_id()
                factory_id = node.get_factory().get_id()
                sgfactory.elt_factory[vid] = (pkg_id, factory_id)

            # Copy internal data
            sgfactory.elt_data[vid] = copy.deepcopy(kdata)
            # Forward compatibility for versions earlier than 0.8.0
            # We do the exact opposite than in load_ad_hoc_data, have a look there.
            if hasattr(node, "__ad_hoc_from_old_map__"):
                for newKey, oldKeys in node.__ad_hoc_from_old_map__.iteritems():
                    if len(oldKeys) == 0: continue
                    data = node.get_ad_hoc_dict().get_metadata(newKey)
                    for pos, newKey in enumerate(oldKeys):
                        sgfactory.elt_data[vid][newKey] = data[
                            pos] if isinstance(data, list) else data

            # Copy ad_hoc data
            sgfactory.elt_ad_hoc[vid] = copy.deepcopy(node.get_ad_hoc_dict())

            # Copy value
            if (not node.get_nb_input()):
                sgfactory.elt_value[vid] = []
            else:
                sgfactory.elt_value[vid] = \
                    [(port, repr(node.get_input(port))) for port
                     in xrange(len(node.inputs))
                     if node.input_states[port] is not "connected"]

        self.graph_modified = False

        # Set node factory if all node have been exported
        if (listid is None):
            self.set_factory(sgfactory)

    def notify_vertex_addition(self, vertex, vid=None):  # TODO: WTF!! always notify and let listeners choose
        vtype = "vertex"
        doNotify = True
        if (vertex.__class__.__dict__.has_key("__graphitem__")):
            vtype = "annotation"
        elif isinstance(vertex, CompositeNodeOutput):
            vtype = "outNode"
            doNotify = True if len(vertex.input_desc) else False
        elif isinstance(vertex, CompositeNodeInput):
            vtype = "inNode"
            doNotify = True if len(vertex.output_desc) else False
        else:
            pass
        if doNotify:
            self.notify_listeners(("vertex_added", (vtype, vertex)))

    def notify_vertex_removal(self, vertex):  # TODO: WTF!! always notify and let listeners choose
        vtype = "vertex"
        doNotify = True
        if (vertex.__class__.__dict__.has_key("__graphitem__")):
            vtype = "annotation"
        elif isinstance(vertex, CompositeNodeOutput):
            vtype = "outNode"
        elif isinstance(vertex, CompositeNodeInput):
            vtype = "inNode"
        else:
            pass
        self.notify_listeners(("vertex_removed", (vtype, vertex)))

    def simulate_destruction_notifications(self):  # TODO: unused, possibly useless and certainly buggy since Node does
                                                   # not have this method to override
        """emits messages as if we were adding elements to
        the composite node"""
        raise DeprecationWarning()
        # Node.simulate_destruction_notifications(self)
        #
        # ids = self.vertices()
        # for eltid in ids:
        #     node = self.node(eltid)
        #     self.notify_vertex_removal(node)
        #
        # for eid in self.edges():
        #     (src_id, dst_id) = self.source(eid), self.target(eid)
        #     etype = None
        #     src_port_id = self.local_id(self.source_port(eid))
        #     dst_port_id = self.local_id(self.target_port(eid))
        #
        #     nodeSrc = self.node(src_id)
        #     nodeDst = self.node(dst_id)
        #     src_port = nodeSrc.output_desc[src_port_id]
        #     dst_port = nodeDst.input_desc[dst_port_id]
        #
        #     # don't notify if the edge is connected to the input or
        #     # output nodes.
        #     # if(src_id == self.id_in or dst_id == self.id_out):
        #     # continue
        #
        #     edgedata = "default", eid
        #     self.notify_listeners(("edge_removed", edgedata))

    def disconnect(self, src_id, port_src, dst_id, port_dst):  # TODO: WTF!! same as remove_edge
        """ Deconnect 2 elements

        :param src_id: source node id
        :param port_src: source output port number
        :param dst_id: destination node id
        :param port_dst: destination input port number
        """

        source_pid = self._dataflow.out_port(src_id, port_src)
        target_pid = self._dataflow.in_port(dst_id, port_dst)

        for eid in self._dataflow.connected_edges(source_pid):

            if self._dataflow.target_port(eid) == target_pid:
                self.notify_listeners(("edge_removed", ("default", eid)))
                self.remove_edge(eid)
                self.node(dst_id).set_input_state(port_dst, "disconnected")
                self.notify_listeners(("connection_modified",))
                self.graph_modified = True

                self.update_eval_listeners(src_id)
                return

        raise InvalidEdge("Edge not found")

    def replace_node(self, vid, newnode):
        """ Replace the node vid by newnode """
        raise DeprecationWarning("Used???")
        # oldnode = self.actor(vid)
        # caption = newnode.caption
        # newnode.update_internal_data(oldnode.internal_data)
        # # newnode.internal_data.update(oldnode.internal_data)
        # newnode.caption = caption
        #
        # if (oldnode.get_nb_input() != newnode.get_nb_input() or
        #             oldnode.get_nb_output() != newnode.get_nb_output()):
        #     raise IncompatibleNodeError()
        #
        # self.set_actor(vid, newnode)

    # Continuous eval functions

    def set_continuous_eval(self, vid, state=True):
        """ Set a node for continuous evaluation.

        args:
            - vid (vid): id of node
            - state (bool) default True: continuous evaluation
        """
        node = self.node(vid)

        if not node.user_application and not state:
            return

        # Remove previous listener
        if node.user_application and hasattr(node, 'continuous_listener'):
            listener = node.continuous_listener
            node.continuous_listener = None
            if listener is not None:
                del listener

        node.user_application = state

        if state:
            listener = ContinuousEvalListener(self, vid)
            node.continuous_listener = listener

            # Add node as observed in all parent node
            for v in self.get_all_parent_nodes(vid):  # TODO: deprecated
                n = self.node(v)
                n.continuous_eval.register_listener(listener)

    def update_eval_listeners(self, vid):
        """ Update continuous evaluation listener for node vid """

        src_node = self.node(vid)
        src_node.continuous_eval.listeners.clear()

        # For each output
        for pid in self._dataflow.out_ports(vid):

            # For each connected node
            for npid in self._dataflow.connected_ports(pid):
                dst_id = self._dataflow.vertex(npid)

                dst_node = self.node(dst_id)
                listeners = dst_node.continuous_eval.listeners
                src_node.continuous_eval.listeners.update(listeners)


from openalea.core.observer import AbstractListener


class ContinuousEvalListener(AbstractListener):
    """ When notified this listener reexecute a dataflow on a particular vid)
    """

    def __init__(self, dataflow, vid):
        """ dataflow, vid : dataflow.eval_as_expression(vid)"""
        AbstractListener.__init__(self)
        self.dataflow = dataflow
        self.vid = vid

    def notify(self, sender, event):
        """ Notification """
        self.dataflow.eval_as_expression(self.vid)


class CompositeNodeInput(Node):  # TODO: to remove
    """Dummy node to represent the composite node inputs"""

    def __init__(self, inputs):
        """
        inputs : list of dict(name='', interface='', value'',...)
        """

        Node.__init__(self, outputs=inputs)
        self.internal_data['caption'] = "In"

    def set_input(self, input_pid, val=None, *args):
        """ Define input value """
        index = self.map_index_out[input_pid]
        self.outputs[index] = val

    def get_input(self, input_pid):
        """ Return the input value """
        index = self.map_index_out[input_pid]
        return self.outputs[index]

    def eval(self):
        return False

    def to_script(self):
        return ""


class CompositeNodeOutput(Node):
    """Dummy node to represent the composite node outputs"""

    def __init__(self, outputs):
        """
        outputs : list of dict(name='', interface='', value'',...)
        """
        Node.__init__(self, inputs=outputs)
        self.internal_data['caption'] = "Out"

    def get_output(self, output_pid):
        """ Return Output value """

        index = self.map_index_in[output_pid]
        return self.inputs[index]

    def set_output(self, output_pid, val):
        """ Define output """

        index = self.map_index_in[output_pid]
        self.inputs[index] = val

    def eval(self):
        return False

    def to_script(self):
        return ""
