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
""" This module provide an implementation of a workflow"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from dataflow import DataFlow
from dataflow_state import DataflowState
from dataflow_evaluation import BruteEvaluation
from dataflow_evaluation_environment import EvaluationEnvironment


class WorkFlow(object):
    """ A workflow associate a dataflow
    with a dataflow state and an evaluation algorithm.
    """
    def __init__(self, with_provenance=False):
        """ Constructor.

        Initialise an empty workflow ready for evaluation.

        args:
            - with_provenance (bool): flag to record provenance.
        """
        raise DeprecationWarning()

        df = DataFlow()
        self._dataflow = df
        self._state = DataflowState(df)
        self._algo = BruteEvaluation(df)
        self._eval_env = EvaluationEnvironment()

        if with_provenance:
            self._eval_env.set_provenance(df)

    def dataflow(self):
        """ Retrieve associated dataflow
        """
        return self._dataflow

    def state(self):
        """ Retrieve current state of workflow.
        """
        return self._state

    def algo(self):
        """ Retrieve current algorithm used to evaluate
        the dataflow.
        """
        return self._algo

    def eval_environment(self):
        """ Retrieve the evaluation environment
        """
        return self._eval_env

    def new_evaluation(self, vid=None):
        """ Compute a new evaluation of the workflow.
        """
        # reset
        self._algo.clear()

        # new evaluation
        self._eval_env.new_execution()

        # perform evaluation
        self._algo.eval(self._eval_env, self._state, vid)

        return self._eval_env.current_execution()

    def reload(self, exec_id):
        """ Reload a given execution state.

        args:
            - exec_id (eid): execution to reload
        """
        if not self._eval_env.record_provenance():
            raise UserWarning("Provenance not recorded")

        self._eval_env.provenance().get_state(exec_id, self._state)