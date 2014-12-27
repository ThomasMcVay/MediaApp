#===============================================================================
# @License: 
#    This example file is public domain. See MediaApp_LGPL.txt ADDENDUM.
#    You may do the following things with this file without restrictions or conditions:
#        1. Modify it.
#        2. Remove or modify this section to your liking.
#        3. Redistribute it under any licensing terms that you wish.
#        4. Make copyright claims to derivative works of this file.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#===============================================================================

from PySide import QtGui, QtCore
import sys
import cmd
import pdb

import __init__ as MyApp

def main():
    MyApp.run()

    pNode = MyApp.Core.createNode('Clip')
    pNode['xpos'].setValue(0)
    pNode['ypos'].setValue(0)

    #sys.exit(MyApp.Core.App.exec_())
    #MyApp.Core.App.exec_()
    
if __name__ == '__main__':
    main()