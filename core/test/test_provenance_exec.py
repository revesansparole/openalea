from nose.tools import assert_raises

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.provenance_exec import ProvenanceExec
from openalea.core.subdataflow import SubDataflow2


def test_prov_exec_init():
    df = []
    prov = ProvenanceExec(df)

    assert id(prov.dataflow()) == id(df)
    prov.clear()
    assert id(prov.dataflow()) == id(df)


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
    df = DataFlow()
    dfs = DataflowState(df)

    prov = ProvenanceExec(None)
    assert 0 not in prov

    assert_raises(KeyError, lambda: prov.store(0, dfs))

    eid = prov.new_execution()
    prov.store(eid, dfs)

    assert eid in prov


def test_prov_exec_store():
    df = DataFlow()
    dfs = DataflowState(df)

    prov = ProvenanceExec(None)
    eid = prov.new_execution()

    prov.store(eid, dfs)

    assert_raises(KeyError, lambda: prov.store(eid, dfs))


def test_prov_exec_store_subdataflow():
    df = DataFlow()
    vid1 = df.add_vertex()
    pid1 = df.add_out_port(vid1, "out")
    vid2 = df.add_vertex()
    pid2 = df.add_in_port(vid2, "in")
    df.connect(pid1, pid2)

    sub = SubDataflow2(df, (vid2,))
    state = DataflowState(sub)
    state.set_data(pid2, None)

    assert state.is_valid()

    prov = ProvenanceExec(df)
    eid = prov.new_execution()
    assert_raises(UserWarning, lambda: prov.store(eid, state))


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


def test_prov_exec_get_state_with_task():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, "in")
    pid1 = df.add_out_port(vid, "out")
    prov = ProvenanceExec(df)

    dfs = DataflowState(df)
    dfs.set_data(pid0, 'a')
    dfs.set_data(pid1, 'b')
    dfs.set_changed(pid1, False)
    dfs.task_started(vid)
    eid = prov.new_execution()
    prov.store(eid, dfs)

    state = prov.get_state(eid)
    assert state.task_start_time(vid) == dfs.task_start_time(vid)
    assert state.task_end_time(vid) is None
    assert not state.task_already_evaluated(vid)

    state.set_task_already_evaluated(vid)
    eid = prov.new_execution()
    prov.store(eid, state)

    state2 = prov.get_state(eid)
    assert state2.task_already_evaluated(vid)


def test_prov_exec_last_evaluation():
    df = DataFlow()
    vid = df.add_vertex()
    prov = ProvenanceExec(df)

    assert_raises(UserWarning, lambda: prov.last_evaluation(vid))

    dfs = DataflowState(df)

    eid = prov.new_execution()
    prov.store(eid, dfs)

    state = prov.get_state(eid)
    assert state.task_start_time(vid) is None
    assert_raises(UserWarning, lambda: prov.last_evaluation(vid, eid))

    prov.clear()
    eid = prov.new_execution()
    dfs.task_started(vid)
    prov.store(eid, dfs)
    dfs.set_task_start_time(vid, None)

    peid = eid
    for i in range(4):
        peid = prov.new_execution(peid)
        prov.store(peid, dfs)

    assert prov.last_evaluation(vid, peid) == eid
    assert prov.last_evaluation(vid) == eid


def test_prov_exec_last_evaluation_fork():
    df = DataFlow()
    vid = df.add_vertex()
    prov = ProvenanceExec(df)

    assert_raises(UserWarning, lambda: prov.last_evaluation(vid))

    dfs = DataflowState(df)

    eid = prov.new_execution()
    prov.store(eid, dfs)

    state = prov.get_state(eid)
    assert state.task_start_time(vid) is None
    assert_raises(UserWarning, lambda: prov.last_evaluation(vid, eid))

    prov.clear()
    eid = prov.new_execution()
    dfs.task_started(vid)
    prov.store(eid, dfs)
    dfs.set_task_start_time(vid, None)

    eids = [eid]
    for i in range(4):
        eids.append(prov.new_execution(eids[-1]))
        prov.store(eids[-1], dfs)

    eids.append(prov.new_execution(eids[2]))
    dfs.task_started(vid)
    prov.store(eids[-1], dfs)
    dfs.set_task_start_time(vid, None)

    for i in range(4):
        eids.append(prov.new_execution(eids[-1]))
        prov.store(eids[-1], dfs)

    assert_raises(UserWarning, lambda: prov.last_evaluation(vid))

    # first branch
    for i in range(5):
        assert prov.last_evaluation(vid, eids[i]) == eids[0]

    # second branch
    for i in range(6, 10):
        assert prov.last_evaluation(vid, eids[i]) == eids[5]


