"""Node tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from openalea.core.node import Node, FuncNode


def test_funcnode():
    """ Test Node creation"""
    inputs = (dict(name='x', interface=None, value=None),)
    outputs = (dict(name='y', interface=None),)

    def func(*input_values):
        return input_values,

    n = FuncNode(inputs, outputs, func)

    n.add_input(name='a', inteface=None, value=0)
    assert n.get_nb_input() == 2
    assert n.get_nb_output() == 1

    # Test IO and acess by key or index
    n.set_input(0, 1)
    n.eval()
    print n.get_output('y')
    assert n.get_output('y') == (1, 0)

    n.set_input('a', 'BB')
    n.eval()
    assert n.get_output(0) == (1, 'BB')


class MyNode(Node):
    def __call__(self, inputs):
        return sum(inputs)


def test_node():
    """ Test Node creation"""
    inputs = (dict(name='x', interface=None, value=None),)
    outputs = (dict(name='y', interface=None),)

    n = Node(inputs, outputs)

    try:
        n()
        assert False
    except NotImplementedError:
        assert True

    n = MyNode(inputs, outputs)

    assert n.get_nb_input() == 1
    assert n.get_nb_output() == 1

    # Test IO and acess by key or index
    n.set_input(0, 1)
    n.eval()
    assert n.get_output('y') == 1


def test_node_output():
    # Test Node creation
    inputs = (dict(name='x', interface=None, value=None),)
    outputs = (dict(name='y', interface=None),)

    def func1(*args):
        return 1

    def func2(*args):
        return [1, 2]

    n1 = FuncNode(inputs, outputs, func1)
    n2 = FuncNode(inputs, outputs, func2)

    assert n1.get_nb_input() == 1
    assert n1.get_nb_output() == 1
    assert n2.get_nb_input() == 1
    assert n2.get_nb_output() == 1

    # Test IO and access by key or index
    n1.eval()
    n2.eval()
    assert n1.get_output('y') == 1
    assert n2.get_output('y') == [1, 2]
