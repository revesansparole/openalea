# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#                       Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
""" Definition of Port objects for Nodes
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from weakref import ref

from openalea.core.interface import TypeNameInterfaceMap
from openalea.core.metadatadict import HasAdHoc
from openalea.core.observer import Observed


class AbstractPort(dict, Observed, HasAdHoc):
    """ Container of properties associated to a port
    """

    def __init__(self, vertex):
        dict.__init__(self)
        HasAdHoc.__init__(self)
        Observed.__init__(self)

        self.vertex = ref(vertex)  # TODO: GRUUIK
        self.__id = None

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def copy_to(self, other):
        other.get_ad_hoc_dict().update(self.get_ad_hoc_dict())
        self.transfer_listeners(other)

    def get_id(self):
        return self.__id

    def set_id(self, pid):
        self.__id = pid

    def get_desc(self):
        """ Get default description.
        """
        return self.get("desc", None)

    def get_default(self):
        """ Get default value associated to this port.
        """
        return self.get("value", None)

    def get_interface(self):
        """ Get the interface.
        """
        interf = self.get("interface", None)
        if isinstance(interf, str):
            return TypeNameInterfaceMap()[interf]
        else:
            return interf

    def get_tip(self, current_value=None):
        """ Get the tool tip associated to this port.
        """
        name = self['name']
        interface = self.get('interface', None)
        desc = self.get('desc', '')
        value = self.get('value', None)
        iname = 'Any'
        if interface is not None:
            try:
                iname = interface.__name__
            except AttributeError:
                try:
                    iname = interface.__class__.__name__
                except AttributeError:
                    iname = str(interface)

        # A way to avoid displaying too long strings.
        comment = str(value)
        if len(comment) > 100:
            comment = comment[:100] + ' ...'

        if current_value is None:
            return '%s(%s): %s [default=%s] ' % (name, iname, desc, comment)
        else:
            return '%s(%s): %s' % (name, iname, str(current_value))


class InputPort(AbstractPort):
    """ Specification of a Port for inputs.
    """
    def __init__(self, node):
        AbstractPort.__init__(self, node)

    def get_label(self):
        """ Get default label.
        """
        return self.get("label", self["name"])

    def is_hidden(self):
        """ True if the port should not be displayed.
        """
        return self.get("hide", False)


class OutputPort(AbstractPort):
    """ Specification of a Port for inputs.
    """
    def __init__(self, node):
        AbstractPort.__init__(self, node)

def initialise_standard_metadata():
    """Declares the standard keys used by the Node structures. Called at the end of this file"""
    # we declare what are the node model ad hoc data we require:
    AbstractPort.extend_ad_hoc_slots("hide" , bool, False)
    AbstractPort.extend_ad_hoc_slots("connectorPosition", list, [0, 0])


initialise_standard_metadata()
