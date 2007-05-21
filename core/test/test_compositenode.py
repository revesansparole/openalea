# -*- python -*-
#
#       OpenAlea.SoftBus: OpenAlea Software Bus
#
#       Copyright or (C) or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Christophe Pradal <christophe.prada@cirad.fr>
#                       Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#



__doc__= """
Test the composite node module
"""



from openalea.core.pkgmanager import PackageManager
from openalea.core.compositenode import CompositeNodeFactory, CompositeNode
from openalea.core.node import gen_port_list
from openalea.core.core import Package, RecursionError 


# Test instantiation
def test_instantiate_compositenode():
       
    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    # build the compositenode factory
    addid = sg.add_node ( pm.get_node("Catalog.Maths", "+"))
    val1id = sg.add_node ( pm.get_node("Catalog.Data", "float")) 
    val2id = sg.add_node ( pm.get_node("Catalog.Data", "float"))
    val3id = sg.add_node ( pm.get_node("Catalog.Data", "float"))

    sg.connect (val1id, 0, addid, 0)
    sg.connect (val2id, 0, addid, 1)
    sg.connect (addid, 0, val3id, 0)

    sgfactory = CompositeNodeFactory("addition")
    sg.to_factory(sgfactory)

    # allocate the compositenode
    sg = sgfactory.instantiate()
    sg.node(val1id).set_input(0, 2.)
    sg.node(val2id).set_input(0, 3.)

    # evaluation
    sg()

    assert sg.node(val3id).get_output(0) == 5.

def test_compositenode_creation_without_edges():
       
    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    # build the compositenode factory
    addid = sg.add_node ( pm.get_node("Catalog.Maths", "+"))
    val1id = sg.add_node ( pm.get_node("Catalog.Data", "float")) 
    val2id = sg.add_node ( pm.get_node("Catalog.Data", "float"))
    val3id = sg.add_node ( pm.get_node("Catalog.Data", "float"))

    
    sgfactory = CompositeNodeFactory("addition")
    sg.to_factory(sgfactory)
    # allocate the compositenode
    sg = sgfactory.instantiate()

    assert len(sg) == 4+2


# Test conversion Composite Node to its Factory
def test_to_factory():
    """ Create a compositenode, generate its factory and reintantiate it """

    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    n1 = pm.get_node("Catalog.Data", "float")
    n2 = pm.get_node("Catalog.Data", "float")
    
    e1 = sg.add_node(n1)
    e2 = sg.add_node(n2)
    sg.connect(e1, 0, e2, 0)

    n1.set_input(0,34.)
    sg()
    assert n2.get_output(0) == 34.

    sgfactory = CompositeNodeFactory("factorytest")
    sg.to_factory(sgfactory)

    sg2 = sgfactory.instantiate()

    assert len(sg2.vertices()) == 2+2# two nodes + in/ou
    assert len(sg2.edges()) == 1

    sg2.node(e1).set_input(0, 3.)
    sg2()
    assert sg2.node(e2).get_output(0) == 3.

    return pm, sg, sgfactory
    

def test_to_factory2():
    
    pm, sg, sgfactory= test_to_factory()

    sg.to_factory( sgfactory )

    sg2= sgfactory.instantiate()

    assert len( sg )== len( sg2 )
    

# Test Recursion detection
#A REVOIR L'ORDRE A CHANGE
"""
def test_recursion_factory():

    pm = PackageManager ()
    pm.init()
    pkg = Package("compositenode", {})

    sgfactory1 = CompositeNodeFactory("graph1")
    sgfactory2 = CompositeNodeFactory("graph2")

    map (pkg.add_factory, (sgfactory1, sgfactory2))

    assert len(pkg.get_names()) == 2

    pm.add_package(pkg)
    
    # build the compositenode factory

    sgfactory1.add_nodefactory ( ("compositenode", "graph2"))
    sgfactory2.add_nodefactory ( ("compositenode", "graph1"))

    try:
        sg = sgfactory1.instantiate ()
        assert False
    except RecursionError:
        assert True
"""


# Test IO
def test_compositenodeio():

    pm = PackageManager ()
    pm.init()

    pkg = Package("compositenode", {})

    # create a compositenode with 2 in and 1 out
    # the compositenode does an addition
    sg = CompositeNode(inputs=(dict(name="in1",interface=None,value=None),\
                              dict(name="in2",interface=None,value=None)),
                      outputs=(dict(name="out",interface=None),),
                      )
    addid = sg.add_node ( pm.get_node("Catalog.Maths", "+"))

    sg.connect (sg.id_in, 0, addid, 0)
    sg.connect (sg.id_in, 1, addid, 1)
    sg.connect (addid, 0, sg.id_out, 0)
    
    sgfactory = CompositeNodeFactory("additionsg")
    sg.to_factory(sgfactory)

    sg1= sgfactory.instantiate()
    sg1.set_input(0,2.)
    sg1.set_input(1,3.)
    sg1()
    
    assert sg1.get_output(0) == 5.

    pkg.add_factory(sgfactory)
    pm.add_package(pkg)


    sg = CompositeNode()
    addid = sg.add_node ( pm.get_node("compositenode", "additionsg"))
    val1id = sg.add_node( pm.get_node("Catalog.Data", "float"))
    val2id = sg.add_node( pm.get_node("Catalog.Data", "float"))
    val3id = sg.add_node( pm.get_node("Catalog.Data", "float"))

    sg.connect (val1id, 0, addid, 0)
    sg.connect (val2id, 0, addid, 1)
    sg.connect (addid, 0, val3id, 0)

    sgfactory2 = CompositeNodeFactory("testio")
    sg.to_factory(sgfactory2)
    # allocate the compositenode
        
    sg = sgfactory2.instantiate()
    sg.node(val1id).set_input(0,2.)
    sg.node(val2id).set_input(0,3.)

    
    # evaluation
    sg()
    
    assert sg.node(val3id).get_output(0) == 5.


