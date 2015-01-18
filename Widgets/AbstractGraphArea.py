#===============================================================================
# @Author: Thomas McVay
# @ModuleDescription: 
# @License:
#    MediaApp Library - Python Package framework for developing robust Media 
#                       Applications with PySide Library
#    Copyright (C) 2013 Thomas McVay
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
from time import time
from copy import copy

from PySide import QtGui, QtCore

import AppCore
from DataStructures import KeyboardDict

#Provides unordered comparisons for a list, In this case keyboard keys,
#so that it does not matter what order you pressed the keys in
class keyList(list):
    def __init__(self, *args):
        super(keyList, self).__init__(*args)
    def __eq__(self, other):
        if not isinstance(other, list):
            return NotImplemented
                
        for item in other:
            if item not in self:
                return False
        for item in self:
            if item not in other:
                return False
        return True

#Provides a list with a currently selected item, .currentMode
class modeList(list):
    def __init__(self, *args):
        super(modeList, self).__init__(*args)
        self.currentMode = 0
        
        self.frameCache = None
        self.frameCacheFrame = None
    def getCurrentMode(self):
        return self[self.currentMode]
    def getCurrentModeIndex(self):
        return self.currentMode
    def setCurrentMode(self, arg):
        if type(arg) is int:
            self.currentMode = i
        elif type(arg) is str:
            for i, mode in enumerate(self):
                if mode == arg:
                    self.currentMode = i

