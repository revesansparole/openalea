from nose.tools import assert_raises
from time import sleep

from openalea.core.dataflow import DataFlow
from openalea.core.dataflow_state import DataflowState
from openalea.core.node import Node
from openalea.core.subdataflow import SubDataflow2


def get_dataflow():
    df = DataFlow()
    df.add_vertex(0)
    df.add_in_port(0, "in", 0)
    df.add_out_port(0, "out", 1)
    df.add_vertex(1)
    df.add_out_port(1, "out", 2)
    df.add_vertex(4)
    df.add_out_port(4, "out", 7)

    df.add_vertex(2)
    df.add_in_port(2, "in1", 3)
    df.add_in_port(2, "in2", 4)
    df.add_out_port(2, "res", 5)

    df.add_vertex(3)
    df.add_in_port(3, "in", 6)

    df.connect(1, 3)
    df.connect(2, 4)
    df.connect(5, 6)
    df.connect(7, 4)

    return df


def test_dataflow_state_init():
    df = get_dataflow()
    dfs = DataflowState(df)
    dfs.clear()

    assert len(tuple(dfs.items())) == 0
    assert id(dfs.dataflow()) == id(df)


def test_dataflow_state_reinit():
    df = get_dataflow()

    dfs = DataflowState(df)

    dfs.set_data(0, 0)

    for i, pid in enumerate([1, 2, 5]):
        dfs.set_data(pid, i)

    dfs.reinit()
    assert dfs.is_ready_for_evaluation()
    for pid in (1, 2, 5):
        assert_raises(KeyError, lambda: dfs.get_data(pid))


def test_dataflow_state_reinit_with_changed():
    df = get_dataflow()

    dfs = DataflowState(df)

    dfs.set_data(0, 0)
    dfs.set_changed(0, False)

    for i, pid in enumerate([1, 2, 5]):
        dfs.set_data(pid, i)

    dfs.reinit()
    for pid in (1, 2, 5):
        assert_raises(KeyError, lambda: dfs.has_changed(pid))

    assert not dfs.has_changed(0)


def test_dataflow_state_update():
    df = get_dataflow()

    dfs1 = DataflowState(df)
    dfs1.set_data(0, 0)
    dfs1.set_changed(0, False)

    for i, pid in enumerate([1, 2, 5, 7]):
        dfs1.set_data(pid, i)

    dfs1.set_task_start_time(0, 1)
    dfs1.set_last_evaluation(1, 0)

    assert dfs1.is_valid()

    # update dataflow state with another dataflow state
    dfs2 = DataflowState(df)
    dfs2.set_data(0, 10)
    dfs2.set_data(1, 10)
    dfs2.set_changed(1, False)

    dfs1.update(dfs2)
    assert dfs1.get_data(0) == 10
    assert dfs1.has_changed(0)
    assert dfs1.get_data(1) == 10
    assert not dfs1.has_changed(1)
    assert dfs1.get_data(2) == 1
    assert dfs1.get_data(5) == 2
    assert dfs1.get_data(7) == 3
    assert dfs1.has_changed(2)
    assert dfs1.has_changed(5)
    assert dfs1.has_changed(7)
    assert dfs1.task_start_time(0) == 1
    assert dfs1.last_evaluation(0) is None
    assert dfs1.last_evaluation(1) == 0

    # update dataflow state with a subdataflow state
    sub = SubDataflow2(df, (0, 2))
    dfs3 = DataflowState(sub)
    dfs3.set_data(0, 20)
    dfs3.set_changed(0, False)
    dfs3.set_data(1, 20)
    dfs3.set_last_evaluation(2, 1)

    dfs1.update(dfs3)
    assert dfs1.get_data(0) == 20
    assert not dfs1.has_changed(0)
    assert dfs1.get_data(1) == 20
    assert dfs1.has_changed(1)
    assert dfs1.get_data(2) == 1
    assert dfs1.get_data(5) == 2
    assert dfs1.get_data(7) == 3
    assert dfs1.has_changed(2)
    assert dfs1.has_changed(5)
    assert dfs1.has_changed(7)
    assert dfs1.task_start_time(0) == 1
    assert dfs1.last_evaluation(0) is None
    assert dfs1.last_evaluation(1) == 0
    assert dfs1.last_evaluation(2) == 1

    # update subdataflow state with dataflow state
    dfs4 = DataflowState(sub)

    dfs4.update(dfs1)
    assert dfs4.get_data(0) == 20
    assert not dfs4.has_changed(0)
    assert dfs4.get_data(1) == 20
    assert dfs4.has_changed(1)
    assert dfs4.task_start_time(0) == 1
    assert dfs4.last_evaluation(0) is None
    assert dfs4.last_evaluation(2) == 1
    for pid in (2, 7, 6):
        assert pid not in dfs4


