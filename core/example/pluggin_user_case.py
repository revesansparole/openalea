""" This file define a simple use case for the plugin manager
from a user point of view.
"""

from openalea.core.service.plugin import plugin, plugins

for pl in plugins(group='openalea.core'):
    print pl


pl = plugin("openalea.core.plugin.builtin:PythonModel", group='openalea.core')
# TODO: pb, need the group attribute even with a unique id

PythonModel = pl.implementation

m = PythonModel()
