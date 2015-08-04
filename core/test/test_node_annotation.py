"""Annotation tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.node_annotation import Annotation


def test_annotation():
    a = Annotation()

    assert a.internal_data.get('text') is None
