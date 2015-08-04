from openalea.core.node import Node
from openalea.core.node_port import AbstractPort, InputPort, OutputPort

def test_port_creation():
    n = Node()
    p = InputPort(n)

    # TODO: hack gruuik
    p['name'] = "gruuik"

    assert len(p.get_tip()) > 0
    assert not p.is_hidden()

