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
from MediaAppKnobs import *

class PrefsWindow(QtWidgets.QWidget):
    def __init__(self):
        super(PrefsWindow, self).__init__()
        AppCore.RegisterObject(self)
        
        self.panelLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.panelLayout)
        
        self.ScrollWidget = QtWidgets.QScrollArea()
        self.EnumeratedPrefs = EnumeratedPrefs()
        self.ScrollWidget.setWidget(self.EnumeratedPrefs)
        self.panelLayout.addWidget(self.ScrollWidget)
        
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        
        saveButton = QtWidgets.QPushButton('SavePrefs')
        saveButton.clicked.connect(self.SavePrefs)
        defaultsButton = QtWidgets.QPushButton('RestoreDefaults')
        defaultsButton.clicked.connect(self.RestoreDefaults)
        closeButton = QtWidgets.QPushButton('Close')
        closeButton.clicked.connect(self.close)
        
        self.buttonsLayout.addWidget(saveButton)
        self.buttonsLayout.addWidget(defaultsButton)
        self.buttonsLayout.addWidget(closeButton)
        
        self.panelLayout.addLayout(self.buttonsLayout)
    def SavePrefs(self):
        pass
    def RestoreDefaults(self):
        pass
class EnumeratedPrefs(QtWidgets.QWidget):
    def __init__(self):
        super(EnumeratedPrefs, self).__init__()
        self.panelLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.panelLayout)
        
        self.knobs = {}
        
        for key in AppCore.AppPrefs:
            if type(AppCore.AppPrefs[key]) is str:
                self[key] = StrKnob(AppCore.AppPrefs[key])
            elif type(AppCore.AppPrefs[key]) is int:
                self[key] = IntKnob(AppCore.AppPrefs[key])
            elif type(AppCore.AppPrefs[key]) is float:
                self[key] = FloatKnob(AppCore.AppPrefs[key])
            elif type(AppCore.AppPrefs[key]) is bool:
                self[key] = BoolKnob(AppCore.AppPrefs[key])
            elif type(AppCore.AppPrefs[key]).__name__ == 'QColor':
                self[key] = ColorKnob(AppCore.AppPrefs[key], name = key)
            else:
                #TODO: QPen, QBrush, QFont
                #print type(AppCore.AppPrefs[key]).__name__ 
                continue
            print('adding pref', key, type(self[key]), self[key])
            self[key].name.labelSize = 250
            self.panelLayout.addWidget(self[key])
    def __delitem__(self, key):
        for i, knob in enumerate(self.knobs):
            if knob.name.text() == key:
                del self.knobs[i]
    def __setitem__(self, key, value):
        if 'knob' in type(value).__name__.lower():
            self.knobs[key] = value
        else:
            self[key].setValue(value)
    def __getitem__(self, key):
        if key in self.knobs.keys():
            return self.knobs[key]
        else:
            return self[key]
            
    def sizeHint(self):
        YHint = 0
        for knob in self.knobs.values():
            YHint += knob.sizeHint().height()+20
        return QtCore.QSize(800,YHint)
        
    #def sizeHint(self):
    #    return QtCore.QSize(400,1000)    
        
PrefsWindow()
        
        
        
        
        
        
        
        
        
        
        