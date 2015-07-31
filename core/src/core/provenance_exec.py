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


from time import clock

from dataflow_state import DataflowState


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
        self._time = {}
        self._stored = {}

    def clock(self):
        """ Convenience function provided
        to ensure everybody use the same time function.
        """
        return clock()

    def clear(self):
        """ Remove all data stored in the provenance.
        """
        self._time.clear()
        self._stored.clear()

    def dataflow(self):
        """ Return reference on surveyed dataflow.
        """
        return self._dataflow

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
                                     same as state but updated.
        """
        if state is None:
            state = DataflowState(self.dataflow())
        else :
            assert state.dataflow() == self.dataflow()

        state.clear()
        state.update(self._stored[exec_id])

        return state

    def get_task(self, exec_id, vid):
        """ Retrieve stored time of execution for a given task.

        args:
            - exec_id (eid): id of execution
            - vid (vid): if of task

        return:
            - (float, float): (t_start, t_end)
        """
        return self._time[exec_id][vid]

    def record_task(self, exec_id, vid, t_start, t_end):
        """ Register execution times of a task.

        args:
            - exec_id (eid): current execution
            - vid (vid): id of task performed
            - t_start (float): time of beginning of task
            - t_end (float): time of end of task
        """
        td = self._time.setdefault(exec_id, {})
        if vid in td:
            raise KeyError("Task already registered during this execution")

        td[vid] = (t_start, t_end)


    def store(self, exec_id, state):
        """ Store a copy of state.

        args:
            - exec_id (eid): unique id for a given execution
            - state (DataFlowState): a state to store
        """
        if exec_id in self._stored:
            raise KeyError("execution already stored")

        self._stored[exec_id] = dict(state.items())
