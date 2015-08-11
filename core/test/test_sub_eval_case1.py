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
from openalea.core.node import FuncNodeSingle
from openalea.core.subdataflow import SubDataflow2


def test_eval_case1():
    class Count(object):
        pass

    count = Count()
    count.func0 = 0
    count.func1 = 0
    count.func2 = 0
    count.func3 = 0

    df = DataFlow()

    def func0():
        count.func0 += 1
        return 0

    n0 = FuncNodeSingle((), ({'name': "out"},), func0)
    vid0 = df.add_actor(n0)

    def func1(a):
        count.func1 += 1
        return 1 + a

    n1 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func1)
    vid1 = df.add_actor(n1)

    def func2(a):
        count.func2 += 1
        return 2 + a

    n2 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func2)
    vid2 = df.add_actor(n2)

    def func3(a):
        count.func3 += 1
        return a

    n3 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func3)
    df.add_actor(n3)

    df.connect(0, 1)
    df.connect(0, 3)
    df.connect(2, 5)
    df.connect(4, 5)

    state = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)

    # Classic evaluation of the full dataflow
    algo.eval(env, state)
    assert count.func0 == 1
    assert count.func1 == 1
    assert count.func2 == 1
    assert count.func3 == 1

    sub1 = SubDataflow2(df, (vid0, vid1))
    sub2 = SubDataflow2(df, (vid0, vid2))

    ss = DataflowState(df)
    ss1 = DataflowState(sub1)
    ss2 = DataflowState(sub2)
    env = EvaluationEnvironment(0)

    # single evaluation of sub1
    ss1.update(ss)
    a1 = LazyEvaluation(sub1)
    a1.eval(env, ss1)
    ss.update(ss1)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 1
    assert count.func3 == 1

    # single evaluation of sub2
    ss2.update(ss)
    a2 = LazyEvaluation(sub2)
    a2.eval(env, ss2)
    ss.update(ss2)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 2
    assert count.func3 == 1

    # evaluation of the full dataflow based
    # on the two previous evaluations
    a3 = LazyEvaluation(df)
    a3.eval(env, ss)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 2
    assert count.func3 == 2

    for pid in df.out_ports():
        assert state.get_data(pid) == ss.get_data(pid)


def test_eval_case1_non_lazy():
    class Count(object):
        pass

    count = Count()
    count.func0 = 0
    count.func1 = 0
    count.func2 = 0
    count.func3 = 0

    df = DataFlow()

    def func0():
        count.func0 += 1
        return 0

    n0 = FuncNodeSingle((), ({'name': "out"},), func0)
    n0.set_lazy(False)
    vid0 = df.add_actor(n0)

    def func1(a):
        count.func1 += 1
        return 1 + a

    n1 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func1)
    vid1 = df.add_actor(n1)

    def func2(a):
        count.func2 += 1
        return 2 + a

    n2 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func2)
    vid2 = df.add_actor(n2)

    def func3(a):
        count.func3 += 1
        return a

    n3 = FuncNodeSingle(({'name': "in"},), ({'name': "out"},), func3)
    df.add_actor(n3)

    df.connect(0, 1)
    df.connect(0, 3)
    df.connect(2, 5)
    df.connect(4, 5)

    state = DataflowState(df)
    env = EvaluationEnvironment(0)
    algo = LazyEvaluation(df)

    # Classic evaluation of the full dataflow
    algo.eval(env, state)
    assert count.func0 == 1
    assert count.func1 == 1
    assert count.func2 == 1
    assert count.func3 == 1

    # Evaluation by pieces
    sub1 = SubDataflow2(df, (vid0, vid1))
    sub2 = SubDataflow2(df, (vid0, vid2))

    ss = DataflowState(df)
    ss1 = DataflowState(sub1)
    ss2 = DataflowState(sub2)
    env = EvaluationEnvironment(0)

    # single evaluation of sub1
    ss1.update(ss)
    a1 = LazyEvaluation(sub1)
    a1.eval(env, ss1)
    ss.update(ss1)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 1
    assert count.func3 == 1

    # single evaluation of sub2
    ss2.update(ss)
    a2 = LazyEvaluation(sub2)
    a2.eval(env, ss2)
    ss.update(ss2)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 2
    assert count.func3 == 1

    # evaluation of the full dataflow based
    # on the two previous evaluations
    a3 = LazyEvaluation(df)
    a3.eval(env, ss)
    assert count.func0 == 2
    assert count.func1 == 2
    assert count.func2 == 2
    assert count.func3 == 2

    for pid in df.out_ports():
        assert state.get_data(pid) == ss.get_data(pid)
