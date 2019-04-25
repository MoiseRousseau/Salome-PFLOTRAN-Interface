#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Author : Moise Rousseau (2019), email at moise.rousseau@polymtl.ca


#TODO
# dialog box for path / ascii / region


import sys
from qtsalome import *


class PFLOTRANTools_UI(QDialog):
  """
  This class defines the design of a Qt dialog box dedicated to the
  salome plugin examples. It presents a UI form that contains
  parameters for the spatial dimensions of geometrical object.  
  """
  def __init__(self, parent=None):
    QDialog.__init__(self, parent)
    self.setupUi()

  def setupUi(self):
    self.setObjectName("Dialog")
    self.resize(400, 300)
    self.hboxlayout = QHBoxLayout(self)
    self.hboxlayout.setContentsMargins(9,9,9,9)
    self.hboxlayout.setSpacing(6)
    self.hboxlayout.setObjectName("hboxlayout")
    self.vboxlayout = QVBoxLayout()
    self.vboxlayout.setContentsMargins(0,0,0,0)
    self.vboxlayout.setSpacing(6)
    self.vboxlayout.setObjectName("vboxlayout")
    self.hboxlayout1 = QHBoxLayout()
    self.hboxlayout1.setContentsMargins(0,0,0,0)
    self.hboxlayout1.setSpacing(6)
    self.hboxlayout1.setObjectName("hboxlayout1")
    self.vboxlayout1 = QVBoxLayout()
    self.vboxlayout1.setContentsMargins(0,0,0,0)
    self.vboxlayout1.setSpacing(6)
    self.vboxlayout1.setObjectName("vboxlayout1")
    self.lblRadius = QLabel(self)
    self.lblRadius.setObjectName("lblRadius")
    self.vboxlayout1.addWidget(self.lblRadius)
    self.lblLength = QLabel(self)
    self.lblLength.setObjectName("lblLength")
    self.vboxlayout1.addWidget(self.lblLength)
    self.lblWidth = QLabel(self)
    self.lblWidth.setObjectName("lblWidth")
    self.vboxlayout1.addWidget(self.lblWidth)
    self.hboxlayout1.addLayout(self.vboxlayout1)
    self.vboxlayout2 = QVBoxLayout()
    self.vboxlayout2.setContentsMargins(0,0,0,0)
    self.vboxlayout2.setSpacing(6)
    self.vboxlayout2.setObjectName("vboxlayout2")
    self.txtRadius = QLineEdit(self)
    self.txtRadius.setObjectName("txtRadius")
    self.vboxlayout2.addWidget(self.txtRadius)
    self.txtLength = QLineEdit(self)
    self.txtLength.setObjectName("txtLength")
    self.vboxlayout2.addWidget(self.txtLength)
    self.txtWidth = QLineEdit(self)
    self.txtWidth.setObjectName("txtWidth")
    self.vboxlayout2.addWidget(self.txtWidth)
    self.hboxlayout1.addLayout(self.vboxlayout2)
    self.vboxlayout.addLayout(self.hboxlayout1)
    spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    self.vboxlayout.addItem(spacerItem)
    self.buttonBox = QDialogButtonBox(self)
    self.buttonBox.setOrientation(Qt.Horizontal)
    self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.NoButton|QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")
    self.vboxlayout.addWidget(self.buttonBox)
    self.hboxlayout.addLayout(self.vboxlayout)

    self.setWindowTitle("Tube construction")
    self.lblRadius.setText("Rayon")
    self.lblLength.setText("Longueur")
    self.lblWidth.setText("Epaisseur")

#
# ======================================================================
# Unit test
# ======================================================================
#
def main( args ):
  a = QApplication(sys.argv)
  dialog = PFLOTRANTools_UI()
  sys.exit(dialog.exec_())

if __name__=="__main__":
  main(sys.argv)





