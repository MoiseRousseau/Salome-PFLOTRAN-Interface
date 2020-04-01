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
# Author : Moise Rousseau (2020), email at moise.rousseau@polymtl.ca


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):

  def setupUi(self, Dialog):
    Dialog.setObjectName("Dialog")
    Dialog.resize(450, 380)
    Dialog.setSizeGripEnabled(True)
    
    #principal layout
    self.gridLayout_main = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_main.setObjectName("gridLayout_main")
    #QtWidgets.QWidget.setLayout(self.gridLayout_main)
    
    #mesh selection
    self.gridLayout_mesh = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_mesh.setObjectName("gridLayout_mesh")
    #mesh
    self.label_mesh = QtWidgets.QLabel(Dialog)
    self.label_mesh.setObjectName("label_mesh")
    self.pb_origMeshFile = QtWidgets.QPushButton(Dialog)
    self.pb_origMeshFile.setObjectName("origMeshFile")
    self.pb_origMeshFile.setCheckable(True)
    self.le_origMeshFile = QtWidgets.QLineEdit(Dialog)
    self.le_origMeshFile.setObjectName("le_origMeshFile")
    self.le_origMeshFile.setReadOnly(True)
    self.gridLayout_mesh.addWidget(self.label_mesh, 0, 0)
    self.gridLayout_mesh.addWidget(self.pb_origMeshFile, 0, 2)
    self.gridLayout_mesh.addWidget(self.le_origMeshFile, 0, 1)
    #add layout
    self.gridLayout_main.addLayout(self.gridLayout_mesh, 0, 0)
    
    #grid format
    self.gridLayout_gridFormat = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_gridFormat.setObjectName("gridLayout_gridFormat")
    self.label_gridFormat = QtWidgets.QLabel(Dialog)
    self.label_gridFormat.setObjectName("label_gridFormat")
    self.gridLayout_gridFormat.addWidget(self.label_gridFormat, 0, 0)
    self.rb_gridFormatGroup = QtWidgets.QButtonGroup(Dialog)
    self.possibleGridFormat = ['Coordinates and direction', 'Vertices', 'Cell ids']
    self.rb_gridFormat = [QtWidgets.QRadioButton(Dialog) for i in self.possibleGridFormat]
    for i,radio in enumerate(self.rb_gridFormat):
      radio.setObjectName(self.possibleGridFormat[i])
      radio.setText(self.possibleGridFormat[i])
      self.rb_gridFormatGroup.addButton(radio)
      self.gridLayout_gridFormat.addWidget(radio, 0, i+1)
    self.rb_gridFormat[0].setChecked(True)
    self.rb_gridFormat[1].setCheckable(True)
    self.gridLayout_main.addLayout(self.gridLayout_gridFormat, 1, 0)
    
    #output
    self.gridLayout_output = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_output.setObjectName("gridLayout_output")
    self.label_output = QtWidgets.QLabel(Dialog)
    self.label_output.setObjectName("label_output")
    self.pb_origOutputFile = QtWidgets.QPushButton(Dialog)
    self.pb_origOutputFile.setObjectName("origOutputFile")
    self.le_origOutputFile = QtWidgets.QLineEdit(Dialog)
    self.le_origOutputFile.setObjectName("le_origOutputFile")
    self.gridLayout_output.addWidget(self.label_output, 0, 0)
    self.gridLayout_output.addWidget(self.pb_origOutputFile, 0, 2)
    self.gridLayout_output.addWidget(self.le_origOutputFile, 0, 1)
    self.gridLayout_main.addLayout(self.gridLayout_output, 2, 0)
    
    #reverse
    self.gridLayout_reverse = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_reverse.setObjectName("gridLayout_autocompletion")
    #enable
    self.cb_reverse = QtWidgets.QCheckBox(Dialog)
    self.cb_reverse.setObjectName("cb_reverse")
    self.gridLayout_reverse.addWidget(self.cb_reverse, 0, 0)
    #addlayout
    self.gridLayout_main.addLayout(self.gridLayout_reverse, 4, 0)
    
    
    #fluxes option
    self.gridLayout_option = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_option.setObjectName("gridLayout_option")
    self.label_option = QtWidgets.QLabel(Dialog)
    self.label_option.setObjectName("label_option")
    self.gridLayout_option.addWidget(self.label_option, 0, 0)
    self.comboBox_option = QtWidgets.QComboBox(Dialog)
    self.possibleOption = ['Signed fluxes', 'Positive fluxes only', 'Absolute fluxes']
    self.comboBox_option.addItems(self.possibleOption)
    self.gridLayout_option.addWidget(self.comboBox_option, 0, 1)
    self.gridLayout_main.addLayout(self.gridLayout_option, 3, 0)
    
    
    #ok and cancel button
    self.splitter = QtWidgets.QSplitter(Dialog)
    self.splitter.setOrientation(QtCore.Qt.Horizontal)
    self.splitter.setObjectName("splitter")
    self.pb_okCancel = QtWidgets.QDialogButtonBox(self.splitter)
    self.pb_okCancel.setOrientation(QtCore.Qt.Horizontal)
    self.pb_okCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
    self.pb_okCancel.setObjectName("pb_okCancel")
    self.gridLayout_main.addWidget(self.splitter, 7, 0)
    self.pb_okCancel.rejected.connect(Dialog.reject)
    
    self.retranslateUi(Dialog)
    self.setDefaultValue()
    

  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "Create integral flux for PFLOTRAN"))
    #MSO
    self.pb_origMeshFile.setText(_translate("Dialog", "Select"))
    self.label_mesh.setText(_translate("Dialog", "Mesh to export:"))
    self.pb_origOutputFile.setText(_translate("Dialog", "Select"))
    self.label_output.setText(_translate("Dialog", "Destination folder and name:"))
    #submesh export
    self.label_gridFormat.setText(_translate("Dialog", "Format:"))
    self.cb_reverse.setText(_translate("Dialog", "Reverse direction"))
    self.label_option.setText(_translate("Dialog", "Fluxes option:"))
  
  
  def setDefaultValue(self):
    pass


