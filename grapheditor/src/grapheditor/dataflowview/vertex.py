# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "Cecill-C"
__revision__ = " $Id: vertex.py 2051 2009-12-21 11:07:28Z chopard $ "

import weakref,sys
from PyQt4 import QtCore, QtGui
from openalea.core import observer
from openalea.core.node import InputPort, OutputPort
from openalea.grapheditor import qtutils
from openalea.grapheditor.qtutils import mixin_method
from openalea.grapheditor import qtgraphview
from . import painting


"""

"""

 

class GraphicalVertex(QtGui.QGraphicsWidget, qtgraphview.Vertex):

    #color of the small box that indicates evaluation
    eval_color = QtGui.QColor(255, 0, 0, 200)

    def __init__(self, vertex, graph, parent=None):
        QtGui.QGraphicsWidget.__init__(self, parent)
        qtgraphview.Vertex.__init__(self, vertex, graph)
        self.set_painting_strategy(painting.default_dataflow_paint)
        self.setZValue(1)

        # ---Small box when the vertex is being evaluated---
        self.modified_item = QtGui.QGraphicsRectItem(5,5,7,7, self)
        self.modified_item.setBrush(self.eval_color)
        self.modified_item.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.modified_item.setVisible(False)

        # ---Sub items layout---
        layout = QtGui.QGraphicsLinearLayout()
        layout.setOrientation(QtCore.Qt.Vertical)
        layout.setSpacing(2)

        self._inPortLayout  = QtGui.QGraphicsLinearLayout()
        self._caption       = QtGui.QLabel()
        self._outPortLayout = QtGui.QGraphicsLinearLayout()
        self._captionProxy  = qtutils.AleaQGraphicsProxyWidget(self._caption)
        self._inPortLayout.setSpacing(0.0)
        self._outPortLayout.setSpacing(0.0)

        #minimum heights
        self._inPortLayout.setMinimumHeight(GraphicalPort.HEIGHT)
        self.set_caption("")
        self._outPortLayout.setMinimumHeight(GraphicalPort.HEIGHT)

        layout.addItem(self._inPortLayout)
        layout.addItem(self._captionProxy)
        layout.addItem(self._outPortLayout)

        layout.setAlignment(self._inPortLayout, QtCore.Qt.AlignHCenter)
        layout.setAlignment(self._outPortLayout, QtCore.Qt.AlignHCenter)
        layout.setAlignment(self._captionProxy, QtCore.Qt.AlignHCenter)

        self.setLayout(layout)
                
        self.initialise_from_model()

    def initialise_from_model(self):
        qtgraphview.Vertex.initialise_from_model(self)
        self.vertex().exclusive_command(self, self.vertex().simulate_construction_notifications)


    #####################################
    # pseudo-protected or private stuff #
    #####################################
    def _all_inputs_visible(self):
        count = self._inPortLayout.count()
        for i in range(count):
            if not self._inPortLayout.itemAt(i).graphicsItem().isVisible():
                return False
        return True
    
    def __add_in_connection(self, port):
        graphicalConn = GraphicalPort(port)
        self._inPortLayout.addItem(graphicalConn)

    def __add_out_connection(self, port):
        graphicalConn = GraphicalPort(port)
        self._outPortLayout.addItem(graphicalConn)


    ####################
    # Observer methods #
    ####################
    def notify(self, sender, event): 
        """ Notification sent by the vertex associated to the item """
        if event is None : return

        #this one simply catches events like becoming lazy
        #or blocked of user app...
        if(event[0] in ["internal_data_changed", "data_modified"]):
            self.update()

        elif(event[0]=="tooltip_modified"):
            tt = event[1]
            if tt is None:
                tt=""
            self._captionProxy.setToolTip(tt)
            self.setToolTip(tt)

        elif(event[0] == "start_eval"):
            self.modified_item.setVisible(self.isVisible())
            self.modified_item.update()
            self.update()
            QtGui.QApplication.processEvents()

        elif(event[0] == "stop_eval"):
            self.modified_item.setVisible(False)
            self.modified_item.update()
            self.update()
            QtGui.QApplication.processEvents()

        elif(event[0] == "caption_modified"):
            self.set_caption(event[1])

        elif(event[0] == "metadata_changed" and event[1]=="userColor"):
            if event[2] is None:
                self.vertex().get_ad_hoc_dict().set_metadata("useUserColor", False, False)
            self.update()

        elif(event[0] == "input_port_added"):
            self.__add_in_connection(event[1])

        elif(event[0] == "output_port_added"):
            self.__add_out_connection(event[1])
            
            
        qtgraphview.Vertex.notify(self, sender, event)
        

    def set_caption(self, caption):
        """Sets the name displayed in the vertex widget, doesn't change
        the vertex data"""
        if caption == "":
            caption = " "
        self._caption.setText(caption)
        layout = self.layout()
        if(layout): layout.updateGeometry()

    ###############################
    # ----Qt World overloads----  #
    ###############################
    def setGeometry(self, geom):
        #forcing a full recomputation of the geometry so that shrinking works
        pos = self.pos()
        QtGui.QGraphicsWidget.setGeometry(self, QtCore.QRectF(pos.x(), pos.y(),-1.0,-1.0))
        pos = self.pos()
        self.vertex().get_ad_hoc_dict().set_metadata('position', 
                                                     [pos.x(), pos.y()])
        self.shapeChanged=True

    polishEvent = mixin_method(qtgraphview.Vertex, QtGui.QGraphicsWidget,
                               "polishEvent")
    moveEvent = mixin_method(qtgraphview.Vertex, QtGui.QGraphicsWidget,
                             "moveEvent")
    mousePressEvent = mixin_method(qtgraphview.Vertex, QtGui.QGraphicsWidget,
                                   "mousePressEvent")
    itemChange = mixin_method(qtgraphview.Vertex, QtGui.QGraphicsWidget,
                              "itemChange")




