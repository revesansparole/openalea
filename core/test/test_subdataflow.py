"""Dataflow Tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises

from openalea.core.actor import IActor
from openalea.core.dataflow import (DataFlow,
                                    InvalidEdge,
                                    InvalidVertex,
                                    PortError)
from openalea.core.subdataflow import SubDataflow2, get_upstream_subdataflow


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
    df.add_vertex(0)
    df.add_out_port(0, "out", 0)
    df.add_vertex(1)
    df.add_out_port(1, "out", 1)

    df.add_vertex(2)
    df.add_in_port(2, "in1", 2)
    df.add_in_port(2, "in2", 3)
    df.add_out_port(2, "res", 4)

    df.add_vertex(3)
    df.add_in_port(3, "in", 5)

    df.add_vertex(4)
    df.add_out_port(4, "out", 6)

    df.connect(0, 2, 0)
    df.connect(1, 3, 1)
    df.connect(4, 5, 2)
    df.connect(6, 3, 3)

    return df


def test_subdataflow_init():
    df = DataFlow()
    sub = SubDataflow2(df)

    assert len(tuple(sub.vertices())) == 0


def test_subdataflow_vertices():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert set(sub.vertices()) == {0, 2}


def test_subdataflow_edges():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert set(sub.edges()) == {0}


def test_subdataflow_in_edges():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert set(sub.in_edges(2)) == {0}


def test_subdataflow_out_edges():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert set(sub.out_edges(0)) == {0}


def test_subdataflow_in_neighbors():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert set(sub.in_neighbors(2)) == {0}


def test_subdataflow_port():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert sub.source_port(0) == df.source_port(0)
    assert_raises(InvalidEdge, lambda: sub.source_port(1))
    assert_raises(InvalidEdge, lambda: sub.source_port(2))

    assert sub.target_port(0) == df.target_port(0)
    assert_raises(InvalidEdge, lambda: sub.target_port(1))
    assert_raises(InvalidEdge, lambda: sub.target_port(2))


def test_subdataflow_ports():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert set(sub.ports()) == {0, 2, 3, 4}
    assert set(sub.ports(0)) == {0}
    assert_raises(InvalidVertex, lambda: sub.ports(1).next())
    assert set(sub.ports(2)) == {2, 3, 4}
    assert_raises(InvalidVertex, lambda: sub.ports(3).next())


def test_subdataflow_in_ports():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert set(sub.in_ports()) == {2, 3}
    assert len(set(sub.in_ports(0))) == 0
    assert_raises(InvalidVertex, lambda: sub.in_ports(1).next())
    assert set(sub.in_ports(2)) == {2, 3}
    assert_raises(InvalidVertex, lambda: sub.in_ports(3).next())


def test_subdataflow_out_ports():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert set(sub.out_ports()) == {0, 4}
    assert set(sub.out_ports(0)) == {0}
    assert_raises(InvalidVertex, lambda: sub.out_ports(1).next())
    assert set(sub.out_ports(2)) == {4}
    assert_raises(InvalidVertex, lambda: sub.out_ports(3).next())


def test_subdataflow_connected_edges():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert set(sub.connected_edges(0)) == {0}
    assert set(sub.connected_edges(2)) == {0}
    assert len(set(sub.connected_edges(3))) == 0
    assert len(set(sub.connected_edges(4))) == 0
    assert_raises(PortError, lambda: sub.connected_edges(1).next())
    assert_raises(PortError, lambda: sub.connected_edges(5).next())


def test_subdataflow_connected_ports():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))

    assert set(sub.connected_ports(0)) == {2}
    assert set(sub.connected_ports(2)) == {0}
    assert len(set(sub.connected_ports(3))) == 0
    assert len(set(sub.connected_ports(4))) == 0
    assert_raises(PortError, lambda: sub.connected_ports(1).next())
    assert_raises(PortError, lambda: sub.connected_ports(5).next())


def test_subdataflow_nb_connections():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert sub.nb_connections(0) == 1
    assert sub.nb_connections(2) == 1
    assert sub.nb_connections(3) == 0
    assert sub.nb_connections(4) == 0
    for pid in (1, 5):
        assert_raises(PortError, lambda: sub.nb_connections(pid))


def test_subdataflow_mirror_functions():
    df = get_df()

    sub = SubDataflow2(df, (0, 2))
    assert sub.is_in_port(2)
    assert sub.is_out_port(0)
    assert sub.vertex(0) == 0
    assert sub.port(0) == df.port(0)
    assert sub.local_id(0) == df.local_id(0)
    assert sub.in_port(2, "in1") == df.in_port(2, "in1")
    assert sub.out_port(0, "out") == df.out_port(0, "out")
    assert sub.actor(0) == df.actor(0)
    assert 0 in sub


def test_subdataflow_get_upstream_subdataflow():
    df = get_df()
    assert_raises(PortError, lambda: get_upstream_subdataflow(df, 0))

    sub = get_upstream_subdataflow(df, 2)
    assert set(sub.vertices()) == {0}

    sub = get_upstream_subdataflow(df, 3)
    assert set(sub.vertices()) == {1, 4}

    sub = get_upstream_subdataflow(df, 5)
    assert set(sub.vertices()) == {0, 1, 2, 4}
