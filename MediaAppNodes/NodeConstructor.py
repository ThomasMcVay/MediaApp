#===============================================================================
# @Author: Madison Aster
# @ModuleDescription: 
# @License:
#    MediaApp Library - Python Package framework for developing robust Media 
#                       Applications with Qt Library
#    Copyright (C) 2013 Madison Aster
#    
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License version 2.1 as published by the Free Software Foundation;
#    
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#    See LICENSE in the root directory of this library for copy of
#    GNU Lesser General Public License and other license details.
#===============================================================================

from Qt import QtGui, QtCore, QtWidgets
    
import math

import AppCore
from MediaAppKnobs import *

class NodeConstructor(object):
    def __init__(self, parent):
        super(NodeConstructor, self).__init__()
        ################################
        self.parent = parent
        
        self.knobs = []

        self['ClassName'] = StrKnob('Node')
        self['ClassName'].shown = False
        
        self['nodeName'] = TitleKnob('Node000')
        
        self['xpos'] = IntKnob(self.parent.getAssignedXPos())
        self['ypos'] = IntKnob(self.parent.getAssignedYPos())
        self['selected'] = BoolKnob(False)
        self['xpos'].shown = False
        self['ypos'].shown = False
        #self['selected'].shown = False
        
        
        self.shapeTransform = QtGui.QTransform()
        self.nodeShape()
        self.mapNodeShape()
        
        self['width'] = IntKnob(self.rectLowHigh[1][0])
        self['width'].shown = False
        self['height'] = IntKnob(self.rectLowHigh[1][1])
        self['height'].shown = False
        #Doesn't really need to be initialized, but here for reference
        #self.parent = None
        
        
        self.inputPaths = [None]
        self.setCurrentInputIndex(0)
        
    def __len__(self):
        return len(self.knobs)
    def __getitem__(self, key):
        for knob in self.knobs:
            if knob.name.text() == key:
                return knob
        else:
            return None
    def __delitem__(self, key):
        for i, knob in enumerate(self.knobs):
            if knob.name.text() == key:
                del self.knobs[i]
    def __setitem__(self, key, value):
        if 'knob' in type(value).__name__.lower():
            if self[key] != None:
                del self[key]       #BUG widgets don't get destroyed when we do a simple delete
            #Node subclass has assigned knob the name key, so we tell the knob that here.   
            value.name.setText(key)
            value.parent = self
            self.knobs.append(value)
        else:
            self[key].setValue(value)
    def __iter__(self):
        for knob in self.knobs:
            yield knob
    def __reversed__(self):
        return reversed(self.knobs)
        
        
    def name(self):
        return self['nodeName'].getValue()
    def toKnob(self, a):
        return self[a]

    def nodeShape(self):
        #Override Me!
        self.polyShape = [[0,0],[70,0],[74,8],[70,16],[0,16]]
        
        #FLAW: add this to appPrefs/appSettings somehow
        self.color1 = QtGui.QColor(238,238,238)
        self.color2 = QtGui.QColor(122,122,122)
        
    def mapNodeShape(self):
        #Center Shape, create rectangle, midpoint
        self.coordList, self.rectLowHigh, self.rectMidPoint = self.coordListCentered(self.polyShape)
        
        #Convert Shape and Rectangle
        self.polyShape = self.coordListConvert(self.coordList)
        self.nodeRectangle = self.rectConvert(self.rectLowHigh)
        self.nodeRectangleI = self.nodeRectangle.toRect()
        
        #Create selectShape
        selectShapeTrans = QtGui.QTransform.fromScale((self.nodeRectangle.width()-3)/self.nodeRectangle.width(), (self.nodeRectangle.height()-3)/self.nodeRectangle.height())
        self.selectShape = selectShapeTrans.map(self.polyShape).translated(1.5,1.5)
        
        #colorTable = 0xCC6666
        self.nodeGradientStart = QtCore.QPointF(0, self.rectLowHigh[0][1])
        self.nodeGradientStop = QtCore.QPointF(0, self.rectLowHigh[1][1])
        self.nodeGradient = QtGui.QLinearGradient(self.nodeGradientStart, self.nodeGradientStop)
        self.nodeGradient.setSpread(QtGui.QGradient.RepeatSpread)
        self.nodeGradient.setColorAt(0, self.color1)
        self.nodeGradient.setColorAt(1, self.color2)
        self.gradientBrush = QtGui.QBrush(self.nodeGradient)
        
        
        Metrics = AppCore.AppPrefs['AppFontMetrics']
        textHeight = Metrics.boundingRect(self.nodeRectangle.toRect(), QtCore.Qt.TextWrapAnywhere, self['nodeName'].getValue()).height()
        textLines = math.ceil(textHeight/float(Metrics.lineSpacing()))
        stretchHeight = textLines*(Metrics.lineSpacing()/self.nodeRectangle.height())

        #self.shapeTransform.scale(1,stretchHeight)
        self.scaledPolyShape = self.shapeTransform.map(self.polyShape)
        
        self.getPos()   
    def getPos(self):
        self.lastX = self['xpos'].getValue()*self.parent.XPixelsPerUnit
        self.lastY = self['ypos'].getValue()*self.parent.YPixelsPerUnit
        
        self.mappedPolyShape = self.scaledPolyShape.translated(self.lastX,self.lastY)
        self.mappedSelectShape = self.shapeTransform.map(self.selectShape).translated(self.lastX,self.lastY)
        self.mappedNodeRect = self.shapeTransform.mapRect(self.nodeRectangle).translated(self.lastX,self.lastY)

        nodeRectX = self.shapeTransform.mapRect(self.nodeRectangle).x()
        nodeRectY = self.shapeTransform.mapRect(self.nodeRectangle).y()
        nodeRectH = self.shapeTransform.mapRect(self.nodeRectangle).height()
        
        #FLAW: add this to appPrefs somehow
        self.nodeGradient.setStart(nodeRectX+self.lastX,nodeRectY+self.lastY)
        self.nodeGradient.setFinalStop(nodeRectX+self.lastX,nodeRectH-nodeRectY+self.lastY)
        self.gradientBrush = QtGui.QBrush(self.nodeGradient)
        
    def coordListRect(self, coordList):
        #Takes: coordList = [[0,0],[70,0],[74,8]]
        #Returns: rectLowHigh = [[0,0],[74,8]]
        dimensions = len(coordList[0])
        lowValues = []
        highValues = []
        for a in range(dimensions):
            lowValues.append(None)
            highValues.append(None)
            for b in coordList:
                if lowValues[a] == None or b[a] < lowValues[a]:
                    lowValues[a] = b[a]
                if highValues[a] == None or b[a] > highValues[a]:
                    highValues[a] = b[a]
        return [lowValues, highValues]    
    def coordListConvert(self, coordList):
        #Takes: coordList = [[0,0],[70,0],[74,8]]
        #Returns: QPolyGonF()
        polyShapeQT = []
        for a in coordList:
            polyShapeQT.append(QtCore.QPointF(a[0],a[1]))
        return QtGui.QPolygonF(polyShapeQT)
    def coordListCentered(self, coordList, rectLowHigh = None):
        #coordList Takes: coordList = [[0,0],[70,0],[74,8]]
        #rectLowHigh Takes: rectLowHigh = [[0,0],[74,8]]
        #    only necessary to manually offset the midpoint
        #Returns: coordList in coordList format, centered around 0 in each dimension
        if rectLowHigh == None:
            rectLowHigh = self.coordListRect(coordList)
        dimensions = len(coordList[0])
        rectMidPoint = []
        for a in range(dimensions):
            for b in range(len(coordList)):
                #move shape so that top, and left boundaries of rect = 0
                coordList[b][a] -= rectLowHigh[0][a]
                rectLowHigh[0][a] -= rectLowHigh[0][a]
                rectLowHigh[1][a] -= rectLowHigh[0][a]
            rectMidPoint.append((rectLowHigh[1][a]-rectLowHigh[0][a])/2)
        return coordList, rectLowHigh, rectMidPoint    
    def rectConvert(self, rectLowHigh):
        #Takes: rectLowHigh = [[0,0],[74,16]]
        #Returns: QRectF(lowX, highY, width, height)
        lowX = rectLowHigh[0][0]
        lowY = rectLowHigh[0][1]
        width = rectLowHigh[1][0]-rectLowHigh[0][0]
        height = rectLowHigh[1][1]-rectLowHigh[0][1]
        return QtCore.QRectF(lowX, lowY, width, height)
    def fallsAround(self, X, Y):
        if X == None:
            X = self.mappedNodeRect.left()
        if Y == None:
            Y = self.mappedNodeRect.top()
        return self.mappedNodeRect.contains(X,Y)
    
    def drawNode(self, painter):
        #FLAW: maybe there is a better way here than to constantly check to see if the node changes pos
        if self.lastX != self['xpos'].getValue() or self.lastY != self['ypos'].getValue():
            self.getPos()
        
        #LAYER0: Node Input Paths
        pinPointX = self.mappedNodeRect.center().x()
        pinPointY = self.mappedNodeRect.top()
        for node in self.inputPaths:
            if node is not None:
                painter.setPen(AppCore.AppPrefs[self.parent.className+'-pathPen01'])
                fromPointX = node.mappedNodeRect.center().x()
                fromPointY = node.mappedNodeRect.bottom()
                
                #TODO: change this to QtGui.QGraphicsLineItem
                painter.drawLine(fromPointX,fromPointY, pinPointX,pinPointY)
                
        #LAYER1: NodeShape/Gradient
        painter.setBrush(self.gradientBrush)
        painter.setPen(AppCore.AppPrefs[self.parent.className+'-nodeTrimPen'])
        painter.drawConvexPolygon(self.mappedPolyShape)
        
        #LAYER2: NodeSelectShape
        if self.toKnob('selected').getValue() == True:
            painter.setBrush(AppCore.AppPrefs[self.parent.className+'-nodeSelectColor'])
            painter.setPen(AppCore.AppPrefs[self.parent.className+'-nodeSelectPen'])
            painter.drawConvexPolygon(self.mappedSelectShape)
        
        #LAYER3: NodeText
        painter.drawText(self.mappedNodeRect,QtCore.Qt.TextWrapAnywhere,self['nodeName'].getValue())
    
        #LAYER4: Node Channels
        
        #LAYER5: Node Thumbnail
        
        self.drawNodeExtra(painter)
    def drawNodeExtra(self, painter): #Override me!
        pass
                
    def setName(self, value):
        self['nodeName'].setValue(value)
        #self.setObjectName(value)
        #self.setWindowTitle(value)
    def attachKnobs(self):
        #for widget in self.widget().panelLayout.findChildren(object):
        #    self.widget().panelLayout.removeWidget(widget)
        LineList = []
        #LineLayout = QtWidgets.QHBoxLayout()
        #LineLayout.setContentsMargins(0,0,0,0)
        #LineLayout.setSpacing(0)
        for knob in self:
            if type(knob) is not TitleKnob:
                if knob.shown is True:
                    if knob not in self.widget().panelLayout.findChildren(object):
                        #if knob.newline is True:
                            #if self.hasStretch(LineLayout) is False:
                            #    LineLayout.addWidget(Spacer())
                        LineLayout = QtWidgets.QHBoxLayout()
                        LineLayout.setContentsMargins(0,0,0,0)
                        LineLayout.setSpacing(0)
                        
                        LineLayout.addWidget(knob)
                        LineList.append(LineLayout)
        if self.hasStretch(LineLayout) is False:
            LineLayout.addWidget(Spacer())
        LineList.append(LineLayout)
        
        for layout in LineList:
            self.widget().panelLayout.addLayout(layout)
        self.widget().panelLayout.addWidget(Spacer())
    def hasStretch(self, layout):
        for index in range(layout.count()):
            if layout.itemAt(index).widget().sizePolicy().horizontalPolicy() == QtWidgets.QSizePolicy.MinimumExpanding:
                return True
            elif layout.itemAt(index).widget().sizePolicy().horizontalPolicy() == QtWidgets.QSizePolicy.Expanding:
                return True
            elif layout.itemAt(index).widget().sizePolicy().horizontalPolicy() == QtWidgets.QSizePolicy.Preferred:
                return True
        else:
            return False
        
    def setParent(self, value):
        self.parent = value
    def update(self):
        self.parent.update()
        
    def setCurrentInputIndex(self, index):
        self.currentInput = index

