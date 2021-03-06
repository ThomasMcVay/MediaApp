#===============================================================================
# @Author: Madison Aster
# @ModuleDescription: 
# @License:
#    MediaApp Library - Python Package framework for developing robust Media 
#                       Applications with PySide Library
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

from Qt import QtGui, QtCore

class QImage(QtGui.QImage):
    def __init__(self, *args, **kwargs):
        super(QImage, self).__init__(*args, **kwargs)
        
        #WORKAROUND: set self.ImageData here so that the object takes ownership of the data.
        #           else wise the data will get destroyed after the function that initialized this
        #           object completes.
        self.ImageData = args[0]
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

