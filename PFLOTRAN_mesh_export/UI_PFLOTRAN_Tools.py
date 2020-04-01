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
    
    #submesh export
    self.gridLayout_submesh = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_submesh.setObjectName("gridLayout_submesh")
    #enable
    self.cb_enableSubmesh = QtWidgets.QCheckBox(Dialog)
    self.cb_enableSubmesh.setObjectName("cb_enableSubmesh")
    self.gridLayout_submesh.addWidget(self.cb_enableSubmesh, 0, 0, 2, 1)
    self.label_enableSubmesh = QtWidgets.QLabel(Dialog)
    #addlayout
    self.gridLayout_main.addLayout(self.gridLayout_submesh, 1, 0)
    #submesh_selection
    self.gridLayout_submesh_sel= QtWidgets.QGridLayout(Dialog)
    self.gridLayout_submesh_sel.setObjectName("gridLayout_submesh_sel")
    #table available
    self.table_availableMesh = QtWidgets.QTableWidget(Dialog)
    self.table_availableMesh.setObjectName("table_available")
    self.table_availableMesh.setColumnCount(1)
    self.table_header_0 = QtWidgets.QTableWidgetItem()
    self.table_availableMesh.setHorizontalHeaderItem(0,self.table_header_0)
    self.table_availableMesh.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    self.gridLayout_submesh_sel.addWidget(self.table_availableMesh, 0, 0, 4, 1)
    #add/remove submesh
    self.pb_addSubmesh = QtWidgets.QPushButton(Dialog)
    self.pb_addSubmesh.setObjectName("pb_addSubmesh")
    self.pb_addSubmesh.setText("+")
    self.pb_removeSubmesh = QtWidgets.QPushButton(Dialog)
    self.pb_removeSubmesh.setObjectName("pb_removeSubmesh")
    self.pb_removeSubmesh.setText("-")
    self.gridLayout_submesh_sel.addWidget(self.pb_addSubmesh, 1, 1, 1, 1)
    self.gridLayout_submesh_sel.addWidget(self.pb_removeSubmesh, 2, 1, 1, 1)
    #table to export
    self.table_toExport = QtWidgets.QTableWidget(Dialog)
    self.table_toExport.setObjectName("table_toExport")
    self.table_toExport.setColumnCount(3)
    self.table_toExport.setHorizontalHeaderItem(0,QtWidgets.QTableWidgetItem("Groups to export"))
    self.table_toExport.setHorizontalHeaderItem(1,QtWidgets.QTableWidgetItem("Name"))
    self.table_toExport.setHorizontalHeaderItem(2,QtWidgets.QTableWidgetItem("Groups type"))
    self.gridLayout_submesh_sel.addWidget(self.table_toExport, 0, 2, 4,1)
    #add submesh_sel layout
    self.gridLayout_main.addLayout(self.gridLayout_submesh_sel, 2, 0)
    
    #output format
    self.gridLayout_outputFormat = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_outputFormat.setObjectName("gridLayout_submesh")
    self.label_outputFormat = QtWidgets.QLabel(Dialog)
    self.label_outputFormat.setObjectName("label_outputFormat")
    self.gridLayout_outputFormat.addWidget(self.label_outputFormat, 0, 0)
    self.rb_outputFormatGroup = QtWidgets.QButtonGroup(Dialog)
    self.possibleOutputFormat = ['Binary (HDF5)', 'Human readable (ASCII)']
    self.rb_outputFormat = [QtWidgets.QRadioButton(Dialog) for i in self.possibleOutputFormat]
    for i,radio in enumerate(self.rb_outputFormat):
      radio.setObjectName(self.possibleOutputFormat[i])
      radio.setText(self.possibleOutputFormat[i])
      self.rb_outputFormatGroup.addButton(radio)
      self.gridLayout_outputFormat.addWidget(radio, 0, i+1)
    self.rb_outputFormat[0].setChecked(True)
    self.gridLayout_main.addLayout(self.gridLayout_outputFormat, 3, 0)
    
    #grid format
    self.gridLayout_gridFormat = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_gridFormat.setObjectName("gridLayout_gridFormat")
    self.label_gridFormat = QtWidgets.QLabel(Dialog)
    self.label_gridFormat.setObjectName("label_gridFormat")
    self.gridLayout_gridFormat.addWidget(self.label_gridFormat, 0, 0)
    self.rb_gridFormatGroup = QtWidgets.QButtonGroup(Dialog)
    self.possibleGridFormat = ['Implicit', 'Explicit']
    self.rb_gridFormat = [QtWidgets.QRadioButton(Dialog) for i in self.possibleGridFormat]
    for i,radio in enumerate(self.rb_gridFormat):
      radio.setObjectName(self.possibleGridFormat[i])
      radio.setText(self.possibleGridFormat[i])
      self.rb_gridFormatGroup.addButton(radio)
      self.gridLayout_gridFormat.addWidget(radio, 0, i+1)
    self.rb_gridFormat[0].setChecked(True)
    self.rb_gridFormat[1].setCheckable(False)
    self.gridLayout_main.addLayout(self.gridLayout_gridFormat, 4, 0)
    
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
    self.gridLayout_main.addLayout(self.gridLayout_output, 5, 0)
    
    #autocompletion
    self.gridLayout_forceFullCalculation = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_forceFullCalculation.setObjectName("gridLayout_forceFullCalculation")
    #enable
    self.cb_forceFullCalculation = QtWidgets.QCheckBox(Dialog)
    self.cb_forceFullCalculation.setObjectName("cb_forceFullCalculation")
    self.gridLayout_forceFullCalculation.addWidget(self.cb_forceFullCalculation, 0, 0)
    #addlayout
    self.gridLayout_main.addLayout(self.gridLayout_forceFullCalculation, 6, 0)
    
    #ok and cancel button
    self.splitter = QtWidgets.QSplitter(Dialog)
    self.splitter.setOrientation(QtCore.Qt.Horizontal)
    self.splitter.setObjectName("splitter")
    self.pb_help = QtWidgets.QPushButton(self.splitter)
    self.pb_help.setObjectName("pb_help")
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
    Dialog.setWindowTitle(_translate("Dialog", "Export Salome meshes to PFLOTRAN"))
    #MSO
    self.pb_origMeshFile.setText(_translate("Dialog", "Select"))
    self.label_mesh.setText(_translate("Dialog", "Mesh to export:"))
    self.pb_origOutputFile.setText(_translate("Dialog", "Select"))
    self.label_output.setText(_translate("Dialog", "Destination folder and name:"))
    #submesh export
    self.cb_enableSubmesh.setText(_translate("Dialog", "Export Salome submeshes or groups as PFLOTRAN regions"))
    self.table_header_0.setText(_translate("Dialog", "Available groups"))
    self.label_outputFormat.setText(_translate("Dialog", "Output format:"))
    self.label_gridFormat.setText(_translate("Dialog", "Grid format:"))
    self.cb_forceFullCalculation.setText(_translate("Dialog", "Force full calculation for element's node order"))
    #help
    self.pb_help.setText(_translate("Dialog", "Help"))
  
  
  def setDefaultValue(self):
    pass
  