def test_dataflow_state_clone():
    df = get_dataflow()

    dfs1 = DataflowState(df)
    dfs1.set_data(0, 0)
    dfs1.set_changed(0, False)

    for i, pid in enumerate([1, 2, 5, 7]):
        dfs1.set_data(pid, i)

    dfs1.set_task_start_time(0, 1)
    dfs1.set_last_evaluation(1, 0)

    sub = SubDataflow2(df, (0, 2))
    dfs2 = dfs1.clone(sub)
    assert dfs2.task_start_time(0) == 1
    assert dfs2.get_data(0) == 0
    assert not dfs2.has_changed(0)
    assert dfs2.get_data(1) == 0
    assert 3 not in dfs2
    for pid in (2, 7, 6):
        assert pid not in dfs2


def test_dataflow_state_is_ready_for_evaluation():
    df = get_dataflow()
    dfs = DataflowState(df)

    assert not dfs.is_ready_for_evaluation()

    dfs.set_data(0, 0)

    assert dfs.is_ready_for_evaluation()

    dfs.clear()
    for i, pid in enumerate([1, 2, 5]):
        dfs.set_data(pid, i)
        assert not dfs.is_ready_for_evaluation()


def test_dataflow_state_is_valid():
    df = get_dataflow()
    dfs = DataflowState(df)

    assert not dfs.is_valid()

    dfs.set_data(0, 0)

    assert not dfs.is_valid()

    dfs.clear()
    for i, pid in enumerate([1, 2, 5, 7]):
        dfs.set_data(pid, i)
        assert not dfs.is_valid()

    dfs.set_data(0, 'a')
    assert dfs.is_valid()


def test_dataflow_state_is_valid_against():
    df = get_dataflow()
    dfs = DataflowState(df)
    for i, pid in enumerate([1, 2, 5, 7]):
        dfs.set_data(pid, i)
        assert not dfs.is_valid()

    dfs.set_data(0, 'a')
    assert dfs.is_valid_against(dfs.dataflow())

    sub = SubDataflow2(df, (2,))
    dfs = DataflowState(sub)
    dfs.set_data(3, None)
    dfs.set_data(4, None)
    dfs.set_data(5, None)
    assert dfs.is_valid()
    assert not dfs.is_valid_against(df)

    sub = SubDataflow2(df, (0,))
    dfs = DataflowState(sub)
    dfs.set_data(0, None)
    dfs.set_data(1, None)
    assert dfs.is_valid()
    assert dfs.is_valid_against(df)

    sub = SubDataflow2(df, (0, 2))
    dfs = DataflowState(sub)
    dfs.set_data(0, None)
    dfs.set_data(1, None)
    dfs.set_data(4, None)
    dfs.set_data(5, None)
    assert dfs.is_valid()
    assert not dfs.is_valid_against(df)

    sub = SubDataflow2(df, (0, 1, 2, 4))
    dfs = DataflowState(sub)
    dfs.set_data(0, None)
    dfs.set_data(1, None)
    dfs.set_data(2, None)
    dfs.set_data(7, None)
    dfs.set_data(5, None)
    assert dfs.is_valid()
    assert dfs.is_valid_against(df)


def test_dataflow_state_items():
    df = get_dataflow()
    dfs = DataflowState(df)

    assert len(tuple(dfs.items())) == 0

    for i, pid in enumerate([1, 2, 5, 7]):
        dfs.set_data(pid, i)

    assert len(tuple(dfs.items())) == 4

    dfs.set_data(0, 'a')
    assert len(tuple(dfs.items())) == 5

    d = dict((pid, i) for i, pid in enumerate([1, 2, 5, 7]))
    d[0] = 'a'
    assert dict(dfs.items()) == d


