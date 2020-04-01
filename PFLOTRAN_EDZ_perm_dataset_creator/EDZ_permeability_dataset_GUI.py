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
    Dialog.resize(416, 380)
    Dialog.setSizeGripEnabled(False)
    
    #principal layout
    self.gridLayout_main = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_main.setObjectName("gridLayout_main")
    #QtWidgets.QWidget.setLayout(self.gridLayout_main)
    
    #mesh/surface/output selection
    self.gridLayout_MSO = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_MSO.setObjectName("gridLayout_MSO")
    #mesh
    self.label_mesh = QtWidgets.QLabel(Dialog)
    self.label_mesh.setObjectName("label_mesh")
    self.pb_origMeshFile = QtWidgets.QPushButton(Dialog)
    self.pb_origMeshFile.setObjectName("origMeshFile")
    self.pb_origMeshFile.setCheckable(True)
    self.le_origMeshFile = QtWidgets.QLineEdit(Dialog)
    self.le_origMeshFile.setObjectName("le_origMeshFile")
    self.le_origMeshFile.setReadOnly(True)
    self.gridLayout_MSO.addWidget(self.label_mesh, 0, 0)
    self.gridLayout_MSO.addWidget(self.pb_origMeshFile, 0, 2)
    self.gridLayout_MSO.addWidget(self.le_origMeshFile, 0, 1)
    #surface
    self.label_surface = QtWidgets.QLabel(Dialog)
    self.label_surface.setObjectName("label_surface")
    self.pb_origSurfaceFile = QtWidgets.QPushButton(Dialog)
    self.pb_origSurfaceFile.setObjectName("origSurfaceFile")
    self.pb_origSurfaceFile.setCheckable(True)
    self.le_origSurfaceFile = QtWidgets.QLineEdit(Dialog)
    self.le_origSurfaceFile.setObjectName("le_origSurfaceFile")
    self.le_origSurfaceFile.setReadOnly(True)
    self.gridLayout_MSO.addWidget(self.label_surface, 1, 0)
    self.gridLayout_MSO.addWidget(self.pb_origSurfaceFile, 1, 2)
    self.gridLayout_MSO.addWidget(self.le_origSurfaceFile, 1, 1)
    #ouptut
    self.label_output = QtWidgets.QLabel(Dialog)
    self.label_output.setObjectName("label_output")
    self.pb_origOutputFile = QtWidgets.QPushButton(Dialog)
    self.pb_origOutputFile.setObjectName("origOutputFile")
    self.le_origOutputFile = QtWidgets.QLineEdit(Dialog)
    self.le_origOutputFile.setObjectName("le_origOutputFile")
    self.gridLayout_MSO.addWidget(self.label_output, 2, 0)
    self.gridLayout_MSO.addWidget(self.pb_origOutputFile, 2, 2)
    self.gridLayout_MSO.addWidget(self.le_origOutputFile, 2, 1)
    
    self.gridLayout_main.addLayout(self.gridLayout_MSO, 0, 0)
    
    #Properties
    self.gridLayout_properties = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_properties.setObjectName("gridLayout_properties")
    self.gridLayout_properties_label = QtWidgets.QGridLayout(Dialog)
    self.label_properties = QtWidgets.QLabel(Dialog)
    self.label_properties.setObjectName("label_properties")
    self.gridLayout_properties_label.addWidget(self.label_properties, 0, 0)
    self.gridLayout_properties_label.addWidget(self.label_properties, 0, 0)
    self.gridLayout_properties.addLayout(self.gridLayout_properties_label, 0, 0)
    
    #Density/distance
    #label density distance
    self.gridLayout_density = QtWidgets.QGridLayout(Dialog)
    self.gridLayout_density.setObjectName("gridLayout_density")
    self.label_density_distance = QtWidgets.QLabel(Dialog)
    self.label_density_distance.setObjectName("label_density_distance")
    self.gridLayout_density.addWidget(self.label_density_distance, 0, 0)
    #trace length
    self.label_trace_length =  QtWidgets.QLabel(Dialog)
    self.gridLayout_density.setObjectName("label_trace_length")
    self.le_traceLength = QtWidgets.QLineEdit(Dialog)
    self.le_traceLength.setObjectName("le_traceLength")
    self.gridLayout_density.addWidget(self.label_trace_length, 1, 0)
    self.gridLayout_density.addWidget(self.le_traceLength, 1, 1)
    #attenuation length
    self.label_attenuation_length =  QtWidgets.QLabel(Dialog)
    self.gridLayout_density.setObjectName("label_attenuation_length")
    self.le_attenuationLength = QtWidgets.QLineEdit(Dialog)
    self.le_attenuationLength.setObjectName("le_attenuationLength")
    self.gridLayout_density.addWidget(self.label_attenuation_length, 1, 2)
    self.gridLayout_density.addWidget(self.le_attenuationLength, 1, 3)
    self.gridLayout_properties.addLayout(self.gridLayout_density, 1, 0)
    
    #fracture properties
    #label
    self.gridLayout_fracProps= QtWidgets.QGridLayout(Dialog)
    self.gridLayout_fracProps.setObjectName("gridLayout_fracProps")
    self.label_fracProps = QtWidgets.QLabel(Dialog)
    self.label_fracProps.setObjectName("label_fracProps")
    self.gridLayout_fracProps.addWidget(self.label_fracProps, 0, 0)
    #fractures is considered circular, add radion button to let the user decide
    #radius
    self.label_radius =  QtWidgets.QLabel(Dialog)
    self.gridLayout_density.setObjectName("label_radius")
    self.le_radius = QtWidgets.QLineEdit(Dialog)
    self.le_radius.setObjectName("le_radius")
    self.gridLayout_fracProps.addWidget(self.label_radius, 1, 0)
    self.gridLayout_fracProps.addWidget(self.le_radius, 1, 1)
    #aperture
    self.label_aperture =  QtWidgets.QLabel(Dialog)
    self.gridLayout_density.setObjectName("label_aperture")
    self.le_aperture = QtWidgets.QLineEdit(Dialog)
    self.le_aperture.setObjectName("le_aperture")
    self.gridLayout_fracProps.addWidget(self.label_aperture, 1, 2)
    self.gridLayout_fracProps.addWidget(self.le_aperture, 1, 3)
    
    self.gridLayout_properties.addLayout(self.gridLayout_fracProps, 2, 0)
    
    #anistropy
    #label
    self.gridLayout_aniso= QtWidgets.QGridLayout(Dialog)
    self.gridLayout_aniso.setObjectName("gridLayout_anisotropy")
    self.label_aniso = QtWidgets.QLabel(Dialog)
    self.label_aniso.setObjectName("label_aniso")
    self.gridLayout_aniso.addWidget(self.label_aniso, 0, 0)
    #enable
    self.cb_enable = QtWidgets.QCheckBox(Dialog)
    self.cb_enable.setObjectName("cb_enable")
    self.gridLayout_aniso.addWidget(self.cb_enable, 1, 0)
    self.label_anisoFactor = QtWidgets.QLabel(Dialog)
    self.label_anisoFactor.setObjectName("label_anisoFactor")
    self.gridLayout_aniso.addWidget(self.label_anisoFactor, 1, 1)
    self.le_anisoFactor = QtWidgets.QLineEdit(Dialog)
    self.le_anisoFactor.setObjectName("le_anisoFactor")
    self.le_anisoFactor.setReadOnly(True)
    self.gridLayout_aniso.addWidget(self.le_anisoFactor, 1, 2)
    
    self.gridLayout_properties.addLayout(self.gridLayout_aniso, 3, 0)
    
    #permeability model
    self.gridLayout_permModel= QtWidgets.QGridLayout(Dialog)
    self.gridLayout_permModel.setObjectName("gridLayout_permModel")
    self.label_permModel = QtWidgets.QLabel(Dialog)
    self.label_permModel.setObjectName("label_permModel")
    self.gridLayout_permModel.addWidget(self.label_permModel, 0, 0)
    #permeability choice
    self.possibleChoice = ['Mourzencko', 'Snow']
    self.choice = [QtWidgets.QRadioButton(Dialog) for i in self.possibleChoice]
    for i,radio in enumerate(self.choice):
      radio.setObjectName(self.possibleChoice[i])
      radio.setText(self.possibleChoice[i])
      self.gridLayout_permModel.addWidget(radio, 1, i)
    
    self.gridLayout_properties.addLayout(self.gridLayout_permModel, 4, 0)
    
    #matrix
    self.gridLayout_matrix= QtWidgets.QGridLayout(Dialog)
    self.gridLayout_matrix.setObjectName("gridLayout_matrix")
    self.label_matrix = QtWidgets.QLabel(Dialog)
    self.label_matrix.setObjectName("label_matrix")
    self.gridLayout_matrix.addWidget(self.label_matrix, 0, 0)
    #coupling mode
    self.label_coupling = QtWidgets.QLabel(Dialog)
    self.label_coupling.setObjectName("label_coupling")
    self.gridLayout_matrix.addWidget(self.label_coupling, 1, 0)
    self.rb_couplingGroup = QtWidgets.QButtonGroup(Dialog)
    self.possibleCoupling = ['Standard', 'Advanced']
    self.rb_coupling = [QtWidgets.QRadioButton(Dialog) for i in self.possibleCoupling]
    for i,radio in enumerate(self.rb_coupling):
      radio.setObjectName(self.possibleCoupling[i])
      radio.setText(self.possibleCoupling[i])
      self.rb_couplingGroup.addButton(radio)
      self.gridLayout_matrix.addWidget(radio, 1, i+2)
    self.rb_coupling[0].setChecked(True)
    #matrix permeability
    self.label_matrixPerm =  QtWidgets.QLabel(Dialog)
    self.gridLayout_density.setObjectName("label_matrixPerm")
    self.le_matrixPerm = QtWidgets.QLineEdit(Dialog)
    self.le_matrixPerm.setObjectName("le_matrixPerm")
    self.gridLayout_matrix.addWidget(self.label_matrixPerm, 2, 0)
    self.gridLayout_matrix.addWidget(self.le_matrixPerm, 2, 3)
    
    self.gridLayout_properties.addLayout(self.gridLayout_matrix, 5, 0)
    
    self.gridLayout_main.addLayout(self.gridLayout_properties, 1, 0)
    
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
    self.gridLayout_main.addWidget(self.splitter, 2, 0)
    self.pb_okCancel.accepted.connect(Dialog.accept)
    self.pb_okCancel.rejected.connect(Dialog.reject)
      
    self.retranslateUi(Dialog)
    self.setDefaultValue()
    

    
  def retranslateUi(self, Dialog):
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "EDZ permeability dataset creator"))
    #MSO
    self.pb_origMeshFile.setText(_translate("Dialog", "Select"))
    self.label_mesh.setText(_translate("Dialog", "Mesh:"))
    self.pb_origSurfaceFile.setText(_translate("Dialog", "Select"))
    self.label_surface.setText(_translate("Dialog", "Surface:"))
    self.pb_origOutputFile.setText(_translate("Dialog", "Select"))
    self.label_output.setText(_translate("Dialog", "Output:"))
    #properties
    self.label_properties.setText(_translate("Dialog", "Excavated Damaged Zone properties"))
    #density distance
    self.label_density_distance.setText(_translate("Dialog", "Density vs distance law:"))
    self.label_trace_length.setText(_translate("Dialog", "Trace length (m-1):"))
    self.label_attenuation_length.setText(_translate("Dialog", "Attenuation length (m):"))
    #fracture properties
    self.label_fracProps.setText(_translate("Dialog", "Fracture properties"))
    self.label_radius.setText(_translate("Dialog", "Fracture radius (m):"))
    self.label_aperture.setText(_translate("Dialog", "Fracture aperture (m):"))
    #anisotropy
    self.label_aniso.setText(_translate("Dialog", "Anisotropy"))
    self.cb_enable.setText(_translate("Dialog", "Enable anisotropy"))
    self.label_anisoFactor.setText(_translate("Dialog", "Anisotropy factor:"))
    #perm model
    self.label_permModel.setText(_translate("Dialog", "Permeability model"))
    #matrix
    self.label_matrix.setText(_translate("Dialog", "Matrix properties"))
    self.label_coupling.setText(_translate("Dialog", "Coupling method:"))
    self.label_matrixPerm.setText(_translate("Dialog", "Matrix permeability (m2)"))
    
    #help
    self.pb_help.setText(_translate("Dialog", "Help"))
    
    
  def setDefaultValue(self):
    #testing purpose
    self.le_traceLength.setText('0.82')
    self.le_attenuationLength.setText('1.5')
    self.le_radius.setText('2')
    self.le_aperture.setText('1e-4')
    self.le_anisoFactor.setText('5')
    self.le_matrixPerm.setText('1e-8')
    

  