class GraphicalPort(QtGui.QGraphicsWidget, qtgraphview.Element):
    """ A vertex port """
    MAX_TIPLEN = 2000
    __spacing  = 5.0
    WIDTH      = 10.0
    HEIGHT     = 10.0

    __size = QtCore.QSizeF(WIDTH+__spacing, 
                           HEIGHT)

    __nosize = QtCore.QSizeF(0.0, 0.0)

    def __init__(self, port):
        """
        """
        QtGui.QGraphicsWidget.__init__(self)
        qtgraphview.Element.__init__(self, port)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)        

        port.vertex().register_listener(self)
        self.setZValue(1.5)
        self.highlighted = False
        
        port.simulate_construction_notifications()

    def port(self):
        return self.get_observed()

    def notify(self, sender, event):
        if(event[0] in ["tooltip_modified", "stop_eval"]):
            self.__update_tooltip()

        elif(event[0]=="metadata_changed"):
            if(sender == self.port()):
                if(event[1]=="hide"):
                    if event[2]: #if hide
                        self.hide()
                    else:
                        self.show()
                    self.updateGeometry()
            elif(sender == self.port().vertex() and event[1]=="position"):
                self.__update_scene_center()

    def get_scene_center(self):
        pos = self.rect().center() + self.scenePos()
        return[pos.x(), pos.y()]
        
    def __update_scene_center(self):
        self.port().get_ad_hoc_dict().set_metadata("connectorPosition", 
                                                   self.get_scene_center())
    def __update_tooltip(self):
        node = self.port().vertex()
        if isinstance(self.port(), OutputPort):
            data = node.get_output(self.port().get_id())
        elif isinstance(self.port(), InputPort):
            data = node.get_input(self.port().get_id())
        s = str(data)
        if(len(s) > self.MAX_TIPLEN): s = "String too long..."
        #self.setToolTip("Value: " + s)
        self.setToolTip(self.port().get_tip(data) )
    
    def set_highlighted(self, val):
        self.highlighted = val
        self.update()

    ##################
    # QtWorld-Layout #
    ##################
    def size(self):
        size = self.__size
        if(not self.isVisible()):
            size = self.__nosize
        return size

    def sizeHint(self, blop, blip):
        return self.size()


    ##################
    # QtWorld-Events #
    ##################
    def mousePressEvent(self, event):
        graphview = self.scene().views()[0]
        if (graphview and event.buttons() & QtCore.Qt.LeftButton):
            graphview.new_edge_start(self.get_scene_center())
            return

    def paint(self, painter, option, widget):
        if(not self.isVisible()):
            return
        
        painter.setBackgroundMode(QtCore.Qt.TransparentMode)
        gradient = QtGui.QLinearGradient(0, 0, 10, 0)
        if self.highlighted:
            gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.red).light(120))
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkRed).light(120))
        else:         
            gradient.setColorAt(0.8, QtGui.QColor(QtCore.Qt.yellow).light(120))
            gradient.setColorAt(0.2, QtGui.QColor(QtCore.Qt.darkYellow).light(120))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))

        painter.drawEllipse(self.__spacing/2+1,1,self.WIDTH-2, self.HEIGHT-2)