class PropertiesWidget(QtWidgets.QWidget):
    def __init__(self):
        super(PropertiesWidget, self).__init__()
        #self.setAccessibleName('PropertiesWidget')   #override visible name here or elsewhere
        ##################################
        #self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        #self.setMaximumSize(200,200)
        
        self.panelLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.panelLayout)
  
    def addKnob(widget):
        self.panelLayout.addWidget(widget)
    def sizeHint(self):
        return QtCore.QSize(400,100)

class PropertiesDockWidget(QtWidgets.QDockWidget):
    def __init__(self):
        super(PropertiesDockWidget, self).__init__()
        ##################################
        self.setWidget(PropertiesWidget())
        self.widget().setPalette(AppCore.App.palette())
        
        #self.visibilityChanged.triggered.connect(self.unDock)
        #self.toggleViewAction().triggered.connect(self.unDock)
        self.setAcceptDrops(True)
        self.setFocusPolicy(AppCore.AppSettings['FocusPolicy'])
        
        self.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
        
        #Parent child relationship workaround
        self.docked = False
    def closeEvent(self, event):
        AppCore.PropertiesBin.unDockThisWidget(self)
    def focusInEvent(self, event):
        AppCore.setActiveNode(self)

class WidgetLinkedNode(NodeConstructor, PropertiesDockWidget):
    def __init__(self, parent):
        super(WidgetLinkedNode, self).__init__(parent)
        self.LinkedWidget = None
    def setLinkedWidget(self, widget):
        self.LinkedWidget = widget
        if self.LinkedWidget.getLinkedNode() != self:
            self.LinkedWidget.setLinkedNode(self)
    def getLinkedWidget(self):
        return self.LinkedWidget        