# Test  node addition
def test_addnode():

    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    # build the compositenode factory
    val1id = sg.add_node ( pm.get_node("Catalog.Data", "float"))
    val2id = sg.add_node ( pm.get_node("Catalog.Data", "float"))

    sg.connect (val1id, 0, val2id, 0)


    sgfactory = CompositeNodeFactory("testaddnode")
    sg.to_factory(sgfactory)
    # allocate the compositenode

    sg = sgfactory.instantiate()

    sg.node(val1id).set_input(0,2.)
    sg()
    assert sg.node(val2id).get_output(0) == 2.


    # Add a new node
    addid = sg.add_node ( pm.get_node("Catalog.Maths", "+"))
    sg.connect (val1id, 0, addid, 0)
    sg.connect (val2id, 0, addid, 1)
    
    sg.to_factory(sgfactory)
    sg = sgfactory.instantiate()
    sg.node(val1id).set_input(0, 3.)
    sg()
    assert sg.node(addid).get_output(0) == 6.


# Test multiple out connection
def test_multi_out_eval():
    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    # build the compositenode factory
    val1id = sg.add_node( pm.get_node("Catalog.Data", "string"))
    val2id = sg.add_node( pm.get_node("Catalog.Data", "string"))
    val3id = sg.add_node( pm.get_node("Catalog.Data", "string"))

    sg.connect (val1id, 0, val2id, 0)
    sg.connect (val1id, 0, val3id, 0)


    sgfactory = CompositeNodeFactory("testlazyeval")
    sg.to_factory(sgfactory)
    # allocate the compositenode
    sg = sgfactory.instantiate()

    sg.node(val1id).set_input(0,"teststring")
    sg()
    assert sg.node(val2id).get_output(0) == "teststring"
    assert sg.node(val3id).get_output(0) == "teststring"

    #partial evaluation
    sg.node(val1id).set_input(0, "teststring2")
    sg.eval_as_expression(val2id)
    assert sg.node(val2id).get_output(0) == "teststring2"
    
    sg.eval_as_expression(val3id)
    assert sg.node(val3id).get_output(0) == "teststring2"


# Test multiple out connection
def test_multi_in_eval():
    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    # build the compositenode factory
    val1id = sg.add_node( pm.get_node("Catalog.Data", "string"))
    val2id = sg.add_node( pm.get_node("Catalog.Data", "string"))
    val3id = sg.add_node( pm.get_node("Catalog.Data", "string"))

    sg.connect (val1id, 0, val3id, 0)
    sg.connect (val2id, 0, val3id, 0)


    sgfactory = CompositeNodeFactory("testlazyeval")
    sg.to_factory(sgfactory)
    # allocate the compositenode
    sg = sgfactory.instantiate()

    sg.node(val1id).set_input(0,"teststring1")
    sg.node(val2id).set_input(0,"teststring2")
    sg()
    assert sg.node(val3id).get_output(0) == "['teststring1', 'teststring2']"


from nose import with_setup
from openalea.core.path import path


def setup_func():
    wralea = path('data')/'jcd_dec.py'
    wralea.copy(path('data')/'jcd_wralea.py')

def teardown_func():
    wralea= path('data')
    map(lambda f: f.remove(),wralea.glob('*wralea*'))


@with_setup(setup_func,teardown_func)
def test_eval_bug():

    pm= PackageManager()
    pm.init()

    name= 'jcd_test'

    sg= CompositeNode()
    cid = sg.add_node(pm.get_node(name,'cid'))
    wid = sg.add_node(pm.get_node(name,'wid'))
    eid = sg.add_node(pm.get_node(name,'eid'))
    dbg = sg.add_node(pm.get_node(name,'dbg'))
    dbg1 = sg.add_node(pm.get_node(name,'dbg'))
    
    sg.connect( cid, 0, dbg, 0 )
    sg.connect( wid, 0, dbg1, 0 )
    sgf= CompositeNodeFactory("test_eval")
    sg.to_factory(sgf)

    sg = sgf.instantiate()
    sg()
    
    print sg.node(dbg).get_output(0)
    print sg.node(dbg1).get_output(0)

    assert sg.node(dbg).get_output(0) == 0
    assert sg.node(dbg1).get_output(0) == 1

    
    

