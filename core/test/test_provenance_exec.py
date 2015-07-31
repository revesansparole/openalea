from nose.tools import assert_raises
from time import sleep

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.provenance_exec import ProvenanceExec


def test_prov_exec_init():
    df = []
    prov = ProvenanceExec(df)

    assert id(prov.dataflow()) == id(df)
    prov.clear()
    assert id(prov.dataflow()) == id(df)


def test_prov_exec_clock():
    prov = ProvenanceExec(None)

    t1 = prov.clock()
    sleep(0.1)
    assert prov.clock() > t1


def test_prov_exec_new_execution():
    prov = ProvenanceExec(None)

    assert_raises(KeyError, lambda: prov.new_execution(0))
    eid1 = prov.new_execution()
    eid2 = prov.new_execution()
    assert eid1 != eid2
    eid3 = prov.new_execution(eid1)
    assert eid1 != eid3


def test_prov_exec_parent_execution():
    prov = ProvenanceExec(None)

    eid1 = prov.new_execution()
    assert prov.parent_execution(eid1) is None
    eid2 = prov.new_execution()
    assert prov.parent_execution(eid2) is None
    eid3 = prov.new_execution(eid1)
    assert prov.parent_execution(eid3) == eid1
    eid4 = prov.new_execution(eid1)
    assert prov.parent_execution(eid4) == eid1


def test_prov_exec_contains():
    dfs = DataflowState(None)

    prov = ProvenanceExec(None)
    assert 0 not in prov

    assert_raises(KeyError, lambda: prov.store(0, dfs))

    eid = prov.new_execution()
    prov.store(eid, dfs)

    assert eid in prov


def test_prov_exec_record_task():
    prov = ProvenanceExec(None)
    assert_raises(KeyError, lambda: prov.record_task(0, 0, 1, 2))

    eid = prov.new_execution()
    prov.record_task(eid, 0, 1, 2)

    assert_raises(KeyError, lambda: prov.record_task(eid, 0, 1, 2))
    assert_raises(KeyError, lambda: prov.record_task(eid, 0, 2, 3))
    prov.record_task(eid, 1, 3, 4)
    eid2 = prov.new_execution()
    prov.record_task(eid2, 0, 4, 5)

    assert prov.get_task(eid, 0) == (1, 2)
    assert prov.get_task(eid, 1) == (3, 4)
    assert prov.get_task(eid2, 0) == (4, 5)
    assert_raises(KeyError, lambda: prov.get_task(eid2, 1))
    assert_raises(KeyError, lambda: prov.get_task(2, 0))


def test_prov_exec_store():
    dfs = DataflowState(None)

    prov = ProvenanceExec(None)
    eid = prov.new_execution()

    prov.store(eid, dfs)

    assert_raises(KeyError, lambda: prov.store(eid, dfs))


def test_prov_exec_get_state():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")
    pid1 = df.add_out_port(vid, "out")
    prov = ProvenanceExec(df)

    # try to retrieve non existing execution id
    assert_raises(KeyError, lambda: prov.get_state(0))

    dfs = DataflowState(df)
    dfs.set_data(pid0, 'a')
    eid = prov.new_execution()
    prov.store(eid, dfs)

    state = prov.get_state(eid)
    assert id(state.dataflow()) == id(df)

    # test that passing a state as argument overwrite given state
    dfs2 = DataflowState(df)
    state2 = prov.get_state(eid, dfs2)
    assert id(state2) == id(dfs2)
    assert id(state2) != id(dfs)
    assert state2.get_data(pid0) == 'a'

    # test that each execution id is a different state object
    eid2 = prov.new_execution()
    dfs.set_data(pid1, 'b')
    prov.store(eid2, dfs)
    state3 = prov.get_state(eid2)
    assert id(state3) != id(dfs)
    assert_raises(KeyError, lambda: state2.get_data(pid1))

    state4 = prov.get_state(eid, state3)
    assert id(state4) == id(state3)
    assert_raises(KeyError, lambda: state3.get_data(pid1))
    assert state3.get_data(pid0) == 'a'


def test_prov_exec_get_state_with_changed():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")
    pid1 = df.add_out_port(vid, "out")
    prov = ProvenanceExec(df)

    dfs = DataflowState(df)
    dfs.set_data(pid0, 'a')
    dfs.set_data(pid1, 'b')
    dfs.set_changed(pid1, False)
    eid = prov.new_execution()
    prov.store(eid, dfs)

    state = prov.get_state(eid)
    for pid in (pid0, pid1):
        assert dfs.has_changed(pid) == state.has_changed(pid)


# def test_prov_exec_with_lazy():
#     df, (pid_in, pid_out) = get_dataflow()
#     prov = ProvenanceExec(df)
#
#     # first execution
#     dfs = DataflowState(df)
#     for pid in df.out_ports():
#         dfs.set_data(pid, pid)
#
#     dfs.set_data(pid_in, 'a')
#     # assert dfs.is_valid()
#
#     prov.store(0, dfs)
#     for vid in dfs.vertices():
#         prov.record_task(0, vid, vid, vid + 1)
#
#     #second execution
#
#
