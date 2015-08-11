# -*- python -*-
#
#       OpenAlea.SoftBus: OpenAlea Software Bus
#
#       Copyright 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
"""Test evaluation algorithm"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import LazyEvaluation
from openalea.core.dataflow_evaluation_environment import EvaluationEnvironment
from openalea.core.interface import IInt
from openalea.core.node import Node


class Counter(Node):
    def __init__(self):
        inputs = ()
        outputs = ({'name': 'out', 'interface': IInt},)
        Node.__init__(self, inputs, outputs)
        self._current = 0
        self.set_lazy(False)

    def reset(self):
        Node.reset(self)
        self._current = 0

    def __call__(self, *args):
        ret = self._current
        self._current += 1
        return ret


def test_eval_simple_counter():
    df = DataFlow()

    n0 = Counter()
    vid0 = df.add_actor(n0)

    state = DataflowState(df)
    env = EvaluationEnvironment()
    algo = LazyEvaluation(df)

    algo.clear()
    algo.eval(env, state)
    assert state.get_data(0) == 0
    algo.clear()
    algo.eval(env, state)
    assert state.get_data(0) == 1
    algo.clear()
    algo.eval(env, state)
    assert state.get_data(0) == 2

    n0.reset()
    algo.clear()
    algo.eval(env, state)
    assert state.get_data(0) == 0
