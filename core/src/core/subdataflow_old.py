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


class SubDataflow(object):
    """ Represents a part of a dataflow for a partial evaluation
    A SubDataflow is a callable and abstracts a part of a dataflow as a function
    """

    def __init__(self, dataflow, algo, node_id, port_index):
        """ Constructor

        :param dataflow: todo
        :param algo: algorithm for evaluation.
        :param node_id: todo
        :param port_index: output port index in node_id
        """

        self.dataflow = dataflow
        self.algo = algo
        self.node_id = node_id
        self.port_index = port_index

    def __call__(self, *args):
        """ Consider the Subdataflow as a function """

        if (not self.dataflow):
            return args[0]
            # Identity function
            # if(len(args)==1): return args[0]
            # else: return args

        self.algo.eval(self.node_id, list(args), is_subdataflow=True)
        ret = self.dataflow.actor(self.node_id).get_output(self.port_index)
        return ret
