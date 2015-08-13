# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
""" This module provide data structure to store global parameters
for a dataflow evaluation.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from graph.id_generator import IdGenerator
from provenance_exec import ProvenanceExec


class EvaluationEnvironment(object):
    """ Environment for evaluation algorithms
    """
    def __init__(self, exec_id=None):
        """ Constructor

        args:
            - exec_id (eid) default None:
                        current id to set for this environment
                        if None, a new one will be created
        """
        self._id_gen = IdGenerator()

        self._exec_id = self._id_gen.get_id(exec_id)
        self._prov = None

    def clear(self):
        """ Clear environment
        """
        self._id_gen = IdGenerator()
        self._exec_id = self._id_gen.get_id()
        if self.record_provenance():
            self._prov.clear()

    def current_execution(self):
        """ Return id of current execution.
        """
        return self._exec_id

    def set_current_execution(self, exec_id):  # TODO: test and handling exceptions
        # TODO: not safe with id_gen
        """ TEST
        """
        self._exec_id = exec_id

    def new_execution(self, exec_id=None):
        """ Change execution id to a new unused id.

        arg:
            - exec_id (eid): id of parent execution
        """
        self._exec_id = self._id_gen.get_id()

        if self.record_provenance():
            self._prov.new_execution(exec_id, self._exec_id)

    def record_provenance(self):
        """ Return whether or not execution provenance
        should be recorded during this execution.
        """
        return self._prov is not None

    def provenance(self):
        """ Return provenance object to use.
        """
        return self._prov

    def set_provenance(self, dataflow):
        """ Set the environment to record provenance.

        args:
            - dataflow (DataFlow): dataflow to observe
        """
        self._prov = ProvenanceExec(dataflow)

        g = self._prov.execution_graph()
        g.add_vertex(self._exec_id)
