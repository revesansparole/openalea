"""Dataflow Tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises

from openalea.core.actor import IActor
from openalea.core.dataflow import (DataFlow,
                                    PortError,
                                    InvalidActor,
                                    InvalidVertex)


class DummyActor(IActor):
    def set_id(self, vid):
        """ GRUUIKK needed for dataflow ?????
        """
        print vid

    def input_descriptions(self):
        for i in range(4):
            yield "in%d" % i, None

    def output_descriptions(self):
        for i in range(3):
            yield "out%d" % i, None


def test_dataflow_init():
    df = DataFlow()

    assert df.nb_vertices() == 0
    assert df.nb_edges() == 0


def test_dataflow_source_port():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()
    eid = df.add_edge((vid1, vid2))

    assert_raises(PortError, lambda: df.source_port(eid))

    pid1 = df.add_out_port(vid1, "out")
    pid2 = df.add_in_port(vid2, "in")
    eid = df.connect(pid1, pid2)

    assert df.source_port(eid) == pid1


def test_dataflow_target_port():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()
    eid = df.add_edge((vid1, vid2))

    assert_raises(PortError, lambda: df.target_port(eid))

    pid1 = df.add_out_port(vid1, "out")
    pid2 = df.add_in_port(vid2, "in")
    eid = df.connect(pid1, pid2)

    assert df.target_port(eid) == pid2


def test_dataflow_ports():
    df = DataFlow()

    assert_raises(InvalidVertex, lambda: df.ports(0).next())

    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    assert len(tuple(df.ports(vid1))) == 0
    assert len(tuple(df.ports())) == 0

    ipid1 = df.add_in_port(vid1, "in")
    opids = [df.add_out_port(vid1, "out%d" % i) for i in range(5)]
    ipid2 = df.add_in_port(vid2, "in")
    opid = df.add_out_port(vid2, "out")

    assert sorted(df.ports(vid1)) == sorted([ipid1] + opids)
    assert sorted(df.ports()) == sorted([ipid1] + opids + [ipid2, opid])


def test_dataflow_in_ports():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    assert len(tuple(df.in_ports(vid1))) == 0
    assert len(tuple(df.in_ports())) == 0

    pids = [df.add_in_port(vid1, "in%d" % i) for i in range(5)]
    df.add_out_port(vid1, "out")
    pid = df.add_in_port(vid2, "in")
    df.add_out_port(vid2, "out")

    assert sorted(df.in_ports(vid1)) == sorted(pids)
    assert sorted(df.in_ports()) == sorted(pids + [pid])


def test_dataflow_out_ports():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    assert len(tuple(df.out_ports(vid1))) == 0
    assert len(tuple(df.out_ports())) == 0

    df.add_in_port(vid1, "in")
    pids = [df.add_out_port(vid1, "out%d" % i) for i in range(5)]
    df.add_in_port(vid2, "in")
    pid = df.add_out_port(vid2, "out")

    assert sorted(df.out_ports(vid1)) == sorted(pids)
    assert sorted(df.out_ports()) == sorted(pids + [pid])


def test_dataflow_is_in_port():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.is_in_port(0))

    pid = df.add_in_port(vid, "in")
    assert_raises(PortError, lambda: df.is_in_port(pid + 1))
    assert df.is_in_port(pid)


def test_dataflow_is_out_port():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.is_out_port(0))

    pid = df.add_out_port(vid, "in")
    assert_raises(PortError, lambda: df.is_out_port(pid + 1))
    assert df.is_out_port(pid)


def test_dataflow_vertex():
    df = DataFlow()

    assert_raises(PortError, lambda: df.vertex(0))

    vid = df.add_vertex()
    pid1 = df.add_in_port(vid, 0)
    pid2 = df.add_out_port(vid, 0)
    assert df.vertex(pid1) == vid
    assert df.vertex(pid2) == vid


def test_dataflow_connected_edges():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()
    vid3 = df.add_vertex()

    assert_raises(PortError, lambda: df.connected_edges(0).next())

    pid1 = df.add_in_port(vid1, 0)
    pid2 = df.add_in_port(vid1, 1)
    pid3 = df.add_out_port(vid2, 0)
    pid4 = df.add_out_port(vid3, 0)

    for pid in (pid1, pid2, pid3, pid4):
        assert len(tuple(df.connected_edges(pid))) == 0

    eid1 = df.connect(pid3, pid1)
    assert tuple(df.connected_edges(pid3)) == (eid1,)
    assert tuple(df.connected_edges(pid1)) == (eid1,)

    eid2 = df.connect(pid4, pid1)
    assert tuple(df.connected_edges(pid3)) == (eid1,)
    assert tuple(df.connected_edges(pid4)) == (eid2,)
    assert sorted(df.connected_edges(pid1)) == sorted((eid1, eid2))

    eid3 = df.connect(pid4, pid2)
    assert tuple(df.connected_edges(pid3)) == (eid1,)
    assert sorted(df.connected_edges(pid4)) == sorted((eid2, eid3))
    assert sorted(df.connected_edges(pid1)) == sorted((eid1, eid2))
    assert tuple(df.connected_edges(pid2)) == (eid3,)


def test_dataflow_connected_ports():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()
    vid3 = df.add_vertex()

    assert_raises(PortError, lambda: df.connected_ports(0).next())

    pid1 = df.add_in_port(vid1, 0)
    pid2 = df.add_in_port(vid1, 1)
    pid3 = df.add_out_port(vid2, 0)
    pid4 = df.add_out_port(vid3, 0)

    for pid in (pid1, pid2, pid3, pid4):
        assert len(tuple(df.connected_ports(pid))) == 0

    df.connect(pid3, pid1)
    assert tuple(df.connected_ports(pid3)) == (pid1,)
    assert tuple(df.connected_ports(pid1)) == (pid3,)

    df.connect(pid4, pid1)
    assert tuple(df.connected_ports(pid3)) == (pid1,)
    assert tuple(df.connected_ports(pid4)) == (pid1,)
    assert sorted(df.connected_ports(pid1)) == sorted((pid3, pid4))

    df.connect(pid4, pid2)
    assert tuple(df.connected_ports(pid3)) == (pid1,)
    assert sorted(df.connected_ports(pid4)) == sorted((pid1, pid2))
    assert sorted(df.connected_ports(pid1)) == sorted((pid3, pid4))
    assert tuple(df.connected_ports(pid2)) == (pid4,)


def dataflow_nb_connections():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()
    vid3 = df.add_vertex()

    assert_raises(PortError, lambda: df.nb_connections(0).next())

    pid1 = df.add_in_port(vid1, 0)
    pid2 = df.add_in_port(vid1, 1)
    pid3 = df.add_out_port(vid2, 0)
    pid4 = df.add_out_port(vid3, 0)

    for pid in (pid1, pid2, pid3, pid4):
        assert len(tuple(df.nb_connections(pid))) == 0

    df.connect(pid3, pid1)
    assert df.nb_connections(pid3) == 1
    assert df.nb_connections(pid1) == 1

    df.connect(pid4, pid1)
    assert df.nb_connections(pid3) == 1
    assert df.nb_connections(pid4) == 1
    assert df.nb_connections(pid1) == 2

    df.connect(pid4, pid2)
    assert df.nb_connections(pid3) == 1
    assert df.nb_connections(pid4) == 2
    assert df.nb_connections(pid1) == 2
    assert df.nb_connections(pid2) == 1


def test_dataflow_port():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.port(0))

    pid1 = df.add_in_port(vid, 0)
    assert df.port(pid1).vid == vid
    pid2 = df.add_out_port(vid, 0)
    assert df.port(pid2).vid == vid


def test_dataflow_local_id():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.local_id(0))

    for lpid in (0, 1, "a", None):
        pid = df.add_in_port(vid, lpid)
        assert df.local_id(pid) == lpid
        pid = df.add_out_port(vid, lpid)
        assert df.local_id(pid) == lpid


def test_dataflow_in_port():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.in_port(0, None))

    pids = [df.add_in_port(vid, lpid) for lpid in (0, 1, "a", None)]
    assert_raises(PortError, lambda: df.in_port(vid, "toto"))

    for i, lpid in enumerate([0, 1, "a", None]):
        assert df.in_port(vid, lpid) == pids[i]


def test_dataflow_out_port():
    df = DataFlow()
    vid = df.add_vertex()

    assert_raises(PortError, lambda: df.out_port(0, None))

    pids = [df.add_out_port(vid, lpid) for lpid in (0, 1, "a", None)]
    assert_raises(PortError, lambda: df.out_port(vid, "toto"))

    for i, lpid in enumerate([0, 1, "a", None]):
        assert df.out_port(vid, lpid) == pids[i]


def test_dataflow_actor():
    df = DataFlow()

    assert_raises(InvalidVertex, lambda: df.actor(0))

    vid = df.add_vertex()
    assert df.actor(vid) is None

    actor = DummyActor()
    assert_raises(PortError, lambda: df.set_actor(vid, actor))

    for key, interface in actor.input_descriptions():
        df.add_in_port(vid, key)

    for key, interface in actor.output_descriptions():
        df.add_out_port(vid, key)

    df.set_actor(vid, actor)
    assert df.actor(vid) == actor


def test_dataflow_set_actor():
    df = DataFlow()
    actor = DummyActor()

    assert_raises(InvalidVertex, lambda: df.set_actor(0, actor))

    vid = df.add_vertex()
    df.set_actor(vid, None)
    assert df.actor(vid) is None
    assert_raises(PortError, lambda: df.set_actor(vid, actor))

    for key, interface in actor.input_descriptions():
        df.add_in_port(vid, key)

    for key, interface in actor.output_descriptions():
        df.add_out_port(vid, key)

    df.set_actor(vid, actor)
    assert df.actor(vid) == actor

    df.set_actor(vid, None)
    assert df.actor(vid) is None


def test_dataflow_add_actor():
    df = DataFlow()
    vid1 = df.add_vertex()
    actor = DummyActor()

    assert_raises(InvalidActor, lambda: df.add_actor(None))
    assert_raises(IndexError, lambda: df.add_actor(actor, vid1))

    for key, interface in actor.input_descriptions():
        df.add_in_port(vid1, key)

    for key, interface in actor.output_descriptions():
        df.add_out_port(vid1, key)

    df.set_actor(vid1, actor)
    assert_raises(IndexError, lambda: df.add_actor(actor, vid1))

    vid2 = df.add_actor(actor)
    assert df.actor(vid2) == actor
    nb = len(tuple(df.in_ports(vid2)))
    assert len(tuple(actor.input_descriptions())) == nb
    nb = len(tuple(df.out_ports(vid2)))
    assert len(tuple(actor.output_descriptions())) == nb


def test_dataflow_add_in_port():
    df = DataFlow()

    assert_raises(InvalidVertex, lambda: df.add_in_port(0, "toto"))

    vid = df.add_vertex()
    pid = df.add_in_port(vid, "port")

    assert_raises(IndexError, lambda: df.add_in_port(vid, "toto", pid))
    assert_raises(PortError, lambda: df.add_in_port(vid, "port"))

    assert tuple(df.in_ports(vid)) == (pid,)
    assert df.local_id(pid) == "port"
    assert df.in_port(vid, "port") == pid


def test_dataflow_add_out_port():
    df = DataFlow()

    assert_raises(InvalidVertex, lambda: df.add_out_port(0, "toto"))

    vid = df.add_vertex()
    pid = df.add_out_port(vid, "port")

    assert_raises(IndexError, lambda: df.add_out_port(vid, "toto", pid))
    assert_raises(PortError, lambda: df.add_out_port(vid, "port"))

    assert tuple(df.out_ports(vid)) == (pid,)
    assert df.local_id(pid) == "port"
    assert df.out_port(vid, "port") == pid


def test_dataflow_remove_port():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    pid1 = df.add_in_port(vid1, "in")
    pid2 = df.add_out_port(vid2, "out")

    df.connect(pid2, pid1)

    assert_raises(PortError, lambda: df.remove_port(pid1 + pid2 + 1))

    df.remove_port(pid1)
    assert len(tuple(df.ports(vid1))) == 0
    assert tuple(df.ports(vid2)) == (pid2,)
    assert df.nb_connections(pid2) == 0


def test_dataflow_connect():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    assert_raises(PortError, lambda: df.connect(0, 1))
    pid1 = df.add_in_port(vid1, "in")
    assert_raises(PortError, lambda: df.connect(pid1 + 1, pid1))
    pid2 = df.add_out_port(vid2, "out")
    assert_raises(PortError, lambda: df.connect(pid2, pid1 + pid2 + 1))
    assert_raises(PortError, lambda: df.connect(pid1, pid2))

    eid = df.connect(pid2, pid1)
    assert df.source_port(eid) == pid2
    assert df.target_port(eid) == pid1
    assert tuple(df.connected_edges(pid1)) == (eid,)
    assert tuple(df.connected_edges(pid2)) == (eid,)
    assert pid1 in df.connected_ports(pid2)
    assert pid2 in df.connected_ports(pid1)

    assert_raises(IndexError, lambda: df.connect(pid2, pid1, eid))


def test_dataflow_add_vertex():
    df = DataFlow()

    vid = df.add_vertex()
    assert df.nb_vertices() == 1
    assert_raises(IndexError, lambda: df.add_vertex(vid))

    assert len(tuple(df.ports(vid))) == 0
    assert df.actor(vid) is None


def test_dataflow_remove_vertex():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    pid1 = df.add_in_port(vid1, "in")
    pid2 = df.add_out_port(vid2, "out")

    df.connect(pid2, pid1)

    assert_raises(InvalidVertex, lambda: df.remove_vertex(vid1 + vid2 + 1))

    df.remove_vertex(vid1)
    assert tuple(df.ports()) == (pid2,)
    assert_raises(InvalidVertex, lambda: df.ports(vid1).next())
    assert tuple(df.ports(vid2)) == (pid2,)
    assert df.nb_connections(pid2) == 0
    assert df.nb_neighbors(vid2) == 0


def test_dataflow_clear():
    df = DataFlow()
    vid1 = df.add_vertex()
    vid2 = df.add_vertex()

    pid1 = df.add_in_port(vid1, "in")
    pid2 = df.add_out_port(vid2, "out")

    df.connect(pid2, pid1)

    df.clear()

    assert df.nb_vertices() == 0
    assert df.nb_edges() == 0
    assert len(tuple(df.ports())) == 0


def test_dataflow_big():
    df = DataFlow()
    vid1 = df.add_vertex()
    pid11 = df.add_out_port(vid1, "out")
    vid2 = df.add_vertex()
    pid21 = df.add_out_port(vid2, "out")

    vid3 = df.add_vertex()
    pid31 = df.add_in_port(vid3, "in1")
    pid32 = df.add_in_port(vid3, "in2")
    pid33 = df.add_out_port(vid3, "res")

    vid4 = df.add_vertex()
    pid41 = df.add_in_port(vid4, "in")

    eid1 = df.connect(pid11, pid31)
    eid2 = df.connect(pid21, pid32)
    df.connect(pid33, pid41)

    assert df.source_port(eid1) == pid11
    assert df.target_port(eid2) == pid32
    assert set(df.out_ports(vid1)) == {pid11}
    assert set(df.in_ports(vid3)) == {pid31, pid32}
    assert set(df.ports(vid3)) == {pid31, pid32, pid33}
    assert df.is_in_port(pid31)
    assert df.is_out_port(pid11)
    assert df.vertex(pid11) == vid1
    assert set(df.connected_ports(pid11)) == {pid31}
    assert set(df.connected_edges(pid21)) == {eid2}
    assert df.out_port(vid1, "out") == pid11
    assert df.in_port(vid3, "in1") == pid31

    test = False
    try:
        df.connect(pid11, pid33)
    except PortError:
        test = True
    assert test

    df.remove_port(pid33)
    assert set(df.connected_ports(pid41)) == set()
    assert set(df.out_edges(vid3)) == set()
    test = False
    try:
        df.port(pid33)
    except PortError:
        test = True
    assert test
