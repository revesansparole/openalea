# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
""" This module provide an implementation of a way
to store data exchanged between nodes of a dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from time import clock


class DataflowState(object):
    """ Store outputs of node and provide a way to access them
    """
    def __init__(self, dataflow):
        """ constructor

        args:
            - dataflow (Dataflow)
        """
        self._dataflow = dataflow
        self._state = {}
        self._changed = {}
        self._task_start = {}
        self._task_end = {}
        self.clear()

    def dataflow(self):
        return self._dataflow

    def clear(self):
        """Clear state
        """
        self._state.clear()
        self._changed.clear()
        self._task_start.clear()
        self._task_end.clear()
        for vid in self._dataflow.vertices():
            self._task_start[vid] = None
            self._task_end[vid] = None

    def reinit(self):
        """ Remove all data stored except for the one
        associated to lonely input ports.
        """
        df = self._dataflow

        # save state
        save = dict((pid, dat) for pid, dat in self._state.items()
                    if df.is_in_port(pid) and df.nb_connections(pid) == 0)

        save_ch = dict((pid, dat) for pid, dat in self._changed.items()
                       if df.is_in_port(pid) and df.nb_connections(pid) == 0)

        # clear
        self.clear()

        # resume state
        self._state.update(save)
        self._changed.update(save_ch)

    def is_ready_for_evaluation(self):
        """ Test wether the state contains enough information
        to evaluate the associated dataflow.

        Simply check that each lonely input port has
        some data attached to it.
        """
        df = self._dataflow
        state = self._state

        return all([pid in state for pid in df.in_ports()
                    if df.nb_connections(pid) == 0])

    def is_valid(self):
        """ Test wether all data have been computed
        """
        df = self._dataflow
        state = self._state

        if not self.is_ready_for_evaluation():
            return False

        # check that all nodes have been evaluated
        if not all([pid in state for pid in df.out_ports()]):
            return False

        return True

    def cmp_port_priority(self, pid1, pid2):
        """ Compare port priority.

        Compare first x position of actors
        then use pids"""
        df = self._dataflow

        try:
            node1 = df.actor(df.vertex(pid1))
        except KeyError:
            return cmp(pid1, pid2)

        try:
            node2 = df.actor(df.vertex(pid2))
        except KeyError:
            return cmp(pid1, pid2)

        p1 = node1.get_ad_hoc_dict().get_metadata('position')[0]
        p2 = node2.get_ad_hoc_dict().get_metadata('position')[0]

        ret = cmp(p1, p2)
        if ret != 0:
            return ret

        return cmp(pid1, pid2)

    def items(self):
        """ Iterate on all pid, values stored in this state.

        yield: (pid, value)
        """
        return self._state.items()

    def __contains__(self, pid):
        """ Check wether the port already hold data.
        """
        return pid in self._state

    def get_data(self, pid):
        """ Retrieve data associated with a port.

        If pid is an output port, retrieve single item of data
        if pid is an input port, retrieve data on all output
        ports connected to this port and return a list of it
        or a single item if only one port connected

        args:
            - pid (pid): id of port either in or out
        """
        df = self._dataflow
        state = self._state

        if pid in state:  # either out_port or lonely in_port
            return state[pid]
        elif df.is_out_port(pid):
            raise KeyError("value not set for this port")
        else:
            npids = list(df.connected_ports(pid))
            if len(npids) == 0:
                raise KeyError("lonely in_port not set")
            elif len(npids) == 1:
                return self.get_data(npids[0])
            else:
                npids.sort(self.cmp_port_priority)
                return [self.get_data(pid) for pid in npids]

    def set_data(self, pid, data):
        """ Store data on a port.

        Port must be either an output port or a lonely input port.

        args:
            - pid (pid): id of port
            - data (any)
        """
        df = self._dataflow
        if df.is_in_port(pid) and df.nb_connections(pid) > 0:
            raise KeyError("no storage on input ports")

        self._state[pid] = data
        # by default data are tagged as changed
        self._changed[pid] = True

    def has_changed(self, pid):
        """ Return wether data has been modified in this state.

        Data in a state can either:
         - be set by user, in which case they are tagged as changed
         - be newly computed by some node, also tagged as changed
         - stay unchanged from some previous computation
         """
        return self._changed[pid]

    def input_has_changed(self, pid):
        """ Check if all outputs connected to this port
        are still flagged as unchanged.

        args:
            - pid (pid): id of input port to test.
        """
        df = self._dataflow

        #check that port is an input port
        if df.is_out_port(pid):
            raise KeyError("must be an input port")

        # case of a top node
        if df.nb_connections(pid) == 0:
            return self._changed.get(pid, True)

        # case of a node connected to other nodes upstream
        for npid in df.connected_ports(pid):
            if self._changed.get(npid, True):
                return True

        return False

    def set_changed(self, pid, flag):
        """ Set the changed property of a data on a port.

        args:
            - pid (pid): id of port where data is stored
            - flag (True|False): changed or unchanged
        """
        if pid not in self._state:
            raise KeyError("no data on given port")

        self._changed[pid] = flag

    def task_start_time(self, vid):
        """ Return time of beginning of task evalution.

        args:
            - vid (vid): id of task to  monitor.

        return:
            - time of beginning of task if task already evaluated
            - None, otherwise
        """
        return self._task_start[vid]

    def set_task_start_time(self, vid, t):
        """ Return time of beginning of task evalution.

        args:
            - vid (vid): id of task to  monitor.
            - t (float): time
        """
        self._task_start[vid] = t

    def task_started(self, vid):
        """ Store start time of a task.

        args:
            - vid (vid): id of task that just started
        """
        self._task_start[vid] = clock()

    def task_end_time(self, vid):
        """ Return time of end of task evalution.

        args:
            - vid (vid): id of task to  monitor.

        return:
            - time of end of task if task already finish evaluation
            - None, otherwise
        """
        return self._task_end[vid]

    def set_task_end_time(self, vid, t):
        """ Return time of end of task evalution.

        args:
            - vid (vid): id of task to  monitor.
            - t (float): time
        """
        self._task_end[vid] = t

    def task_ended(self, vid):
        """ Store end time of a task.

        args:
            - vid (vid): id of task that just started
        """
        self._task_end[vid] = clock()

    def tasks(self):
        """ Iterate on all tasks and evaluation times.

        return:
            - iter of (vid,(float|float)): tuple of task id, (tinit, tend)
        """
        for vid in self._dataflow.vertices():
            yield vid, (self._task_start[vid], self._task_end[vid])
