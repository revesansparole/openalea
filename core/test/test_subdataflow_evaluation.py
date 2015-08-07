from nose.tools import assert_raises
import operator

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import (EvaluationError,
                                               AbstractEvaluation,
                                               BruteEvaluation,
                                               LazyEvaluation)
from openalea.core.node import Node, FuncNodeRaw, FuncNodeSingle
from openalea.core.subdataflow import SubDataflow2


def print_func(*args):
    print "print_func", args
    return args,


def display_func(*args):
    print "print_func", args


def fixed_function():
    return 5


def double_fixed_function():
    return 5, 5


def get_dataflow():
    df = DataFlow()
    vid1 = df.add_vertex()
    pid10 = df.add_in_port(vid1, "in")
    pid11 = df.add_out_port(vid1, "out")
    vid2 = df.add_vertex()
    pid21 = df.add_out_port(vid2, "out")

    vid3 = df.add_vertex()
    pid31 = df.add_in_port(vid3, "in1")
    pid32 = df.add_in_port(vid3, "in2")
    pid33 = df.add_out_port(vid3, "res")

    vid4 = df.add_vertex()
    pid41 = df.add_in_port(vid4, "in")
    pid42 = df.add_out_port(vid4, "out")

    eid1 = df.connect(pid11, pid31)
    eid2 = df.connect(pid21, pid32)
    eid3 = df.connect(pid33, pid41)

    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.set_actor(vid2, FuncNodeSingle({}, {}, fixed_function))
    df.set_actor(vid3, FuncNodeSingle({}, {}, operator.add))
    df.set_actor(vid4, FuncNodeRaw({}, {}, print_func))

    pids = (pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid42)
    eids = (eid1, eid2, eid3)
    vids = (vid1, vid2, vid3, vid4)
    return df, pids, eids, vids


def test_subdataflow_state_update():
    assert False


def test_subdataflow_evaluation():
    df, pids, eids, vids = get_dataflow()
    vid1, vid2, vid3, vid4 = vids
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid42 = pids
    sub = SubDataflow2(df, (vid1, vid3))
    algo = BruteEvaluation(sub)

    env = None
    dfs = DataflowState(sub)
    dfs.set_data(pid10, 1)
    dfs.set_data(pid32, 5)

    assert not dfs.is_valid()
    algo.eval(env, dfs)
    assert dfs.is_valid()


# def test_subdataflow_eval_on_dataflow_state():
#     df, pids, eids, vids = get_dataflow()
#     vid1, vid2, vid3, vid4 = vids
#     pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid42 = pids
#     sub = SubDataflow2(df, (vid1, vid3))
#     algo = BruteEvaluation(sub)
#
#     env = None
#     dfs = DataflowState(df)
#     dfs.set_data(pid10, 1)
#     dfs.set_data(pid32, 5)
#
#     assert not dfs.is_valid()
#     algo.eval(env, dfs)
#     assert dfs.is_valid()
