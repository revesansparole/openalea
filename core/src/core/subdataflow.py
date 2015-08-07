# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
"""This module provide an implementation of a subdataflow"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from dataflow import InvalidVertex, InvalidEdge, PortError


class SubDataflow2(object):
    """ Provide a view on a sub part of a dataflow.

    Mainly for evaluation purposes.
    No edition allowed.
    """
    def __init__(self, dataflow, vids=()):
        """ Construct a view on dataflow.

        args:
            - dataflow (DataFlow): the dataflow to mirror
            - root_id (vid) default (): view will incorporate
                       only the nodes whose id in this list.
        """
        self._dataflow = dataflow
        self._vids = set(vids)

    def has_vertex(self, vid):
        return vid in self._vids

    def has_edge(self, eid):
        df = self._dataflow
        vids = self._vids
        return df.source(eid) in vids and df.target(eid) in vids

    def has_port(self, pid):
        return self._dataflow.vertex(pid) in self._vids

    def vertices(self):
        for vid in self._dataflow.vertices():
            if self.has_vertex(vid):
                yield vid

    def edges(self):
        for eid in self._dataflow.edges():
            if self.has_edge(eid):
                yield eid

    def source_port(self, eid):
        if self.has_edge(eid):
            return self._dataflow.source_port(eid)
        else:
            raise InvalidEdge("Edge not in view")

    def target_port(self, eid):
        if self.has_edge(eid):
            return self._dataflow.target_port(eid)
        else:
            raise InvalidEdge("Edge not in view")

    def ports(self, vid=None):
        if vid is not None and not self.has_vertex(vid):
            raise InvalidVertex("vertex not in view")

        for pid in self._dataflow.ports(vid):
            if self.has_port(pid):
                yield pid

    def in_ports(self, vid=None):
        if vid is not None and not self.has_vertex(vid):
            raise InvalidVertex("vertex not in view")

        for pid in self._dataflow.in_ports(vid):
            if self.has_port(pid):
                yield pid

    def out_ports(self, vid=None):
        if vid is not None and not self.has_vertex(vid):
            raise InvalidVertex("vertex not in view")

        for pid in self._dataflow.out_ports(vid):
            if self.has_port(pid):
                yield pid

    def connected_edges(self, pid):
        if not self.has_port(pid):
            raise PortError("port not in view")

        for eid in self._dataflow.connected_edges(pid):
            if self.has_edge(eid):
                yield eid

    def connected_ports(self, pid):
        if not self.has_port(pid):
            raise PortError("port not in view")

        for pid in self._dataflow.connected_ports(pid):
            if self.has_port(pid):
                yield pid

    def nb_connections(self, pid):
        if not self.has_port(pid):
            raise PortError("port not in view")

        return len(tuple(self.connected_edges(pid)))

    def port(self, pid):
        return self._dataflow.port(pid)

    def local_id(self, pid):
        return self._dataflow.local_id(pid)

    def in_port(self, vid, local_id):
        return self._dataflow.in_port(vid, local_id)

    def out_port(self, vid, local_id):
        return self._dataflow.out_port(vid, local_id)

    def actor(self, vid):
        return self._dataflow.actor(vid)