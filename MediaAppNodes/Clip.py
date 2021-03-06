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
import os

from Qt import QtGui, QtCore
#import imageio

import AppCore
import DataStructures
from MediaAppKnobs import *
from NodeConstructor import *
#import NodeConstructor
#print(dir(NodeConstructor))

class Clip(ImageNode, AudioNode):
    def __init__(self, parent):
        super(Clip, self).__init__(parent)
        self['ClassName'] = 'Clip'
        self.setName(AppCore.getIncrementedName('Clip'))
        ################################
        
        #FLAW: move parent kw setting to KnobConstructor
        defaultPath = '*NWSTORAGE/'
        self['file'] = FileKnob(defaultPath, parent = self)
        
        self['before'] = ComboKnob(['hold', 'loop', 'bounce', 'black'])
        self['firstFrame'] = IntKnob(1)
        self['lastFrame'] = IntKnob(100)
        self['after'] = ComboKnob(['hold', 'loop', 'bounce', 'black'])
        self['firstFrame'].newline = False
        self['lastFrame'].newline = False
        self['after'].newline = False
        
        self['startAt'] = IntKnob(0)

        self['Notes'] = TextKnob('')
        
        self.attachKnobs()
        
        self.leftToolBar = QtGui.QToolBar('Left Tool Bar')
        self.leftToolBar.setMovable(False)
        
        #self.ViewerToolbars = [[QtCore.Qt.LeftToolBarArea, self.leftToolBar]]
        
    def generateImage(self, *args):
        if len(args) is 1:
            imagePath = self['file'].getEvaluatedPath(args[0])
        else:
            imagePath = self['file'].getEvaluatedPath()
        
        if os.path.isfile(imagePath):
            #print('#######imagePath', imagePath, end = "")
            #image = imageio.imread(imagePath)
            #print(image)
            #image = imageio.core.util.image_as_uint8(image)
            
            
            #imageString = image.tobytes()
            imageString = image.tostring()
            
            #TEST: I don't think swapaxes will add any overhead, take it out if it does
            image = image.swapaxes(0, 1)
            width, height, channels = image.shape
            #height, width, channels = image.shape
            
            bytesPerLine = channels * width
            if channels == 4:
                #QImage = DataStructures.QImage(imageString, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32).rgbSwapped()
                QImage = DataStructures.QImage(imageString, width, height, bytesPerLine, QtGui.QImage.Format_ARGB32)
            elif channels == 3:
                QImage = DataStructures.QImage(imageString, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            
            return QImage
        else:
            #Generate Black QImage
            width = AppCore.AppAttributes['ResolutionWidth']
            height = AppCore.AppAttributes['ResolutionHeight']
            image = DataStructures.QImage(width, height, QtGui.QImage.Format_ARGB32)
            return image
    
    
    ###Pointer Functions###
    def getCurrentFrameNumber(self):
        return self.parent.getCurrentFrameNumber()
        
        
        