def test_prov_exec_last_change():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, 'in')
    pid1 = df.add_out_port(vid0, 'out')
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, 'in')
    pid3 = df.add_out_port(vid1, 'out')
    df.connect(pid1, pid2)

    prov = ProvenanceExec(df)
    dfs = DataflowState(df)
    # for i, pid in enumerate([pid0, pid1, pid2, pid3]):
    #     dfs.set_data(pid, i)

    eid = prov.new_execution()
    assert_raises(KeyError, lambda: prov.last_change(pid0, eid))
    assert_raises(KeyError, lambda: prov.last_change(pid1, eid))
    assert_raises(KeyError, lambda: prov.last_change(pid2, eid))
    assert_raises(KeyError, lambda: prov.last_change(pid3, eid))

    prov.store(eid, dfs)
    assert_raises(KeyError, lambda: prov.last_change(pid0, eid))

    prov.clear()
    dfs.set_data(pid0, 0)
    dfs.set_data(pid1, 0)
    dfs.set_data(pid3, 0)
    dfs.set_changed(pid3, False)
    eid0 = prov.new_execution()
    prov.store(eid0, dfs)
    assert_raises(KeyError, lambda: prov.last_change(pid2, eid0))
    assert prov.last_change(pid0, eid0) == eid0
    assert prov.last_change(pid1, eid0) == eid0
    assert_raises(UserWarning, lambda: prov.last_change(pid3, eid0))

    eid1 = prov.new_execution(eid0)
    dfs.set_changed(pid0, False)
    dfs.set_changed(pid1, False)
    prov.store(eid1, dfs)
    assert prov.last_change(pid0, eid1) == eid0
    assert prov.last_change(pid1, eid1) == eid0

    eid2 = prov.new_execution(eid1)
    dfs.set_changed(pid0, True)
    dfs.set_changed(pid1, True)
    prov.store(eid2, dfs)
    assert prov.last_change(pid0, eid2) == eid2
    assert prov.last_change(pid1, eid2) == eid2


def test_prov_exec_provenance_single_node():
    df = DataFlow()
    vid = df.add_vertex()
    pid0 = df.add_in_port(vid, 'in')
    pid1 = df.add_out_port(vid, 'out')

    prov = ProvenanceExec(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 0)
    dfs.set_data(pid1, 1)
    dfs.task_started(vid)

    eid = prov.new_execution()
    prov.store(eid, dfs)

    assert prov.provenance(pid0, eid) == (None, eid)

    assert_raises(KeyError, lambda: prov.provenance(pid1, eid + 1))
    assert prov.provenance(pid1, eid) == (vid, eid)


def test_prov_exec_provenance_two_nodes():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, 'in')
    pid1 = df.add_out_port(vid0, 'out')
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, 'in')
    pid3 = df.add_out_port(vid1, 'out')
    df.connect(pid1, pid2)

    prov = ProvenanceExec(df)
    dfs = DataflowState(df)
    dfs.set_data(pid0, 0)
    dfs.set_data(pid1, 1)
    dfs.set_data(pid3, 3)
    dfs.task_started(vid0)
    dfs.task_started(vid1)

    eid = prov.new_execution()
    prov.store(eid, dfs)

    assert prov.provenance(pid0, eid) == (None, eid)
    assert prov.provenance(pid1, eid) == (vid0, eid)
    assert prov.provenance(pid2, eid) == (pid1,)
    assert prov.provenance(pid3, eid) == (vid1, eid)


def test_prov_exec_last_eval_subdataflow():
    df = DataFlow()
    vid0 = df.add_vertex()
    pid0 = df.add_in_port(vid0, 'in')
    pid1 = df.add_out_port(vid0, 'out')
    vid1 = df.add_vertex()
    pid2 = df.add_in_port(vid1, 'in')
    pid3 = df.add_out_port(vid1, 'out')
    df.connect(pid1, pid2)

    sub = SubDataflow2(df, (vid0,))

    prov = ProvenanceExec(df)

    dfs1 = DataflowState(df)
    dfs1.set_data(pid0, 0)
    dfs1.set_data(pid1, 1)
    dfs1.set_data(pid3, 3)
    dfs1.task_started(vid0)
    dfs1.task_started(vid1)

    eid1 = prov.new_execution()
    prov.store(eid1, dfs1)

    dfs2 = DataflowState(sub)
    dfs2.set_data(pid0, 4)
    dfs2.set_data(pid1, 5)
    dfs2.task_started(vid0)

    eid2 = prov.new_execution(eid1)
    prov.store(eid2, dfs2)

    assert prov.last_evaluation(vid0, eid2) == eid2
    assert prov.last_evaluation(vid1, eid2) == eid1
    assert prov.last_evaluation(vid0, eid1) == eid1
    assert prov.last_evaluation(vid1, eid1) == eid1
