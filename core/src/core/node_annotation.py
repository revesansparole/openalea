# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
"""Node and NodeFactory classes.

A Node is generalized functor which is embeded in a dataflow.
A Factory build Node from its description. Factories instantiate
Nodes on demand for the dataflow.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from openalea.core.node import AbstractNode


class Annotation(AbstractNode):
    def __init__(self):
        AbstractNode.__init__(self)

    def to_script (self):
        """Script translation of this node.
        """
        return ""


def initialise_standard_metadata():
    """Declares the standard keys used by the Node structures. Called at the end of this file"""
    # we declare what are the node model ad hoc data we require:
    Annotation.extend_ad_hoc_slots("text", str, "", "txt")
#    Annotation.extend_ad_hoc_slots("htmlText", str, None)
    Annotation.extend_ad_hoc_slots("textColor", list, None)
    Annotation.extend_ad_hoc_slots("rectP2", tuple, (-1, -1))
    Annotation.extend_ad_hoc_slots("color", list, None)
    Annotation.extend_ad_hoc_slots("visualStyle", int, None)


initialise_standard_metadata()
