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
from time import time, sleep
import copy

from PySide import QtGui, QtCore

import AppCore
import MediaAppIcons
import MediaAppKnobs
import DataStructures
from NodeLinkedWidget import *

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
        
        
class Viewer(QtGui.QWidget):
    def __init__(self):
        super(Viewer, self).__init__()
        self.className = self.__class__.__name__
        
        self.setFocusPolicy(AppCore.AppSettings['FocusPolicy'])
        self.setMouseTracking(True)
        self.setMinimumSize(0, 0)
        self.setGeometry(0, 0, 0, 0)
        
        #Initialize Values
        self.modes = modeList(['None','zoomMode','panMode','marqMode', 'extraMode'])
        self.middleClick = False
        self.leftClick = False
        self.rightClick = False
        self.shiftKey = False
        self.ctrlKey = False

        #Initialize User Values#
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
        
        self.frameCache = AppCore.generateBlack()
    
    def keyPressEvent(self, event):
        #FLAW: find a better place to put some of these, this should be a fairly short function
        if event.key() == 16777234: #Left 
            self.parent().getInput().moveCurrentFrame(-1)
            self.parent().updateFrame()
            self.parent().getInput().repaint()
        if event.key() == 16777236: #Right
            self.parent().getInput().moveCurrentFrame(1)
            self.parent().updateFrame()
            self.parent().getInput().repaint()
        if event.key() == 67: #C
            self.parent().cacheFrames()
            self.parent().updateFrame()
        if event.key() == 32: #Space
            self.playForward()
            
        key = str(event.key())
        self.changeButton(key, True)

    def keyReleaseEvent(self, event):    
        key = str(event.key())
        self.changeButton(key, False)
        
    def setNode(self, node):
        self.node = node
    def mousePressEvent(self, event):
        self.startMouseX = event.pos().x()
        self.startMouseY = event.pos().y()
        self.startModeX, self.startModeY = self.graphTrans.inverted()[0].map(self.startMouseX, self.startMouseY)
            
        button = str(event.button())
        
        self.changeButton(button, True)
    def mouseReleaseEvent(self, event):
        self.endMouseX = event.pos().x()
        self.endMouseY = event.pos().y()
        self.endModeX, self.endModeY = self.graphTrans.inverted()[0].map(self.endMouseX, self.endMouseY)
        
        button = str(event.button())
        
        self.changeButton(button, False)
    def changeButton(self, button, Value):
        if button.rsplit('.', 1)[-1] == 'MiddleButton' or button.rsplit('.', 1)[-1] == 'MidButton':
            self.middleClick = Value
        elif button.rsplit('.', 1)[-1] == 'LeftButton':
            self.leftClick = Value
        elif button.rsplit('.', 1)[-1] == 'RightButton':
            self.rightClick = Value
        elif button == '16777248': #Shift
            self.shiftKey = Value
        elif button == '16777249': #Ctrl
            self.ctrlKey = Value
        else:
            print 'button', button, Value
            return
        
        self.setMode()
        self.grabValues()
        self.update()
    def setMode(self):
        #Mouse and Touch modes
        if self.middleClick == True and self.leftClick == True:
            self.modes.setCurrentMode('zoomMode')
        elif self.middleClick == True and self.leftClick == False:
            self.modes.setCurrentMode('panMode')
        
        #Modifier Modes
        elif hasattr(AppCore.getActiveNode(), 'ViewerEventExtra'):
            self.modes.setCurrentMode('extraMode')
        elif self.shiftKey == True and self.leftClick == True:
            self.modes.setCurrentMode('marqMode')
        
        #Finally
        else:
            self.modes.setCurrentMode('None')
    def getCurrentMode(self):
        return self.modes.getCurrentMode()
    def grabValues(self):
        AppCore.AppAttributes[self.className+'-GraphX'] = self.curGraphX
        AppCore.AppAttributes[self.className+'-GraphY'] = self.curGraphY
        AppCore.AppAttributes[self.className+'-GraphXS'] = self.curGraphXS
        AppCore.AppAttributes[self.className+'-GraphYS'] = self.curGraphYS
        self.endModeX = self.startModeX
        self.endModeY = self.startModeY
        if hasattr(AppCore.getActiveNode(), 'grabViewerValues'):
            AppCore.getActiveNode().grabViewerValues(self)
    def mouseMoveEvent(self, event):
        self.curMouseX = event.pos().x()
        self.curMouseY = event.pos().y()
        self.curModeX, self.curModeY = self.graphTrans.inverted()[0].map(self.curMouseX, self.curMouseY)
        
        #Mouse and Touch Modes
        if self.getCurrentMode() == 'zoomMode':
            self.zoomEvent()
        elif self.getCurrentMode() == 'panMode':
            self.panEvent()
        
        #Modifier Modes
        elif self.getCurrentMode() == 'extraMode':
            self.extraEvent()
        elif self.getCurrentMode() == 'marqMode':
            self.marqEvent()
           
        self.update() #Redraw      
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
    def marqEvent(self):
        self.endModeX = self.curModeX
        self.endModeY = self.curModeY
        self.marqContains()
    def extraEvent(self):
        self.endModeX = self.curModeX
        self.endModeY = self.curModeY
        AppCore.getActiveNode().ViewerEventExtra(self)
    def marqContains(self):
        #Sample Pixels here
        pass
        
    
    def playForward(self):
        frameperiod=1.0/AppCore.AppAttributes['FPS']
        now = time()
        nextframe = now
        cache = self.parent().getCache()
        print cache
        for image in cache:
            while now < nextframe:
                sleep(nextframe-now)
                now = time()
                
            self.frameCache = image
            #Maybe some overhead here
            cache.moveCurrentFrame(1, playback = True)
            self.repaint()
            
            nextframe += frameperiod
            
    def cacheFrame(self, image):
        self.frameCache = image
    
    def paintEvent(self, pEvent):
        painter = QtGui.QPainter(self)
        #ADD quickpaint here?
        
        #DrawBG
        self.widgetSize = self.size()
        painter.setBrush(AppCore.AppPrefs[self.className+'-bgColor'])
        painter.drawRect(0, 0, self.widgetSize.width(), self.widgetSize.height())
        
        #SetTransform
        self.graphTrans = QtGui.QTransform()
        self.graphTrans.translate(self.curGraphX, self.curGraphY)
        self.graphTrans.scale(self.curGraphXS+1, self.curGraphYS+1)
        painter.setTransform(self.graphTrans)
        
        
        #DrawImage
        
        #if self.frameCache is None or self.frameCacheFrame != AppCore.getCurrentFrame():
        #    self.frameCache =  self.node.getImage()
        #    self.frameCacheFrame = AppCore.getCurrentFrame()
        
        #self.frameCache =  self.node.getImage()
        painter.drawImage(QtCore.QRect(0,0,self.frameCache.width(),self.frameCache.height()), self.frameCache)
        
        #DrawResolutionBox
        painter.setBrush(AppCore.AppPrefs[self.className+'-ResBoxColor'])
        pen = AppCore.AppPrefs[self.className+'-ResBoxPen']
        pen.setCosmetic(True)
        painter.setPen(pen)
        #BUG: Diagonal line gets drawn here when zoomed in just the right way
        painter.drawRect(QtCore.QRect(-1,-1,self.frameCache.width()+2,self.frameCache.height()+2))
        
        #DrawBoundingBox
        
        #Draw ActiveNode Overlays
        if hasattr(AppCore.getActiveNode(), 'ViewerOverlays'):
            AppCore.getActiveNode().ViewerOverlays(self, painter)
            
        #DrawMarq
        if self.modes.getCurrentMode() == 'marqMode':
            marqX = [self.startModeX, self.endModeX]
            marqY = [self.startModeY, self.endModeY]
            marqX.sort()
            marqY.sort()
            painter.setBrush(AppCore.AppPrefs[self.className+'-marqBoxColor'])
            pen = AppCore.AppPrefs[self.className+'-marqOutlinePen']
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawRect(QtCore.QRectF(marqX[0], marqY[0], marqX[1]-marqX[0], marqY[1]-marqY[0]))
        
        #Finished
        painter.end()
            