if 0:
  class dialogBox(QDialog):
    
    def setupUi(self, Dialog):
      Dialog.setObjectName("Dialog")
      Dialog.resize(150, 380)
      Dialog.setSizeGripEnabled(False)
      
      #principal layout
      self.gridLayout_main = QtWidgets.QGridLayout(Dialog)
      self.gridLayout_main.setObjectName("gridLayout_main")
      #text
      self.gridLayout_text = QtWidgets.QGridLayout(Dialog)
      self.gridLayout_text.setObjectName("gridLayout_text")
      #mesh
      self.label_text = QtWidgets.QLabel(Dialog)
      self.label_text.setObjectName("label_text")
      self.gridLayout_text.addWidget(self.label_text, 0, 0)
      self.gridLayout_main.addLayout(self.gridLayout_text, 0, 0)
      
      #ok and cancel button
      self.splitter = QtWidgets.QSplitter(Dialog)
      self.splitter.setOrientation(QtCore.Qt.Horizontal)
      self.splitter.setObjectName("splitter")
      self.pb_help = QtWidgets.QPushButton(self.splitter)
      self.pb_help.setObjectName("pb_help")
      self.pb_okCancel = QtWidgets.QDialogButtonBox(self.splitter)
      self.pb_okCancel.setOrientation(QtCore.Qt.Horizontal)
      self.pb_okCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
      self.pb_okCancel.setObjectName("pb_okCancel")
      self.gridLayout_main.addWidget(self.splitter, 1, 0)
      self.pb_okCancel.accepted.connect(Dialog.accept)
      self.pb_okCancel.rejected.connect(Dialog.reject)
      
    def setText(self, text):
      self.label_text.setText(text)
      
    def setTitle(self, Dialog, title):
      Dialog.setWindowTitle(title)


