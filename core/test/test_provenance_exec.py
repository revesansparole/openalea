from nose.tools import assert_raises
import operator

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.dataflow_evaluation import (AbstractEvaluation,
                                               BruteEvaluation)
from openalea.core.node import Node, FuncNode
from openalea.core.provenance_exec import ProvenanceExec


def print_func(*args):
    print args


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

    df.connect(pid11, pid31)
    df.connect(pid21, pid32)
    df.connect(pid33, pid41)

    df.set_actor(vid1, FuncNode({}, {}, int))
    df.set_actor(vid2, FuncNode({}, {}, fixed_function))
    df.set_actor(vid3, FuncNode({}, {}, operator.add))
    df.set_actor(vid4, FuncNode({}, {}, print_func))

    return df, (pid10, pid42)


def test_prov_exec_init():
    df, (pid_in, pid_out) = get_dataflow()
    prov = ProvenanceExec(df)

    assert id(prov.dataflow()) == id(df)
    prov.clear()
    assert id(prov.dataflow()) == id(df)


def test_prov_exec_store():
    df, (pid_in, pid_out) = get_dataflow()
    dfs = DataflowState(df)

    prov = ProvenanceExec(df)
    prov.store(0, dfs)

    assert_raises(KeyError, lambda: prov.store(0, dfs))


def test_prov_exec_get_state():
    df, (pid_in, pid_out) = get_dataflow()
    prov = ProvenanceExec(df)

    # try to retrieve non existing execution id
    assert_raises(KeyError, lambda: prov.get_state(0))

    dfs = DataflowState(df)
    dfs.set_data(0, 'a')
    prov.store(0, dfs)

    state = prov.get_state(0)
    assert id(state.dataflow()) == id(df)

    # test that passing a state as argument overwrite given state
    dfs2 = DataflowState(df)
    state2 = prov.get_state(0, dfs2)
    assert id(state2) == id(dfs2)
    assert id(state2) != id(dfs)
    assert state2.get_data(0) == 'a'

    # test that each execution id is a different state object
    dfs.set_data(1, 'b')
    prov.store(1, dfs)
    state3 = prov.get_state(1)
    assert id(state3) != id(dfs)
    assert_raises(KeyError, lambda: state2.get_data(1))

    state4 = prov.get_state(0, state3)
    assert id(state4) == id(state3)
    assert_raises(KeyError, lambda: state3.get_data(1))
    assert state3.get_data(0) == 'a'