class ViewerWidget(NodeLinkedWidget, QtGui.QMainWindow):
    def __init__(self):
        super(ViewerWidget, self).__init__()
        self.setDockOptions(False)
        self.setFocusPolicy(AppCore.AppSettings['FocusPolicy'])

        self.setLinkedNode(AppCore.NodeGraph.createNode('ViewerNode'))
        self.TimeIndicator = DataStructures.TimeCache()
        
        self.widget = Viewer()
        self.setCentralWidget(self.widget)
        
        self.AccessoryToolBars = []
        self.createViewerToolbars()
        
        
    def createViewerToolbars(self):
        self.topToolBar = QtGui.QToolBar('Top Tool Bar')
        self.leftToolBar = QtGui.QToolBar('Left Tool Bar')
        self.rightToolBar = QtGui.QToolBar('Right Tool Bar')
        self.bottomToolBar = QtGui.QToolBar('Bottom Tool Bar')
        
        self.topToolBar.setMovable(False)
        self.leftToolBar.setMovable(False)
        self.rightToolBar.setMovable(False)
        self.bottomToolBar.setMovable(False)
        
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.topToolBar)
        #self.addToolBar(QtCore.Qt.LeftToolBarArea, self.leftToolBar)
        #self.addToolBar(QtCore.Qt.RightToolBarArea, self.rightToolBar)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.bottomToolBar)
        
        
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.topToolBar.addWidget(spacer)
        
        self.inputSelectorA = MediaAppKnobs.ComboKnob([])
        self.topToolBar.addWidget(self.inputSelectorA)
        
        self.inputCombiner = MediaAppKnobs.ComboKnob(['A Only','B Only','Wipe','Blend'])
        self.topToolBar.addWidget(self.inputCombiner)
        
        self.inputSelectorB = MediaAppKnobs.ComboKnob([])
        self.topToolBar.addWidget(self.inputSelectorB)
        
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.topToolBar.addWidget(spacer)
        
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.bottomToolBar.addWidget(spacer)

        RNext = QtGui.QAction(MediaAppIcons.RNext(), 'RNext', self)
        RNext.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(RNext)
        
        RPlay = QtGui.QAction(MediaAppIcons.RPlay(), 'RPlay', self)
        RPlay.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(RPlay)
        
        RAdvance = QtGui.QAction(MediaAppIcons.RAdvance(), 'RAdvance', self)
        RAdvance.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(RAdvance)
        
        Stop = QtGui.QAction(MediaAppIcons.Stop(), 'Stop', self)
        Stop.triggered.connect(self.updateFrame)
        self.bottomToolBar.addAction(Stop)
        
        Advance = QtGui.QAction(MediaAppIcons.Advance(), 'Advance', self)
        Advance.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(Advance)
        
        Play = QtGui.QAction(MediaAppIcons.Play(), 'Play', self)
        Play.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(Play)
        
        Next = QtGui.QAction(MediaAppIcons.Next(), 'Next', self)
        Next.triggered.connect(self.widget.playForward)
        self.bottomToolBar.addAction(Next)
        
        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.bottomToolBar.addWidget(spacer)
    
    def getInput(self):
        #FLAW: need to figure out how to play back from 2 caches at once in opengl later
        if self.inputCombiner.getValue() is 'B Only':
            return self.getLinkedNode().getInput(self.inputSelectorB.currentIndex())
        else:
            #For now just return input A, because there's no current method for connecting to two caches at once.
            return self.getLinkedNode().getInput(self.inputSelectorA.currentIndex())
        
    def updateFrame(self):
        inputA = self.getLinkedNode().getInput(self.inputSelectorA.currentIndex())
        inputB = self.getLinkedNode().getInput(self.inputSelectorB.currentIndex())
        
        #TODO 'implement a provided timeline in the viewer'
        if str(self.inputCombiner.getValue()) == 'A Only':
            self.widget.cacheFrame(inputA.getImage())
        elif str(self.inputCombiner.getValue()) == 'B Only':
            self.widget.cacheFrame(inputB.getImage())
        else:
            imageA = inputA.getImage()
            imageB = inputB.getImage()
        if str(self.inputCombiner.getValue()) is 'Blend':    
            self.widget.cacheFrame(self.blendImage(imageA, imageB))
        elif str(self.inputCombiner.getValue()) is 'Wipe':
            self.widget.cacheFrame(self.wipeImage(imageA, imageB))
        
        
        #if AppCore.getCurrentFrame() in AppCore.data['frameCache']:
        #    self.frameCache = AppCore.data['frameCache'][0]
        #else:
        #    self.frameCache = AppCore.generateBlack()
        
    def dumpAccessoryToolbars(self):
        for toolbar in self.AccessoryToolBars:
            self.removeToolBar(toolbar)
        self.AccessoryToolBars = []
    def addAccessoryToolbars(self, toolbars):
        for toolbar in toolbars:
            self.AccessoryToolBars.append(toolbar[1])
            self.addToolBar(toolbar[0], self.AccessoryToolBars[-1])
            self.AccessoryToolBars[-1].show()
            
    ###Pointer Functions###
    def getCache(self):
        input = self.getInput()
        if hasattr(input, 'getCache'):
            return self.getInput().getCache()
        else:
            return self.TimeIndicator
    def cacheFrames(self):
        input = self.getInput()
        if hasattr(input, 'cacheFrames'):
            self.getInput().cacheFrames()
        else:
            firstFrame, lastFrame = self.getInputRange()
            self.TimeIndicator.cacheFrames(self.generateFrames(firstFrame, lastFrame), firstFrame = firstFrame)
    
    def generateFrames(self, firstFrame, lastFrame):
        print 'Viewer generating '+str(lastFrame-firstFrame)+' frames as QImages',
        input = self.getInput()
        for frame in range(firstFrame, lastFrame):
            yield input.getImage(frame)