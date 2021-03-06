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

import AppCore
from .KnobConstructor import Knob
from . import KnobElements
from .FloatKnob import FloatKnob

import MediaAppIcons

class ColorKnob(Knob):
    def __init__(self, *args, **kwargs):
        if 'name' in kwargs.keys():
            name = kwargs['name']
        else:
            name = 'ColorKnob'
        super(ColorKnob, self).__init__()
        
        self.shown = True
        self.newline = True
        
        self.name = KnobElements.KnobLabel()
        self.name.setText(name)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        self.knobLayout.addWidget(self.name)
        
        self.button = QtWidgets.QPushButton()
        self.knobLayout.addWidget(self.button)

        if len(args) > 0:
            self.QColor = args[0]
        else:
            self.QColor = QtGui.QColor(AppCore.AppPrefs['ColorKnob-DefaultColor'])
        
        self.setIcon()
        self.button.clicked.connect(self.showDialog)
        #self.QColor = QtGui.QColor(QtGui.QColor(255,255,255))
        
        def none(): pass
        self.changed = none

    def setValue(self, value):
        if isinstance(value, QtGui.QColor):
            self.QColor = value
        else:
            self.QColor.setNamedColor(value)
        self.setIcon()
        self.changed()
        self.update()
    def getValue(self):
        return self.QColor
    def showDialog(self):
        newColor = QtWidgets.QColorDialog.getColor(self.QColor)
        if newColor.isValid():
            self.QColor = newColor
        self.setIcon()
        self.changed()
        self.update()
        return self.QColor
    def setIcon(self):
        self.button.setIcon(MediaAppIcons.IconFromColor(self.QColor))
    def sizeHint(self):
        return QtCore.QSize(64,64)
    