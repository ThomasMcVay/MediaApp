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

import AppCore
from MediaAppKnobs import *
from NodeConstructor import *

class TimelineNode(ImageNode, AudioNode, WidgetLinkedNode):
    def __init__(self, parent):
        super(TimelineNode, self).__init__(parent)
        self['ClassName'] = 'TimelineNode'
        self.setName(AppCore.getIncrementedName('TimelineNode'))
        ################################
        
        #TODO: create ImageMath package, tie these to some math
        self['zti'] = IntKnob(0)
        self['cti'] = IntKnob(0)

        self.attachKnobs()
        
    def nodeShape(self):
        self.polyShape = [[0,0],[100,0],[100,24],[0,24]]
        self.color1 = QtGui.QColor(180,50,238)
        self.color2 = QtGui.QColor(122,122,122)
        
    ###Pointer Functions###
    def moveCurrentFrameNumber(self, value, playback = False):
        self.getLinkedWidget().moveCurrentFrameNumber(value, playback = playback)
    def repaint(self):
        self.getLinkedWidget().repaint()
    def getImage(self):
        return self.getLinkedWidget().getImage()
    def getCache(self):
        return self.getLinkedWidget().getCache()
    def cacheFrames(self):
        self.getLinkedWidget().cacheFrames()
    #######################
