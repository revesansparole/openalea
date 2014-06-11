# -*- python -*-
#
#       Visualea Manager applet
# 
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2013 INRIA - CIRAD - INRA
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
__revision__ = "$Id : "

DEBUG = False

import types
#import sys

from openalea.oalab.model.visualea import VisualeaModel
from openalea.vpltk.qt import QtCore, QtGui
from openalea.visualea.graph_operator import GraphOperator
from openalea.visualea import dataflowview
from openalea.core.compositenode import CompositeNodeFactory
#from openalea.plantgl.wralea.visualization import viewernode
from openalea.oalab.service.help import display_help


def get_code(self):
    """
    :return: workflow string representation to save it on disk
    """
    return self.applet.model.repr_code()


def actions(self):
    """
    :return: list of actions to set in the menu.
    """
    return self._actions


def mainMenu(self):
    """
    :return: Name of menu tab to automatically set current when current widget
    begin current.
    """
    return "Simulation"


class VisualeaModelController(object):
    default_name = VisualeaModel.default_name
    default_file_name = VisualeaModel.default_file_name
    pattern = VisualeaModel.pattern
    extension = VisualeaModel.extension
    icon = VisualeaModel.icon

    def __init__(self, name="workflow.wpy", code="", model=None, filepath=None, interpreter=None, editor_container=None, parent=None):
        self.name = name
        self.filepath = filepath
        if model:
            self.model = model
        else:
            self.model = VisualeaModel(name=name, code=code)
        self.parent = parent
        self.editor_container = editor_container
        self._widget = None
        self.interpreter = interpreter

    def instanciate_widget(self):
        self._widget = dataflowview.GraphicalGraph.create_view(self.model._workflow, clone=True)
        self._clipboard = CompositeNodeFactory("Clipboard")

        GraphOperator.globalInterpreter = self.interpreter
        self._operator = GraphOperator(graph = self.model._workflow,
                                 graphScene = self._widget.scene(),
                                 clipboard  = self._clipboard,
                                 )
        self._widget.mainMenu = types.MethodType(mainMenu, self._widget)
        self._widget.applet = self
        self._widget._actions = None

        methods = {}
        methods['actions'] = actions
        methods['get_code'] = get_code
        methods['mainMenu'] = mainMenu

        self._widget = adapt_widget(self._widget, methods)
        # todo
        # viewernode.registerPlotter(self.controller._plugins['Viewer3D'].instance())

        # todo: use services
        self.widget().scene().focusedItemChanged.connect(self.item_focus_change)

        return self.widget()

    def item_focus_change(self, scene, item):
        """
        Set doc string in Help widget when focus on node changed
        """
        assert isinstance(item, dataflowview.vertex.GraphicalVertex)
        txt = item.vertex().get_tip()
        # todo: use services
        display_help(txt)
    
    def focus_change(self):
        """
        Set doc string in Help widget when focus changed
        """
        txt = """
<H1><IMG SRC=%s
 ALT="icon"
 HEIGHT=25
 WIDTH=25
 TITLE="Visualea logo">Visualea</H1>

More informations: http://openalea.gforge.inria.fr/doc/openalea/visualea/doc/_build/html/contents.html        
"""%str(self.icon)
        # todo: use services
        display_help(txt)

    def widget(self):
        """
        :return: the edition widget
        """
        return self._widget     
        
    def run(self, *args, **kwargs):
        # todo : register plotter
        """
        viewernode = sys.modules['openalea.plantgl.wralea.visualization.viewernode']
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('Viewer3D'):
                viewernode.registerPlotter(self.controller._plugins['Viewer3D'].instance())
        else:
            if self.controller.applets.has_key('Viewer3D'):
                viewernode.registerPlotter(self.controller.applets['Viewer3D'])"""
        return self.model(*args, **kwargs)

    def animate(self, *args, **kwargs):
        # todo : register plotter
        """
        viewernode = sys.modules['openalea.plantgl.wralea.visualization.viewernode']
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('Viewer3D'):
                viewernode.registerPlotter(self.controller._plugins['Viewer3D'].instance())
        else:
            if self.controller.applets.has_key('Viewer3D'):
                viewernode.registerPlotter(self.controller.applets['Viewer3D'])"""
        return self.model.animate(*args, **kwargs)
        
    def step(self, *args, **kwargs):
        return self.model.step(*args, **kwargs)
        
    def stop(self, *args, **kwargs):
        return self.stop(*args, **kwargs)

    def reinit(self, *args, **kwargs):
        return self.model.init(*args, **kwargs)


def adapt_widget(widget, methods):
    method_list = ['actions', 'get_code', 'mainMenu']
    def check():
        for m in method_list:
            if m not in methods:
                raise NotImplementedError(m)
    check()
    for m in method_list:
        widget.__setattr__(m, types.MethodType(methods[m], widget))
    return widget