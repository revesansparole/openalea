from nose.tools import assert_raises
from time import sleep

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.node import Node
from openalea.core.subdataflow import SubDataflow2


def get_dataflow():
    df = DataFlow()
    vid1 = df.add_vertex()
    pid10 = df.add_in_port(vid1, "in")
    pid11 = df.add_out_port(vid1, "out")
    vid2 = df.add_vertex()
    pid21 = df.add_out_port(vid2, "out")
    vid5 = df.add_vertex()
    pid51 = df.add_out_port(vid5, "out")

    vid3 = df.add_vertex()
    pid31 = df.add_in_port(vid3, "in1")
    pid32 = df.add_in_port(vid3, "in2")
    pid33 = df.add_out_port(vid3, "res")

    vid4 = df.add_vertex()
    pid41 = df.add_in_port(vid4, "in")

    df.connect(pid11, pid31)
    df.connect(pid21, pid32)
    df.connect(pid33, pid41)
    df.connect(pid51, pid32)

    vids = [vid1, vid2, vid3, vid4, vid5]
    pids = [pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51]
    return df, vids, pids


def test_dataflow_state_init():
    df, vids, pids = get_dataflow()
    dfs = DataflowState(df)
    dfs.clear()

    assert len(tuple(dfs.items())) == 0
    assert id(dfs.dataflow()) == id(df)
    d = dict(dfs.tasks())
    assert set(d) == set(vids)


def test_dataflow_state_reinit():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids

    dfs = DataflowState(df)

    dfs.set_data(pid10, 0)

    for i, pid in enumerate([pid11, pid21, pid33]):
        dfs.set_data(pid, i)

    dfs.reinit()
    assert dfs.is_ready_for_evaluation()
    for pid in (pid11, pid21, pid33):
        assert_raises(KeyError, lambda: dfs.get_data(pid))


def test_dataflow_state_reinit_with_changed():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids

    dfs = DataflowState(df)

    dfs.set_data(pid10, 0)
    dfs.set_changed(pid10, False)

    for i, pid in enumerate([pid11, pid21, pid33]):
        dfs.set_data(pid, i)

    dfs.reinit()
    for pid in (pid11, pid21, pid33):
        assert_raises(KeyError, lambda: dfs.has_changed(pid))

    assert not dfs.has_changed(pid10)


def test_dataflow_state_update():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    vid1, vid2, vid3, vid4, vid5 = vids

    dfs1 = DataflowState(df)
    dfs1.set_data(pid10, 0)
    dfs1.set_changed(pid10, False)

    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        dfs1.set_data(pid, i)

    assert dfs1.is_valid()

    dfs2 = DataflowState(df)
    dfs2.set_data(pid10, 10)
    dfs2.set_data(pid11, 10)
    dfs2.set_changed(pid11, False)

    dfs1.update(dfs2)
    assert dfs1.get_data(pid10) == 10
    assert dfs1.has_changed(pid10)
    assert dfs1.get_data(pid11) == 10
    assert not dfs1.has_changed(pid11)
    assert dfs1.get_data(pid21) == 1
    assert dfs1.get_data(pid33) == 2
    assert dfs1.get_data(pid51) == 3
    assert dfs1.has_changed(pid21)
    assert dfs1.has_changed(pid33)
    assert dfs1.has_changed(pid51)

    sub = SubDataflow2(df, (vid1, vid3))
    dfs3 = DataflowState(sub)
    dfs3.set_data(pid10, 20)
    dfs3.set_changed(pid10, False)
    dfs3.set_data(pid11, 20)

    dfs1.update(dfs3)
    assert dfs1.get_data(pid10) == 20
    assert not dfs1.has_changed(pid10)
    assert dfs1.get_data(pid11) == 20
    assert dfs1.has_changed(pid11)
    assert dfs1.get_data(pid21) == 1
    assert dfs1.get_data(pid33) == 2
    assert dfs1.get_data(pid51) == 3
    assert dfs1.has_changed(pid21)
    assert dfs1.has_changed(pid33)
    assert dfs1.has_changed(pid51)


def test_dataflow_state_is_ready_for_evaluation():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    assert not dfs.is_ready_for_evaluation()

    dfs.set_data(pid10, 0)

    assert dfs.is_ready_for_evaluation()

    dfs.clear()
    for i, pid in enumerate([pid11, pid21, pid33]):
        dfs.set_data(pid, i)
        assert not dfs.is_ready_for_evaluation()


def test_dataflow_state_is_valid():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    assert not dfs.is_valid()

    dfs.set_data(pid10, 0)

    assert not dfs.is_valid()

    dfs.clear()
    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        dfs.set_data(pid, i)
        assert not dfs.is_valid()

    dfs.set_data(pid10, 'a')
    assert dfs.is_valid()