class AbstractGraphArea(QtGui.QWidget):
    ###Initialize Class###
    def __init__(self):
        super(AbstractGraphArea, self).__init__()
        self.className = self.__class__.__name__
        
        #QWidget Settings
        self.setFocusPolicy(AppCore.AppSettings['FocusPolicy'])
        self.setMinimumSize(0, 0)
        self.setGeometry(0, 0, 0, 0)
        
        #Initialize Values
        self.modes = modeList(['None','zoomMode','panMode'])
        self.pressedButtons = keyList()
        self.inputInterval = 0
        
        self.addToolBarLayouts()
        self.getDictSettings()
        
    def addToolBarLayouts(self):
        self.VBox = QtGui.QVBoxLayout()
        self.HBox = QtGui.QHBoxLayout()
        self.topToolBars = QtGui.QVBoxLayout()
        self.bottomToolBars = QtGui.QVBoxLayout()
        self.leftToolBars = QtGui.QHBoxLayout()
        self.rightToolBars = QtGui.QHBoxLayout()
        
        self.VBox.setContentsMargins(0, 0, 0, 0)
        self.HBox.setContentsMargins(0, 0, 0, 0)
        self.topToolBars.setContentsMargins(0, 0, 0, 0)
        self.bottomToolBars.setContentsMargins(0, 0, 0, 0)
        self.leftToolBars.setContentsMargins(0, 0, 0, 0)
        self.rightToolBars.setContentsMargins(0, 0, 0, 0)
        
        self.VBox.setSpacing(0)
        self.HBox.setSpacing(0)
        self.topToolBars.setSpacing(0)
        self.bottomToolBars.setSpacing(0)
        self.leftToolBars.setSpacing(0)
        self.rightToolBars.setSpacing(0)
        
        self.setLayout(self.VBox)
        
        ###Widget ToolBarLayouts###
        self.VBox.addLayout(self.topToolBars)
        
        self.VBox.addLayout(self.HBox)
        self.HBox.addLayout(self.leftToolBars)
        
        spacer = QtGui.QWidget()
        spacer.setMouseTracking(True)
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.HBox.addWidget(spacer)
        
        self.HBox.addLayout(self.rightToolBars)

        self.VBox.addLayout(self.bottomToolBars)
        ####################
        
    def getDictSettings(self):
        self.ZoomXYJoined = AppCore.AppSettings[self.className+'-ZoomXYJoined']
        self.XPixelsPerUnit = AppCore.AppSettings[self.className+'-XPixelsPerUnit']
        self.YPixelsPerUnit = AppCore.AppSettings[self.className+'-YPixelsPerUnit']
        self.upperXZoomLimit = AppCore.AppSettings[self.className+'-upperXZoomLimit']
        self.upperYZoomLimit = AppCore.AppSettings[self.className+'-upperYZoomLimit']
        self.lowerXZoomLimit = AppCore.AppSettings[self.className+'-lowerXZoomLimit']
        self.lowerYZoomLimit = AppCore.AppSettings[self.className+'-lowerYZoomLimit']
        self.zoomSensitivity = 100.0/AppCore.AppSettings[self.className+'-zoomSensitivity']

        self.curGraphX = AppCore.AppAttributes[self.className+'-GraphX']
        self.curGraphY = AppCore.AppAttributes[self.className+'-GraphY']
        self.curGraphXS = AppCore.AppAttributes[self.className+'-GraphXS']
        self.curGraphYS = AppCore.AppAttributes[self.className+'-GraphYS']
    ######################
    
    ###Input Events###
    def keyPressEvent(self, event):
        if event.key() in KeyboardDict.keys():
            key = KeyboardDict[event.key()]
        else:
            print 'key '+str(event.key())+' pressed.'
            return
        self.setButton(key)
        self.subclassPressEvents(event)
    def keyReleaseEvent(self, event):    
        if event.key() in KeyboardDict.keys():
            key = KeyboardDict[event.key()]
        else:
            print 'key '+str(event.key())+' released.'
            return
        self.clearButton(key)
    def mousePressEvent(self, event):
        self.startMouseX = event.pos().x()
        self.startMouseY = event.pos().y()
        self.startModeX, self.startModeY = self.graphTrans.inverted()[0].map(self.startMouseX, self.startMouseY)
        
        button = str(event.button()).rsplit('.', 1)[-1]
        self.setButton(button)
        self.subclassPressEvents(event)
    def mouseReleaseEvent(self, event):
        self.endMouseX = event.pos().x()
        self.endMouseY = event.pos().y()
        self.endModeX, self.endModeY = self.graphTrans.inverted()[0].map(self.endMouseX, self.endMouseY)
        
        button = str(event.button()).rsplit('.', 1)[-1]
        self.clearButton(button)
    def subclassPressEvents(self, event): #Override me!
        pass
    ##################
    
    ###Button Handling###
    def setButton(self, button):
        self.pressedButtons.append(button)
        self.setMode()
        self.initialValues()
    def clearButton(self, button):
        if button in self.pressedButtons:
            self.pressedButtons.remove(button)
            
        #self.modes.setCurrentMode('None')
        self.setMode()
        self.initialValues()
        self.releaseTime = time()
        self.inputInterval = AppCore.AppPrefs['AbstractGraphArea-inputInterval']
    def setMode(self):
        if self.inputInterval > 0:
            if time() > self.releaseTime+self.inputInterval:
                self.inputInterval = 0
            else:
                return
        
        if self.pressedButtons == AppCore.AppPrefs['AbstractGraphArea-Shortcuts-Zoom']:
            self.modes.setCurrentMode('zoomMode')
        elif self.pressedButtons == AppCore.AppPrefs['AbstractGraphArea-Shortcuts-Pan']:
            self.modes.setCurrentMode('panMode')
        else:
            self.modes.setCurrentMode('None')
            self.subclassModes()
        self.update()
    def subclassModes(self): #Override me!
        pass
    def getCurrentMode(self):
        return self.modes.getCurrentMode()
    #####################
    
    ###InitalValues###
    def initialValues(self):
        AppCore.AppAttributes[self.className+'-GraphX'] = self.curGraphX
        AppCore.AppAttributes[self.className+'-GraphY'] = self.curGraphY
        AppCore.AppAttributes[self.className+'-GraphXS'] = self.curGraphXS
        AppCore.AppAttributes[self.className+'-GraphYS'] = self.curGraphYS
        self.endModeX = self.startModeX
        self.endModeY = self.startModeY
        
        self.subclassInitialValues()
    def subclassInitialValues(self): #Override me!
        pass
    ##################

    ###MoveEvents###
    def mouseMoveEvent(self, event):
        self.progressValues(event)
        self.ModeEvents(event)
        self.update() #Redraw  
        self.repaint()
    ################
    
    ###ProgressValues###
    def progressValues(self, event):
        self.curMouseX = event.pos().x()
        self.curMouseY = event.pos().y()
        self.curModeX, self.curModeY = self.graphTrans.inverted()[0].map(self.curMouseX, self.curMouseY)
        self.subclassProgressValues(event)
    def subclassProgressValues(self, event): #Override me!
        pass
    ####################
    
    ###ModeEvents###
    def ModeEvents(self, event):
        if self.getCurrentMode() == 'zoomMode':
            self.zoomEvent()
        elif self.getCurrentMode() == 'panMode':
            self.panEvent()
        else:
            self.subclassModeEvents(event)
    def subclassModeEvents(self, event): #Override me!
        pass
        
    def panEvent(self):
        self.curGraphX = AppCore.AppAttributes[self.className+'-GraphX']+(self.curMouseX-self.startMouseX)
        self.curGraphY = AppCore.AppAttributes[self.className+'-GraphY']+(self.curMouseY-self.startMouseY)
    def zoomEvent(self):
        posDeltaX = (self.curMouseX-self.startMouseX)
        posDeltaY = (self.curMouseY-self.startMouseY)
        scaleDeltaX = posDeltaX/self.zoomSensitivity
        scaleDeltaY = posDeltaY/self.zoomSensitivity*-1
        
        if self.ZoomXYJoined == True:
            self.curGraphXS = AppCore.AppAttributes[self.className+'-GraphXS']+(scaleDeltaX+scaleDeltaY)/2
            self.curGraphYS = AppCore.AppAttributes[self.className+'-GraphYS']+(scaleDeltaX+scaleDeltaY)/2
        else:
            self.curGraphXS = AppCore.AppAttributes[self.className+'-GraphXS']+scaleDeltaX
            self.curGraphYS = AppCore.AppAttributes[self.className+'-GraphYS']+scaleDeltaY
        
        difScaleX = self.curGraphXS-AppCore.AppAttributes[self.className+'-GraphXS']
        difScaleY = self.curGraphYS-AppCore.AppAttributes[self.className+'-GraphYS']
        
        if self.curGraphXS > self.upperXZoomLimit:
            self.curGraphXS = self.upperXZoomLimit
        elif self.curGraphXS < self.lowerXZoomLimit:
            self.curGraphXS = self.lowerXZoomLimit
        else:
            self.curGraphX = AppCore.AppAttributes[self.className+'-GraphX']-(self.startModeX*difScaleX)
            
        if self.curGraphYS > self.upperYZoomLimit:
            self.curGraphYS = self.upperYZoomLimit  
        elif self.curGraphYS < self.lowerYZoomLimit:
            self.curGraphYS = self.lowerYZoomLimit
        else:
            self.curGraphY = AppCore.AppAttributes[self.className+'-GraphY']-(self.startModeY*difScaleY)   
    #################
    
    ###PaintEvents###
    def paintEvent(self, pEvent):
        painter = QtGui.QPainter(self)
        
        #DrawBG
        self.widgetSize = self.size()
        painter.setBrush(AppCore.AppPrefs[self.className+'-bgColor'])
        painter.drawRect(0, 0, self.widgetSize.width(), self.widgetSize.height())
        
        #SetTransform
        self.graphTrans = QtGui.QTransform()
        self.graphTrans.translate(self.curGraphX, self.curGraphY)
        self.graphTrans.scale(self.curGraphXS+1, self.curGraphYS+1)
        painter.setTransform(self.graphTrans)
        
        self.subclassPaintEvent(pEvent, painter)
    def subclassPaintEvent(self, pEvent, painter): #Override me!
        painter.end()
    #################

    ###Other Functions###
    def addToolBar(self, ToolBarArea, ToolBar):
        if ToolBarArea == QtCore.Qt.TopToolBarArea:
            self.topToolBars.addWidget(ToolBar)
        if ToolBarArea == QtCore.Qt.BottomToolBarArea:
            self.bottomToolBars.addWidget(ToolBar)
        if ToolBarArea == QtCore.Qt.LeftToolBarArea:
            ToolBar.setOrientation(QtCore.Qt.Vertical)
            self.leftToolBars.addWidget(ToolBar)
        if ToolBarArea == QtCore.Qt.RightToolBarArea:
            ToolBar.setOrientation(QtCore.Qt.Vertical)
            self.rightToolBars.addWidget(ToolBar)
    #####################
    pass