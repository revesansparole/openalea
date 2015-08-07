"""Workflow Tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises
import operator

from openalea.core.dataflow_evaluation import EvaluationError
from openalea.core.node import Node, FuncNodeRaw, FuncNodeSingle
from openalea.core.workflow import WorkFlow


def fixed_function():
    return 5


def print_func(*args):
    print "print_func", args
    return args,


def get_dataflow(df):
    df.clear()
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

    df.set_actor(vid1, FuncNodeSingle({}, {}, int))
    df.set_actor(vid2, FuncNodeSingle({}, {}, fixed_function))
    df.set_actor(vid3, FuncNodeSingle({}, {}, operator.add))
    df.set_actor(vid4, FuncNodeRaw({}, {}, print_func))

    return pid10, pid42


def test_workflow_init():
    wf = WorkFlow()
    df = wf.dataflow()

    assert df is not None
    assert id(wf.state().dataflow()) == id(df)
    assert id(wf.algo().dataflow()) == id(df)
    assert wf.eval_environment() is not None
    assert wf.eval_environment().provenance() is None

    wf = WorkFlow(with_provenance=True)
    df = wf.dataflow()

    assert df is not None
    assert id(wf.state().dataflow()) == id(df)
    assert id(wf.algo().dataflow()) == id(df)
    assert wf.eval_environment() is not None
    assert wf.eval_environment().record_provenance()
    assert id(wf.eval_environment().provenance().dataflow()) == id(df)


def test_workflow_eval():
    wf = WorkFlow()
    df = wf.dataflow()
    pid_in, pid_out = get_dataflow(df)

    assert_raises(EvaluationError, lambda: wf.new_evaluation())
    st = wf.state()
    st.set_data(pid_in, 1)

    wf.new_evaluation()
    assert st.get_data(pid_out) == (6,)


def test_workflow_reload():
    wf = WorkFlow()
    df = wf.dataflow()
    pid_in, pid_out = get_dataflow(df)
    st = wf.state()
    st.set_data(pid_in, 1)

    assert_raises(UserWarning, lambda: wf.reload(0))

    wf = WorkFlow(True)
    df = wf.dataflow()
    pid_in, pid_out = get_dataflow(df)
    st = wf.state()
    st.set_data(pid_in, 1)

    assert_raises(KeyError, lambda: wf.reload(0))

    eid1 = wf.new_evaluation()
    assert eid1 is not None
    mem1 = dict((pid, st.get_data(pid)) for pid in df.ports())
    assert_raises(KeyError, lambda: wf.reload(eid1 + 1))
    wf.reload(eid1)
    new_state = wf.state()
    assert mem1 == dict((pid, new_state.get_data(pid)) for pid in df.ports())

    wf.state().set_data(pid_in, 2)
    eid2 = wf.new_evaluation()
    mem2 = dict((pid, st.get_data(pid)) for pid in df.ports())
    new_state = wf.state()
    assert mem1 != dict((pid, new_state.get_data(pid)) for pid in df.ports())

    wf.reload(eid1)
    new_state = wf.state()
    assert mem1 == dict((pid, new_state.get_data(pid)) for pid in df.ports())

    wf.reload(eid2)
    new_state = wf.state()
    assert mem2 == dict((pid, new_state.get_data(pid)) for pid in df.ports())
