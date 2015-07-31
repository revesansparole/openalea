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


from provenance_exec import ProvenanceExec


class EvaluationEnvironment(object):
    """ Environment for evaluation algorithms
    """
    def __init__(self):
        """ Constructor """
        self._exec_id = 0
        self._record_prov = False
        self._prov = None

    def current_execution(self):
        """ Return id of current execution.
        """
        return self._exec_id

    def new_execution(self):
        """ Change execution id to a new unused id.
        """
        self._exec_id += 1

    def record_provenance(self):
        """ Return wether or not execution provenance
        should be recorded during this execution.
        """
        return self._record_prov

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
        self._record_prov = True
