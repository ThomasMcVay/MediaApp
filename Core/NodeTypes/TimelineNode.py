#===============================================================================
# @Author: Thomas McVay
# @Version: 0.1
# @LastModified: 130511
# @Description: 
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
#    See MediaApp_LGPL.txt in the root directory of this library for copy of
#    GNU Lesser General Public License and other license details.
#===============================================================================

from NodeConstructor import *
from KnobTypes import *

class TimelineNode(ImageNode, AudioNode):
    def __init__(self, CorePointer):
        global Core
        Core = CorePointer
        super(TimelineNode, self).__init__(CorePointer)
        self['ClassName'] = 'TimelineNode'
        self.setName(Core.getIncrementedName('TimelineNode'))
        ################################
        
        self.TimelineWidget = None
        
        #TODO: create ImageMath package, tie these to some math
        self['zti'] = IntKnob(0)
        self['cti'] = IntKnob(0)

        self.attachKnobs()
        
    
    def nodeShape(self):
        self.polyShape = [[0,0],[100,0],[100,24],[0,24]]
        self.color1 = QtGui.QColor(180,50,238)
        self.color2 = QtGui.QColor(122,122,122)

    def setTimelineWidget(self, widget):
        self.TimelineWidget = widget
    
    
    def getImage(self):
        inputNode = self.TimelineWidget.getTopNodeForCurrentFrame()
        self.frameCache = self.generateImage(inputNode = inputNode)
        return self.frameCache