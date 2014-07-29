# -*- python -*-
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2014 INRIA - CIRAD - INRA
#
#       File author(s): Julien Coste <julien.coste@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
from openalea.oalab.model.parse import get_docstring, parse_function, parse_input_and_output, parse_docstring, parse_doc


def test_ast_getdoc():
    model_src = '''"""
This is the doc of my model
"""

print "ok"
result = 42


"""
ok
"""
'''
    d = get_docstring(model_src)

    real_d = "This is the doc of my model"
    assert len(real_d), len(d)


def test_docstring_oneline():
    model_src = '''"""
model1(x,y)->r

beautifull doc
"""

r = x + y
'''
    d = get_docstring(model_src)
    model, inputs, outputs = parse_function(d)
    assert model == "model1"
    assert inputs == ['x', 'y']
    assert outputs == ['r']


def test_docstring_input():
    model_src = '''"""

input = x:int=4, y:float=3.14, z, debug:bool
output = success

beautifull doc
"""

print "ok"
'''
    d = get_docstring(model_src)
    inputs, outputs = parse_input_and_output(d)
    assert inputs
    assert outputs


def test_docstring_input():
    doc0 = "input = x, y, z"
    model, inputs, outputs = parse_doc(doc0)
    assert inputs[0].name == "x"
    assert inputs[1].name == "y"
    assert inputs[2].name == "z"

    doc1 = '''
input = x:int=4, y:float=3.14, z, debug:bool
output = success

beautifull doc
'''
    model, inputs, outputs = parse_doc(doc1)
    assert inputs[0].name == "x"
    assert inputs[0].default == "4"
    assert inputs[0].interface == "int"
    assert inputs[1].name == "y"
    assert inputs[1].default == "3.14"
    assert inputs[1].interface == "float"
    assert inputs[2].name == "z"
    assert inputs[3].name == "debug"
    assert inputs[3].interface == "bool"

    doc2 = '''
input = x=4, y:int, z, debug:bool
output = success

beautifull doc
'''
    model, inputs, outputs = parse_doc(doc2)
    assert inputs[0].name == "x"
    assert inputs[0].default == "4"
    assert inputs[1].name == "y"
    assert inputs[1].interface == "int"
    assert inputs[2].name == "z"
    assert inputs[3].name == "debug"
    assert inputs[3].interface == "bool"

    doc3 = "input = x=[1,2,3], y=(1,2), z=(1,), a=4, b"
    model, inputs, outputs = parse_doc(doc3)
    assert inputs[0].name == "x"
    assert inputs[0].default == "[1,2,3]"
    assert inputs[1].name == "y"
    assert inputs[1].default == "(1,2)"
    assert inputs[2].name == "z"
    assert inputs[2].default == "(1,)"
    assert inputs[3].name == "a"
    assert inputs[3].default == "4"
    assert inputs[4].name == "b"

    doc4 = "input = x=[[1,2,3],[1,2,3],[1,2,3]], y=((1,2,3),(1,2,3),(1,2,3))"
    model, inputs, outputs = parse_doc(doc4)
    assert inputs[0].name == "x"
    assert inputs[0].default == "[[1,2,3],[1,2,3],[1,2,3]]"
    assert inputs[1].name == "y"
    assert inputs[1].default == "((1,2,3),(1,2,3),(1,2,3))"

    doc5 = "input = x=[(1,2,3),[1,2,3],[(1,2),(3)]]"
    model, inputs, outputs = parse_doc(doc5)
    assert inputs[0].name == "x"
    assert inputs[0].default == "[(1,2,3),[1,2,3],[(1,2),(3)]]"


def test_docstring_output():
    doc0 = "output = x, y, z"
    model, inputs, outputs = parse_doc(doc0)
    assert outputs[0].name == "x"
    assert outputs[1].name == "y"
    assert outputs[2].name == "z"

    doc1 = '''
input = x:int=4, y:float=3.14, z, debug:bool
output = success

beautifull doc
'''
    model, inputs, outputs = parse_doc(doc1)
    assert outputs[0].name == "success"

    doc2 = '''
input = x=4, y:int, z, debug:bool
output = success:bool

beautifull doc
'''
    model, inputs, outputs = parse_doc(doc2)
    assert outputs[0].name == "success"
    assert outputs[0].interface == "bool"

    doc3 = "output = x=[1,2,3], y=(1,2), z=(1,), a=4, b"
    model, inputs, outputs = parse_doc(doc3)
    assert outputs[0].name == "x"
    assert outputs[0].default == "[1,2,3]"
    assert outputs[1].name == "y"
    assert outputs[1].default == "(1,2)"
    assert outputs[2].name == "z"
    assert outputs[2].default == "(1,)"
    assert outputs[3].name == "a"
    assert outputs[3].default == "4"
    assert outputs[4].name == "b"

    doc4 = "output = x=[[1,2,3],[1,2,3],[1,2,3]], y=((1,2,3),(1,2,3),(1,2,3))"
    model, inputs, outputs = parse_doc(doc4)
    assert outputs[0].name == "x"
    assert outputs[0].default == "[[1,2,3],[1,2,3],[1,2,3]]"
    assert outputs[1].name == "y"
    assert outputs[1].default == "((1,2,3),(1,2,3),(1,2,3))"

    doc5 = "output = x=[(1,2,3),[1,2,3],[(1,2),(3)]]"
    model, inputs, outputs = parse_doc(doc5)
    assert outputs[0].name == "x"
    assert outputs[0].default == "[(1,2,3),[1,2,3],[(1,2),(3)]]"


def test_docstring_unknow():
    model_src = '''"""
model1(x,y)->r
input = x:int=4, y:float=3.14

beautifull doc
"""

print "ok"
'''
    model, inputs, outputs = parse_docstring(model_src)

    assert model == "model1"
    assert len(inputs) == 2
    assert len(outputs) == 1
    assert inputs[0].name == "x"
    assert inputs[0].default == "4"
    assert inputs[0].interface == "int"
    assert inputs[1].name == "y"
    assert inputs[1].default == "3.14"
    assert inputs[1].interface == "float"

