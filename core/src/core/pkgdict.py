# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
""" Special Dict with case insensitive key and protected fields.
"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


def lower(name):
    """ Change name to lower case.
    """
    try:
        return name.lower()
    except AttributeError:
        return name


def is_protected(name):
    """ Return true if name is protected.
    """
    try:
        return name.startswith('#')
    except AttributeError:
        return False


def protect(name):
    """ Return corresponding protected name for item.
    """
    return "#" + name


class PackageDict(dict):
    """ Dictionnary with case insensitive key.

    This object is able to handle protected entry beginning with an '#'
    """

    def __init__(self, *args):
        dict.__init__(self, *args)

    def __getitem__(self, key):
        key = lower(key)

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            # Try to return protected entry
            return dict.__getitem__(self, protect(key))

    def __setitem__(self, key, item):
        if not isinstance(key, str):
            raise KeyError("only str keys")

        return dict.__setitem__(self, lower(key), item)

    def __contains__(self, key):
        return self.has_key(key)

    def has_key(self, key):
        """ Test whether the given key exists in the dict
        either as key or as protected(key).

        args:
            - key(str)
        """
        key = lower(key)
        if dict.has_key(self, key):
            return True
        else:
            try:
                return dict.has_key(self, protect(key))
            except TypeError:
                return False

    def __delitem__(self, key):
        """ Attempt to remove an item from the dict.
        """
        return dict.__delitem__(self, lower(key))

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return dict.get(self, protect(key), default)

    def public_values(self):
        """ Iterate through all values corresponding
        to non protected keys.
        """
        for k, v in self.items():
            if not is_protected(k):
                yield v

    def nb_public_values(self):
        """ Return the number of unprotected items.
        """
        return len(tuple(self.public_values()))
