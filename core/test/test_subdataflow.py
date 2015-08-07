"""Dataflow Tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises

from openalea.core.actor import IActor
from openalea.core.dataflow import (DataFlow,
                                    InvalidEdge,
                                    InvalidVertex,
                                    PortError)
from openalea.core.subdataflow import SubDataflow2

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


def get_df():
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
    eid3 = df.connect(pid33, pid41)

    pids = (pid11, pid21, pid31, pid32, pid33, pid41)
    eids = (eid1, eid2, eid3)
    vids = (vid1, vid2, vid3, vid4)
    return df, pids, eids, vids


def test_subdataflow_init():
    df = DataFlow()
    sub = SubDataflow2(df)

    assert len(tuple(sub.vertices())) == 0


def test_subdataflow_vertices():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))
    assert set(sub.vertices()) == {vid1, vid3}


def test_subdataflow_edges():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))
    assert set(sub.edges()) == {eid1}


def test_subdataflow_out_edges():
    assert False


def test_subdataflow_in_neighbors():
    assert False


def test_subdataflow_port():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert sub.source_port(eid1) == df.source_port(eid1)
    assert_raises(InvalidEdge, lambda: sub.source_port(eid2))
    assert_raises(InvalidEdge, lambda: sub.source_port(eid3))

    assert sub.target_port(eid1) == df.target_port(eid1)
    assert_raises(InvalidEdge, lambda: sub.target_port(eid2))
    assert_raises(InvalidEdge, lambda: sub.target_port(eid3))


def test_subdataflow_ports():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert set(sub.ports()) == {pid11, pid31, pid32, pid33}
    assert set(sub.ports(vid1)) == {pid11}
    assert_raises(InvalidVertex, lambda: sub.ports(vid2).next())
    assert set(sub.ports(vid3)) == {pid31, pid32, pid33}
    assert_raises(InvalidVertex, lambda: sub.ports(vid4).next())


def test_subdataflow_in_ports():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert set(sub.in_ports()) == {pid31, pid32}
    assert len(set(sub.in_ports(vid1))) == 0
    assert_raises(InvalidVertex, lambda: sub.in_ports(vid2).next())
    assert set(sub.in_ports(vid3)) == {pid31, pid32}
    assert_raises(InvalidVertex, lambda: sub.in_ports(vid4).next())


def test_subdataflow_out_ports():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert set(sub.out_ports()) == {pid11, pid33}
    assert set(sub.out_ports(vid1)) == {pid11}
    assert_raises(InvalidVertex, lambda: sub.out_ports(vid2).next())
    assert set(sub.out_ports(vid3)) == {pid33}
    assert_raises(InvalidVertex, lambda: sub.out_ports(vid4).next())


def test_subdataflow_connected_edges():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert set(sub.connected_edges(pid11)) == {eid1}
    assert set(sub.connected_edges(pid31)) == {eid1}
    assert len(set(sub.connected_edges(pid32))) == 0
    assert len(set(sub.connected_edges(pid33))) == 0
    assert_raises(PortError, lambda: sub.connected_edges(pid21).next())
    assert_raises(PortError, lambda: sub.connected_edges(pid41).next())


def test_subdataflow_connected_ports():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))

    assert set(sub.connected_ports(pid11)) == {pid31}
    assert set(sub.connected_ports(pid31)) == {pid11}
    assert len(set(sub.connected_ports(pid32))) == 0
    assert len(set(sub.connected_ports(pid33))) == 0
    assert_raises(PortError, lambda: sub.connected_ports(pid21).next())
    assert_raises(PortError, lambda: sub.connected_ports(pid41).next())


def test_subdataflow_nb_connections():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))
    assert sub.nb_connections(pid11) == 1
    assert sub.nb_connections(pid31) == 1
    assert sub.nb_connections(pid32) == 0
    assert sub.nb_connections(pid33) == 0
    for pid in (pid21, pid41):
        assert_raises(PortError, lambda: sub.nb_connections(pid))


def test_subdataflow_mirror_functions():
    df, pids, eids, vids = get_df()
    pid11, pid21, pid31, pid32, pid33, pid41 = pids
    eid1, eid2, eid3 = eids
    vid1, vid2, vid3, vid4 = vids

    sub = SubDataflow2(df, (vid1, vid3))
    assert sub.is_in_port(pid31)
    assert sub.is_out_port(pid11)
    assert sub.vertex(pid11) == vid1
    assert sub.port(pid11) == df.port(pid11)
    assert sub.local_id(pid11) == df.local_id(pid11)
    assert sub.in_port(vid3, "in1") == df.in_port(vid3, "in1")
    assert sub.out_port(vid1, "out") == df.out_port(vid1, "out")
    assert sub.actor(vid1) == df.actor(vid1)
