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

from Qt import QtGui, QtCore

import AppCore

class NodeOwningObject(object):
    def __init__(self, objectName='', accessibleName=''):
        super(NodeOwningObject, self).__init__()
        
        #TEST: see if using this duplicate dictionary is actually faster than AppCore.getChildrenOf(self)
        self.Nodes = {}
        self.preferredNodeClass = 'GraphNode'
    def __getitem__(self, key):
        return self.Nodes[key]
    def createNode(self, nodeType):
        node = AppCore.createNode(nodeType, parent = self, baseClass = self.preferredNodeClass)
        self.Nodes[node.name()] = node
        self.nodeCreated()
        
        if hasattr(self, 'update'):
            self.update()
        #if hasattr(self, 'repaint'):
        #    self.repaint()
        return node
    def allNodes(self):
        returnList = []
        for nodeName in self.Nodes:
            returnList.append(self.Nodes[nodeName])
        return returnList
    def nodesOfType(self, nodeClass):
        returnList = []
        for node in self.allNodes():
            if node['ClassName'].getValue() == nodeClass:
                returnList.append(node)
        return returnList
    def selectedNodes(self):
        returnList = []
        for nodeName in self.Nodes:
            if self.Nodes[nodeName]['selected'].getValue() == True:
                returnList.append(self.Nodes[nodeName])
        return returnList    
    def nodeCreated(self):
        #Overridable event
        return
    def SoftDelete(self):
        print('Please implement this soon')
    def getAssignedXPos(self):
        return AppCore.AppAttributes[self.className+'-GraphX']
    def getAssignedYPos(self):
        return AppCore.AppAttributes[self.className+'-GraphY']