def test_dataflow_state_is_valid_against():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    vid1, vid2, vid3, vid4, vid5 = vids
    dfs = DataflowState(df)
    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        dfs.set_data(pid, i)
        assert not dfs.is_valid()

    dfs.set_data(pid10, 'a')
    assert dfs.is_valid_against(dfs.dataflow())

    sub = SubDataflow2(df, (vid3,))
    dfs = DataflowState(sub)
    dfs.set_data(pid31, None)
    dfs.set_data(pid32, None)
    dfs.set_data(pid33, None)
    assert dfs.is_valid()
    assert not dfs.is_valid_against(df)

    sub = SubDataflow2(df, (vid1,))
    dfs = DataflowState(sub)
    dfs.set_data(pid10, None)
    dfs.set_data(pid11, None)
    assert dfs.is_valid()
    assert dfs.is_valid_against(df)

    sub = SubDataflow2(df, (vid1, vid3))
    dfs = DataflowState(sub)
    dfs.set_data(pid10, None)
    dfs.set_data(pid11, None)
    dfs.set_data(pid32, None)
    dfs.set_data(pid33, None)
    assert dfs.is_valid()
    assert not dfs.is_valid_against(df)

    sub = SubDataflow2(df, (vid1, vid2, vid3, vid5))
    dfs = DataflowState(sub)
    dfs.set_data(pid10, None)
    dfs.set_data(pid11, None)
    dfs.set_data(pid21, None)
    dfs.set_data(pid51, None)
    dfs.set_data(pid33, None)
    assert dfs.is_valid()
    assert dfs.is_valid_against(df)


def test_dataflow_state_items():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    assert len(tuple(dfs.items())) == 0

    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        dfs.set_data(pid, i)

    assert len(tuple(dfs.items())) == 4

    dfs.set_data(pid10, 'a')
    assert len(tuple(dfs.items())) == 5

    d = dict((pid, i) for i, pid in enumerate([pid11, pid21, pid33, pid51]))
    d[pid10] = 'a'
    assert dict(dfs.items()) == d


def test_dataflow_state_set_data():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    # allowed to set data on param in ports
    dfs.set_data(pid10, None)
    assert dfs.has_changed(pid10)

    # not allowed to set data on non param in ports
    for pid in (pid31, pid41):
        assert_raises(KeyError, lambda: dfs.set_data(pid, None))

    # allowed to set data in out ports
    for pid in (pid21, pid33, pid51):
        dfs.set_data(pid, None)
        assert dfs.has_changed(pid)


def test_dataflow_state_get_data():
    df, vids, pids = get_dataflow()
    vid1, vid2, vid3, vid4, vid5 = vids
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    for pid in df.ports():
        assert_raises(KeyError, lambda: dfs.get_data(pid))

    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        dfs.set_data(pid, i)

    assert_raises(KeyError, lambda: dfs.get_data(pid10))

    dfs.set_data(pid10, 'a')
    assert dfs.get_data(pid10) == 'a'

    for i, pid in enumerate([pid11, pid21, pid33, pid51]):
        assert dfs.get_data(pid) == i

    assert dfs.get_data(pid31) == 0
    assert tuple(dfs.get_data(pid32)) == (1, 3)
    assert dfs.get_data(pid41) == 2

    n2 = Node()
    df.set_actor(vid2, n2)

    assert tuple(dfs.get_data(pid32)) == (1, 3)

    n5 = Node()
    df.set_actor(vid5, n5)
    assert tuple(dfs.get_data(pid32)) == (1, 3)

    n2.get_ad_hoc_dict().set_metadata('position', [10, 0])
    n5.get_ad_hoc_dict().set_metadata('position', [0, 0])
    assert tuple(dfs.get_data(pid32)) == (3, 1)


def test_dataflow_state_changed():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    dfs.set_data(pid10, 'a')
    assert dfs.has_changed(pid10)
    assert_raises(KeyError, lambda: dfs.has_changed(pid11))
    assert_raises(KeyError, lambda: dfs.set_changed(pid31, False))
    assert_raises(KeyError, lambda: dfs.set_changed(pid51, False))

    for pid in (pid11, pid21, pid33, pid51):
        dfs.set_data(pid, pid)
        assert dfs.has_changed(pid)

    dfs.set_changed(pid21, False)
    assert not dfs.has_changed(pid21)
    assert dfs.has_changed(pid10)


def test_dataflow_state_input_has_changed():
    df, vids, pids = get_dataflow()
    pid10, pid11, pid21, pid31, pid32, pid33, pid41, pid51 = pids
    dfs = DataflowState(df)

    dfs.set_data(pid10, 'a')

    for pid in (pid11, pid21, pid33, pid51):
        dfs.set_data(pid, pid)

    dfs.set_changed(pid21, False)

    assert_raises(KeyError, lambda: dfs.input_has_changed(pid21))
    assert dfs.input_has_changed(pid10)
    assert dfs.input_has_changed(pid31)
    assert dfs.input_has_changed(pid32)
    assert dfs.input_has_changed(pid41)

    dfs.set_changed(pid11, False)
    assert not dfs.input_has_changed(pid31)

    dfs.set_changed(pid10, False)
    assert not dfs.input_has_changed(pid10)

    dfs.set_changed(pid51, False)
    assert not dfs.input_has_changed(pid32)


def test_dataflow_state_start_task():
    df, vids, pids = get_dataflow()
    vid1, vid2, vid3, vid4, vid5 = vids
    dfs = DataflowState(df)

    assert dfs.task_start_time(vid1) is None
    assert dfs.task_end_time(vid1) is None

    dfs.task_started(vid1)
    sleep(0.01)
    dfs.task_ended(vid1)

    dfs.set_task_start_time(vid2, 1)
    dfs.set_task_end_time(vid2, 2)

    t0 = dfs.task_start_time(vid1)
    t1 = dfs.task_end_time(vid1)
    assert t1 > t0

    assert dfs.task_start_time(vid2) == 1
    assert dfs.task_end_time(vid2) == 2

    dfs.reinit()
    for vid in vids:
        assert dfs.task_start_time(vid) is None
        assert dfs.task_end_time(vid) is None
