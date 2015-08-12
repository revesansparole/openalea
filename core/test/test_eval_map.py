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
from openalea.core.node_control_flow import MapNode, XNode


class Session(object):  # Hack to maintain some values
    def __init__(self):
        self.counter = 0
        self.task0 = 0
        self.task1 = 0
        self.task2 = 0


def test_map_simple_no_args():
    session = Session()

    df = DataFlow()
    ip = df.in_port
    op = df.out_port

    def task1():
        session.task1 += 1
        return 0

    n0 = FuncNodeSingle((), ({'name': 'out'},), task1)
    n0.set_lazy(False)
    df.add_actor(n0, 0)

    def task2():
        session.task2 += 1
        return [0, 1, 2]

    n1 = FuncNodeSingle((), ({'name': 'out'},), task2)
    df.add_actor(n1, 1)

    n2 = MapNode()
    df.add_actor(n2, 2)

    df.connect(op(0, "out"), ip(2, "func"))
    df.connect(op(1, "out"), ip(2, "seq"))


    state = DataflowState(df)

    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)
    algo.eval(env, state)

    assert tuple(state.get_data(op(2, "out"))) == (0, 0, 0)
    assert state.has_changed(op(2, "out"))
    assert session.task1 == 3
    assert session.task2 == 1


def test_map_simple_x():
    session = Session()

    df = DataFlow()
    ip = df.in_port
    op = df.out_port

    n0 = XNode()
    df.add_actor(n0, 0)

    def task1(a):
        session.task1 += 1
        return a * 5

    n1 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task1)
    df.add_actor(n1, 1)

    def task2():
        session.task2 += 1
        return [0, 1, 2]

    n2 = FuncNodeSingle((), ({'name': 'out'},), task2)
    df.add_actor(n2, 2)

    n3 = MapNode()
    df.add_actor(n3, 3)

    df.connect(op(0, "out"), ip(1, "in"))
    df.connect(op(1, "out"), ip(3, "func"))
    df.connect(op(2, "out"), ip(3, "seq"))


    state = DataflowState(df)
    state.set_data(ip(0, "order"), 0)

    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)
    algo.eval(env, state)

    assert tuple(state.get_data(op(3, "out"))) == (0, 5, 10)
    assert state.has_changed(op(3, "out"))
    assert session.task1 == 3
    assert session.task2 == 1


def test_eval_map_double_x():
    session = Session()

    df = DataFlow()
    ip = df.in_port
    op = df.out_port

    n0 = XNode()
    df.add_actor(n0, 0)
    n1 = XNode()
    df.add_actor(n1, 1)

    def task1(a, b):
        session.task1 += 1
        return a + b

    n2 = FuncNodeSingle(({'name': 'in1'}, {'name': 'in2'}),
                        ({'name': 'out'},),
                        task1)
    df.add_actor(n2, 2)

    def task2():
        session.task2 += 1
        return [('a', 'b'), ('c', 'd')]

    n3 = FuncNodeSingle((), ({'name': 'out'},), task2)
    df.add_actor(n3, 3)

    n4 = MapNode()
    df.add_actor(n4, 4)

    df.connect(op(0, "out"), ip(2, "in1"))
    df.connect(op(1, "out"), ip(2, "in2"))
    df.connect(op(2, "out"), ip(4, "func"))
    df.connect(op(3, "out"), ip(4, "seq"))


    state = DataflowState(df)
    state.set_data(ip(0, "order"), 0)
    state.set_data(ip(1, "order"), 1)

    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)
    algo.eval(env, state)

    assert tuple(state.get_data(op(4, "out"))) == ('ab', 'cd')
    assert state.has_changed(op(4, "out"))
    assert session.task1 == 2
    assert session.task2 == 1

    state = DataflowState(df)
    state.set_data(ip(0, "order"), 1)
    state.set_data(ip(1, "order"), 0)

    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)
    algo.eval(env, state)

    assert tuple(state.get_data(op(4, "out"))) == ('ba', 'dc')
    assert state.has_changed(op(4, "out"))
    assert session.task1 == 4
    assert session.task2 == 2

# def test_for_diamond():
#     df = DataFlow()
#
#     session = Session()
#
#     def task0():
#         session.task0 += 1
#         ret = session.counter
#         session.counter += 1
#         return ret
#
#     def task1(a):
#         session.task1 += 1
#         if a >= 5:
#             raise StopIteration()
#
#     def task2(a):
#         session.task2 += 1
#         return a * 2
#
#
#     n0 = FuncNodeSingle((), ({'name': 'out'},), task0)
#     n0.set_lazy(False)
#     df.add_actor(n0, 0)
#
#     n1 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task1)
#     df.add_actor(n1, 1)
#
#     n2 = FuncNodeSingle(({'name': 'in'},), ({'name': 'out'},), task2)
#     df.add_actor(n2, 2)
#
#     n3 = ForNode()
#     df.add_actor(n3, 3)
#
#
#     df.connect(0, 1)
#     df.connect(0, 3)
#     df.connect(2, 5)
#     df.connect(4, 6)
#
#     state = DataflowState(df)
#
#     env = EvaluationEnvironment()
#     algo = LazyEvaluation(df)
#     algo.eval(env, state)
#     assert tuple(state.get_data(7)) == (0, 2, 4, 6, 8)
#     assert state.has_changed(7)
#     assert session.task0 == 6
#     assert session.task1 == 6
#     assert session.task2 == 5
