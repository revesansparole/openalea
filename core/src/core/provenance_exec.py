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


from openalea.core.dataflow_state import DataflowState


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
        self._stored = {}

    def clear(self):
        """ Remove all data stored in the provenance.
        """
        self._stored.clear()

    def dataflow(self):
        """ Return reference on surveyed dataflow.
        """
        return self._dataflow

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

    def store (self, exec_id, state):
        """ Store a copy of state.

        args:
            - exec_id (eid): unique id for a given execution
            - state (DataFlowState): a state to store
        """
        if exec_id in self._stored:
            raise KeyError("execution already stored")

        self._stored[exec_id] = dict(state.items())
