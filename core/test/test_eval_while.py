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
from openalea.core.node import Node, FuncNodeSingle
from openalea.core.node_control_flow import WhileNode


class Session(object):  # Hack to maintain some values
    def __init__(self):
        self.counter = 0
        self.task0 = 0
        self.task1 = 0
        self.task2 = 0


def test_while_simple():
    session = Session()

    df = DataFlow()

    def task0():
        session.task0 += 1
        ret = session.counter
        session.counter += 1
        return ret

    n0 = FuncNodeSingle((), ({'name': 'out'},), task0)
    n0.set_lazy(False)
    df.add_actor(n0)

    def task1(a):
        session.task1 += 1
        return a < 5

    n1 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task1)
    df.add_actor(n1)

    def task2():
        session.task2 += 1
        return 0

    n2 = FuncNodeSingle((), ({'name': 'out'},), task2)
    n2.set_lazy(False)
    df.add_actor(n2)

    n3 = WhileNode()
    df.add_actor(n3)

    df.connect(0, 1)
    df.connect(2, 4)
    df.connect(3, 5)


    state = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)
    algo.eval(env, state)

    assert tuple(state.get_data(6)) == (0, 0, 0, 0, 0)
    assert state.has_changed(6)
    assert session.task0 == 6
    assert session.task1 == 6
    assert session.task2 == 5


def test_while_diamond():
    df = DataFlow()

    session = Session()

    def task0():
        session.task0 += 1
        ret = session.counter
        session.counter += 1
        return ret

    def task1(a):
        session.task1 += 1
        return a < 5

    def task2(a):
        session.task2 += 1
        return a * 2


    n0 = FuncNodeSingle((), ({'name': 'out'},), task0)
    n0.set_lazy(False)
    df.add_actor(n0, 0)

    n1 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task1)
    df.add_actor(n1, 1)

    n2 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task2)
    df.add_actor(n2, 2)

    n3 = WhileNode()
    df.add_actor(n3, 3)


    df.connect(0, 1)
    df.connect(0, 3)
    df.connect(2, 5)
    df.connect(4, 6)

    state = DataflowState(df)

    env = EvaluationEnvironment()
    algo = LazyEvaluation(df)
    algo.eval(env, state)
    assert tuple(state.get_data(7)) == (0, 2, 4, 6, 8)
    assert state.has_changed(7)
    assert session.task0 == 6
    assert session.task1 == 6
    assert session.task2 == 5
