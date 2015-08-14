# -*- python -*-
#
#       OpenAlea.SoftBus: OpenAlea Software Bus
#
#       Copyright 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
"""Test evaluation algorithm"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import assert_raises

from openalea.core.node_control_flow import ControlFlowNode


def test_control_flow_simple():
    n = ControlFlowNode()
    a = n()
    assert a is None
    assert_raises(NotImplementedError, lambda: n.perform_evaluation(None, None, None, None))
