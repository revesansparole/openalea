# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
""" This module provide algorithms to store execution
provenance based on a dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from dataflow_state import DataflowState
from graph import Graph


class ProvenanceExec(object):
    """ Base class to store the states of a dataflow
    after evaluations and reload them.
    """
    def __init__(self, dataflow):
        """ Constructor

        args:
            - dataflow (DataFlow): the dataflow to survey
        """
        self._dataflow = dataflow
        self._exec_graph = Graph()
        self._stored = {}

    def clear(self):
        """ Remove all data stored in the provenance.
        """
        self._exec_graph.clear()
        self._stored.clear()

    def dataflow(self):
        """ Return reference on surveyed dataflow.
        """
        return self._dataflow

    def execution_graph(self):
        """ Return reference on execution graph.
        """
        return self._exec_graph

    def new_execution(self, exec_id=None):
        """ Create a new execution instance.

        If exec_id is not None, the new execution
        will be seen as its daughter

        args:
            - exec_id (eid): id of reference execution

        return:
            - eid: id of new execution
        """
        if exec_id is not None and exec_id not in self._exec_graph:
            raise KeyError("invalid exec_id")

        eid = self._exec_graph.add_vertex()

        if exec_id is not None:
            self._exec_graph.add_edge((exec_id, eid))

        return eid

    def parent_execution(self, exec_id):
        """ Retrieve execution connected to this one.

        args:
            - exec_id (eid): id of execution whose parent is unknown

        return:
            - parent id (eid) or None if no parent
        """
        if self._exec_graph.nb_in_edges(exec_id) == 0:
            return None

        eid, = self._exec_graph.in_neighbors(exec_id)
        return eid

    def __contains__(self, exec_id):
        """ Test wether the given exec_id has been stored already.
        """
        return exec_id in self._stored

    def get_state(self, exec_id, state=None):
        """ Retrieve the state associated with a given execution.

        args:
            - exec_id (eid): unique id for a given execution
            - state (DataFlowState): a state in which to store the data
                                     associated with an execution.
                                     Default to None, will create a new one

        return:
            - state (DataFlowState): newly created if state is None or
                                     use state but clear it first.
        """
        dp, dv = self._stored[exec_id]

        if state is None:
            state = DataflowState(self.dataflow())
        else:
            assert state.dataflow() == self.dataflow()

        state.clear()

        for pid, (changed, data) in dp.items():
            state.set_data(pid, data)
            state.set_changed(pid, changed)

        for vid, (tinit, tend, already) in dv.items():
            if tinit is not None:
                state.set_task_start_time(vid, tinit)
            if tend is not None:
                state.set_task_end_time(vid, tend)
            if already:
                state.set_task_already_evaluated(vid)

        return state

    def store(self, exec_id, state):
        """ Store a copy of state.

        args:
            - exec_id (eid): unique id for a given execution
            - state (DataFlowState): a state to store
        """
        if exec_id in self._stored:
            raise KeyError("execution already stored")

        if exec_id not in self._exec_graph:
            raise KeyError("execution id hasn't been recorded")

        if not state.is_valid_against(self._dataflow):
            raise UserWarning("Unable to store this state")

        dv = dict(state.tasks())
        dp = {}
        for pid, data in state.items():
            dp[pid] = (state.has_changed(pid), data)

        self._stored[exec_id] = (dp, dv)

    def last_evaluation(self, vid, exec_id=None):
        """ Find last execution id where node has been evaluated.

        Useful with lazy evaluations.

        args:
            - vid (vid): id of node to check
            - exec_id (eid): execution to start the search
                             if None will start from leaf of the graph
                             or raise an error if there is multiple leaves.

        return:
            - eid (eid): id of execution where evaluation of node
                         actually occurred for the last time
        """
        g = self._exec_graph

        if exec_id is None:
            # find leaves of the execution graph
            leaves = [eid for eid in g.vertices() if g.nb_out_edges(eid) == 0]
            print "leaves", leaves, tuple(g.vertices())
            if len(leaves) == 0:
                raise UserWarning("no execution recorded yet")
            elif len(leaves) > 1:
                msg = "function ambiguous, need to specify a branch"
                raise UserWarning(msg)
            else:
                exec_id, = leaves

        state = self.get_state(exec_id)  # TODO: optimize
        if state.task_start_time(vid) is None:
            if g.nb_in_neighbors(exec_id) == 0:
                raise UserWarning("no valid evaluation found")

            p_exec, = tuple(g.in_neighbors(exec_id))
            return self.last_evaluation(vid, p_exec)
        else:
            return exec_id

    def last_change(self, pid, exec_id):
        """ Find the last evaluation that changed this port.

        args:
            - pid (pid): id of output port, or lonely input port, to look at
            - exec_id (eid): id of execution that modified this port data
        """
        df = self._dataflow
        g = self._exec_graph

        state = self.get_state(exec_id)  # TODO: optimize

        if df.is_in_port(pid):
            if df.nb_connections(pid) == 0:  # lonely input port
                changed = state.has_changed(pid)
                if changed or g.nb_in_neighbors(exec_id) == 0:
                    return exec_id
                else:
                    p_exec, = tuple(g.in_neighbors(exec_id))
                    return self.last_change(pid, p_exec)
            else:
                raise KeyError("unable to compute last change for in ports")
        else:  # out port
            changed = state.has_changed(pid)
            if changed:
                return exec_id
            else:
                parent_ids = tuple(g.in_neighbors(exec_id))
                if len(parent_ids) == 0:
                    raise UserWarning("data never changed????")
                p_exec, = parent_ids
                return self.last_change(pid, p_exec)

    def provenance(self, pid, exec_id):
        """ Find where does a data come from.

        if pid is an input port:
            - lonely port: return execution id when user set this port
            - other: return list of output ports which made up this data
        if pid is an output port:
            return id of node that produced this data and execution

        args:
            - pid (pid): id of port on which resides the data.
            - exec_id (eid): id of the execution for which data
                            are on given port.

        return:
            - lonely input port: (None, exec_id)
            - input port: (output_port1, ..., output_portN)
            - output_port: (vid, exec_id)
        """
        df = self._dataflow

        if exec_id not in self:
            raise KeyError("execution not stored yet")

        if df.is_in_port(pid):  # input port
            if df.nb_connections(pid) == 0:  # lonely input port
                return None, self.last_change(pid, exec_id)
            else:
                return tuple(df.connected_ports(pid))
        else:  # output port
            vid = df.vertex(pid)
            return vid, self.last_evaluation(vid, exec_id)