def test_dataflow_state_set_data():
    df = get_dataflow()
    dfs = DataflowState(df)

    # allowed to set data on param in ports
    dfs.set_data(0, None)
    assert dfs.has_changed(0)

    # not allowed to set data on non param in ports
    for pid in (3, 6):
        assert_raises(KeyError, lambda: dfs.set_data(pid, None))

    # allowed to set data in out ports
    for pid in (2, 5, 7):
        dfs.set_data(pid, None)
        assert dfs.has_changed(pid)


def test_dataflow_state_get_data():
    df = get_dataflow()
    dfs = DataflowState(df)

    for pid in df.ports():
        assert_raises(KeyError, lambda: dfs.get_data(pid))

    for i, pid in enumerate([1, 2, 5, 7]):
        dfs.set_data(pid, i)

    assert_raises(KeyError, lambda: dfs.get_data(0))

    dfs.set_data(0, 'a')
    assert dfs.get_data(0) == 'a'

    for i, pid in enumerate([1, 2, 5, 7]):
        assert dfs.get_data(pid) == i

    assert dfs.get_data(3) == 0
    assert tuple(dfs.get_data(4)) == (1, 3)
    assert dfs.get_data(6) == 2

    n2 = Node()
    df.set_actor(1, n2)

    assert tuple(dfs.get_data(4)) == (1, 3)

    n5 = Node()
    df.set_actor(4, n5)
    assert tuple(dfs.get_data(4)) == (1, 3)

    n2.get_ad_hoc_dict().set_metadata('position', [10, 0])
    n5.get_ad_hoc_dict().set_metadata('position', [0, 0])
    assert tuple(dfs.get_data(4)) == (3, 1)


def test_dataflow_state_changed():
    df = get_dataflow()
    dfs = DataflowState(df)

    dfs.set_data(0, 'a')
    assert dfs.has_changed(0)
    assert_raises(KeyError, lambda: dfs.has_changed(1))
    assert_raises(KeyError, lambda: dfs.set_changed(5, False))
    assert_raises(KeyError, lambda: dfs.set_changed(7, False))

    for pid in (1, 2, 5, 7):
        dfs.set_data(pid, pid)
        assert dfs.has_changed(pid)

    dfs.set_changed(2, False)
    assert not dfs.has_changed(2)
    assert dfs.has_changed(0)


def test_dataflow_state_input_has_changed():
    df = get_dataflow()
    dfs = DataflowState(df)

    # lonely input port
    assert_raises(KeyError, lambda: dfs.input_has_changed(0))

    dfs.set_data(0, 'a')
    assert dfs.input_has_changed(0)
    dfs.set_changed(0, False)
    assert not dfs.input_has_changed(0)

    # output port
    assert_raises(KeyError, lambda: dfs.input_has_changed(1))
    dfs.set_data(1, 'b')
    assert_raises(KeyError, lambda: dfs.input_has_changed(1))
    dfs.set_changed(1, False)
    assert_raises(KeyError, lambda: dfs.input_has_changed(1))

    # input ports
    assert_raises(KeyError, lambda: dfs.input_has_changed(4))

    for pid in (1, 2, 5, 7):
        dfs.set_data(pid, pid)

    dfs.set_changed(2, False)

    assert_raises(KeyError, lambda: dfs.input_has_changed(2))
    assert dfs.input_has_changed(3)
    assert dfs.input_has_changed(4)
    assert dfs.input_has_changed(6)

    dfs.set_changed(1, False)
    assert not dfs.input_has_changed(3)

    dfs.set_changed(7, False)
    assert not dfs.input_has_changed(4)


def test_dataflow_state_start_task():
    df = get_dataflow()
    dfs = DataflowState(df)

    assert dfs.task_start_time(0) is None
    assert dfs.task_end_time(0) is None

    dfs.task_started(0)
    sleep(0.01)
    dfs.task_ended(0)

    dfs.set_task_start_time(1, 1)
    dfs.set_task_end_time(1, 2)

    t0 = dfs.task_start_time(0)
    t1 = dfs.task_end_time(0)
    assert t1 > t0

    assert dfs.task_start_time(1) == 1
    assert dfs.task_end_time(1) == 2

    dfs.reinit()
    for vid in (0, 1, 2, 3, 4):
        assert dfs.task_start_time(vid) is None
        assert dfs.task_end_time(vid) is None


def test_dataflow_state_last_evaluation():
    df = get_dataflow()
    dfs = DataflowState(df)

    assert dfs.last_evaluation(0) is None