class GraphNode(WidgetLinkedNode):
    def __init__(self, parent):
        super(GraphNode, self).__init__(parent)
        self.setTitleBarWidget(self['nodeName'])
    def setInput(self, index, object):
        self.inputPaths[index] = object
        self.inputsChanged()
    def setCurrentInputIndex(self, index):
        self.currentInput = index
    def getInput(self, *args):
        if len(args) < 1:
            return self.inputPaths[self.getCurrentInputIndex()]
        else:
            return self.inputPaths[args[0]]
    def getInputs(self):
        return self.inputPaths
    def getCurrentInputIndex(self):
        return self.currentInput
    def inputsChanged(self):
        #overridable slot
        pass  
    def nodeShape(self):
        #Override Me!
        self.polyShape = [[0,0],[70,0],[74,8],[70,16],[0,16]]
        
        #FLAW: add this to appPrefs/appSettings somehow
        self.color1 = QtGui.QColor(238,238,238)
        self.color2 = QtGui.QColor(122,122,122)

class TimelineNode(WidgetLinkedNode):
    def __init__(self, parent):
        super(TimelineNode, self).__init__(parent)
        self.setTitleBarWidget(self['nodeName'])
    def setInput(self, index, object):
        return
    def setCurrentInputIndex(self, index):
        return
    def getInput(self, *args):
        if len(args) < 1:
            return self.parent.getTopNodeAtFrame(self.getCurrentInputIndex(), notNode = self)
        else:
            return self.parent.getTopNodeAtFrame(args[0], notNode = self)
    def getInputs(self):
        returnList = []
        for frame in range(self['width'].getValue()):
            frame += self['firstFrame'].getValue()
            returnList.appened(self.parent.getTopNodeAtFrame(frame, notNode = self))
        return returnList
    def getCurrentInputIndex(self):
        return self.parent.getCurrentFrameNumber()
    def nodeShape(self):
        self.polyShape = [[0,0],[100,0],[100,self.parent.YPixelsPerUnit],[0,self.parent.YPixelsPerUnit]]
        self.color1 = QtGui.QColor(238,238,238)
        self.color2 = QtGui.QColor(122,122,122)
    
    def setWidth(self, *args):
        if len(args) is 1:
            value = args[0]
        else:   
            value = self['lastFrame'].getValue()-self['firstFrame'].getValue()+1
        self['width'].setValue(value)
        
        self.polyShape = [[0,0],[value,0],[value,self.parent.YPixelsPerUnit],[0,self.parent.YPixelsPerUnit]]
        self.mapNodeShape()

class ImageNode(GraphNode):
    def __init__(self, parent):
        super(ImageNode, self).__init__(parent)
        #self.extension()
        self.frameCache = None
        self.frameCacheFrame = None
        
    def getImage(self, *args):
        return self.generateImage(*args)
        
    def generateImage(self, *args):
        #Override this method
        if self.getInput() is None:
            return AppCore.generateBlack()
        else:
            return self.getInput().getImage(*args)

class AudioNode(GraphNode):
    def __init__(self, parent):
        super(AudioNode, self).__init__(parent)

class GeometryNode(GraphNode):
    def __init__(self, parent):
        super(GeometryNode, self).__init__(parent)

class ArrayDataNode(GraphNode):
    def __init__(self, parent):
        super(ArrayDataNode, self).__init__(parent)
