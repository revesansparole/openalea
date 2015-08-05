"""Node tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.node import Node
from openalea.core.node_factory import Factory


class MyNode(Node):
    def __call__(self, inputs):
        return sum(inputs)


def my_func(a, b):
    return a + b


def test_factory():
    """test factory"""
    f1 = Factory(name="MyFactory",
                 nodemodule="test_node_factory",
                 nodeclass="MyNode",
                 )

    n = f1.instantiate()
    print n.get_nb_input()
    assert n.get_nb_input() == 0

    f2 = Factory(name="MyFactory2",
                 nodemodule="test_node_factory",
                 nodeclass="my_func",
                 )

    n = f2.instantiate()
    assert n.get_nb_input() == 2

    f1IO = Factory(name="MyFactory",
                   nodemodule="test_node_factory",
                   nodeclass="MyNode",
                   inputs=(dict(name="x", interface=None),
                           dict(name="y", interface=None),
                           dict(name="z", interface=None)),
                   outputs=(dict(name="a", interface=None),), )

    n = f1IO.instantiate()
    assert n.get_nb_input() == 3

    f2IO = Factory(name="MyFactory2",
                   nodemodule="test_node_factory",
                   nodeclass="my_func",
                   inputs=(dict(name="x", interface=None),
                           dict(name="y", interface=None)),
                   outputs=(dict(name="z", interface=None),), )

    n = f2IO.instantiate()
    assert n.get_nb_input() == 2


def test_factory_name():
    """ test the factory python name """

    names = ['aaaa',
             '234AB3',
             'azert er',
             'AZ_12',
             '::qsd,;']

    for n in names:
        f = Factory(name=n)
        python_name = f.get_python_name()
        exec ("%s = 0" % python_name)
