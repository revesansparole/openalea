# -*- python -*-
#
#       OpenAlea.SoftBus: OpenAlea Software Bus
#
#       Copyright 2006 INRIA - CIRAD - INRA
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
"""Test the subgraph module"""

__license__ = "Cecill-C"
__revision__ = " $Id$ "

from nose.tools import with_setup
import os
import shutil

from openalea.core.pkgmanager import PackageManager
from openalea.core.compositenode import CompositeNodeFactory, CompositeNode
from openalea.core.node_factory import Factory


def setup_func():
    pass


def teardown_func():
    pth = "MyTestPackage"
    if os.path.exists(pth):
        shutil.rmtree(pth)


@with_setup(setup_func, teardown_func)
def test_compositenodewriter():
    pm = PackageManager()
    pm.init("pkg")

    sg = CompositeNode(inputs=[dict(name="%d" % i) for i in xrange(3)],
                       outputs=[dict(name="%d" % i) for i in xrange(4)],
                       )

    # build the compositenode factory
    addid = sg.add_node(pm.get_node("pkg_test", "+"))
    val1id = sg.add_node(pm.get_node("pkg_test", "float"))
    val2id = sg.add_node(pm.get_node("pkg_test", "float"))
    val3id = sg.add_node(pm.get_node("pkg_test", "float"))

    sg.connect(val1id, 0, addid, 0)
    sg.connect(val2id, 0, addid, 1)
    sg.connect(addid, 0, val3id, 0)
    sg.connect(val3id, 0, sg.id_out, 0)
    sgfactory = CompositeNodeFactory("addition")
    sg.to_factory(sgfactory)
    # Package
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.gforge.inria.fr'}

    package1 = pm.create_user_package("MyTestPackage",
                                      metainfo, os.path.curdir)
    package1.add_factory(sgfactory)
    print package1.keys()
    assert 'addition' in package1
    package1.write()

    sg = sgfactory.instantiate()

    sg.node(val1id).set_input(0, 2.)
    sg.node(val2id).set_input(0, 3.)

    # evaluation
    sg()
    print sg.node(val3id).get_output(0)
    assert sg.node(val3id).get_output(0) == 5.

    assert len(sg) == 6

    pm.init("MyTestPackage")
    newsg = pm.get_node('MyTestPackage', 'addition')
    assert len(newsg) == 6


def setup_func2():
    pass


def teardown_func2():  # avoid collision with other tests
    pth = "MyTestPackage2"
    if os.path.exists(pth):
        shutil.rmtree(pth)


@with_setup(setup_func2, teardown_func2)
def test_nodewriter():
    """test node writer"""
    pm = PackageManager()
    pm.init("pkg")

    # Package
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.gforge.inria.fr'}

    package1 = pm.create_user_package("MyTestPackage2",
                                      metainfo, os.path.curdir)
    assert package1 is not None

    nf = package1.create_user_node(name="mynode",
                                   category='test',
                                   description="descr",
                                   inputs=(),
                                   outputs=(),
                                   )
    package1.write()
    pm.init("MyTestPackage2")
    newsg = pm.get_node('MyTestPackage2', 'mynode')
    package1.remove_files()
