"""Node tests"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "


from nose.tools import assert_raises

from openalea.core.node import Node, FuncNode


class Dummy(object): pass


def test_node_init():
    node = Node()

    assert len(node.get_tip()) > 0
    assert callable(node.get_process_obj())


def test_node_factory():
    node = Node()

    assert node.get_factory() is None
    assert_raises(TypeError, lambda: node.set_factory("toto"))
    fac = Dummy()
    fac.name = "toto"
    node.set_factory(fac)
    assert node.get_factory().name == "toto"


def test_node_id():
    node = Node()

    assert node.get_id() is None
    node.set_id("toto")
    assert node.get_id() == "toto"


def node_data():
    node = Node()

    assert node.get_data("toto") is None
    assert node.get_data("toto", ()) == ()

    node.set_data("a", 1)
    assert node.get_data("a") == 1
    assert node.get_data("a", "0") == 1


def test_node_lazy():
    node = Node()

    assert node.is_lazy()
    node.set_lazy(True)
    assert node.is_lazy()
    node.set_lazy(False)
    assert not node.is_lazy()


def test_node_delay():
    node = Node()

    assert node.get_delay() == 0
    node.set_delay(0)
    assert node.get_delay() == 0
    node.set_delay(10)
    assert node.get_delay() == 10
    assert_raises(ValueError, lambda: node.set_delay('a'))


def test_node_block():
    node = Node()

    assert not node.is_block()
    node.set_block(True)
    assert node.is_block()
    node.set_block(False)
    assert not node.is_block()


def test_node_caption():
    node = Node()

    assert node.get_caption() == ""
    node.set_caption("toto")
    assert node.get_caption() == "toto"
    node.set_caption("toto")
    assert node.get_caption() == "toto"
    node.set_caption(10)
    assert node.get_caption() == str(10)


def test_node_add_input():
    node = Node()

    node.add_input(name='toto1')
    assert node.get_nb_input() == 1
    node.add_input(name='toto2', interface='IInt')
    assert node.get_nb_input() == 2

    assert_raises(KeyError, lambda: node.add_input(name='toto1'))
    assert_raises(KeyError, lambda: node.get_input_port(name='AAAA'))

    p = node.get_input_port('toto1')
    assert node.get_input_port(p.get_id()) == p
    assert p.get_interface() is None
    p = node.get_input_port('toto2')
    assert node.get_input_port(p.get_id()) == p
    assert str(p.get_interface()) == 'IInt'


def test_node_add_output():
    node = Node()

    node.add_output(name='toto1')
    assert node.get_nb_output() == 1
    node.add_output(name='toto2', interface='IInt')
    assert node.get_nb_output() == 2

    assert_raises(KeyError, lambda: node.add_output(name='toto1'))
    assert_raises(KeyError, lambda: node.get_output_port(name='AAAA'))

    p = node.get_output_port('toto1')
    assert node.get_output_port(p.get_id()) == p
    assert p.get_interface() is None
    p = node.get_output_port('toto2')
    assert node.get_output_port(p.get_id()) == p
    assert str(p.get_interface()) == 'IInt'




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
