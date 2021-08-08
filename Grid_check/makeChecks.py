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


import UI_makeChecks
import checkClass
import importlib
importlib.reload(UI_makeChecks)
importlib.reload(checkClass)
import salome

import SMESH
from PyQt5 import QtCore, QtGui, QtWidgets
from salome.smesh import smeshBuilder
from salome.gui import helper
from qtsalome import QDialog, QFileDialog


def checkNonOrthogonality(context):
  
  class ExportDialog(QDialog):
    
    def __init__(self):
      QDialog.__init__(self)
      # Set up the user interface from Designer.
      #self.ui = EDZ_permeability_dataset_GUI.Ui_Dialog()
      self.ui = UI_makeChecks.Ui_Dialog()
      self.ui.setupUi(self)
      self.show()
      #initialization
      self.selectMesh = False
      self.selectedMesh = None
      #connect button
      self.ui.pb_origMeshFile.clicked.connect(self.setMeshInput)
      self.ui.pb_compute.clicked.connect(self.computeStats)
      self.ui.pb_group_no.clicked.connect(self.makeNonOrthGroup)
      self.ui.pb_group_skew.clicked.connect(self.makeSkewGroup)
      self.ui.pb_export.clicked.connect(self.saveQuality)
      # make check object
      self.MQC = None
      return
      
    ### MESH SELECTION
    def select(self):
      #sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      mesh = helper.getSObjectSelected()[0].GetObject()
      if self.selectMesh:
        self._selectMeshInput(mesh)
      return
      
    def _selectMeshInput(self, mesh):
      self.selectedMesh = mesh
      name = ''
      if isinstance(self.selectedMesh,salome.smesh.smeshBuilder.meshProxy):
        name = salome.smesh.smeshBuilder.GetName(self.selectedMesh)
        smesh = salome.smesh.smeshBuilder.New()
        self.selectedMesh = smesh.Mesh(self.selectedMesh)
        if not self.selectedMesh.GetElementsByType(SMESH.VOLUME):
          self.printErrorMessage('PFLOTRAN mesh need to 3-dimensional. Please select a 3D mesh. If you mesh is 1 or 2-dimensional, extrude it in the others direction with an unit length.')
          self.ui.le_origMeshFile.setText('')
          self.selectedMesh = None
          return
      self.ui.le_origMeshFile.setText(name)
      return
      
    def setMeshInput(self):
      if self.selectMesh == True:
        self.selectMesh = False
        context.sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      else:
        self.selectMesh = True
        context.sg.getObjectBrowser().selectionChanged.connect(self.select)
        self.select()
      return
    
    ### COMPUTE STATS
    def computeStats(self):
      self.MQC = checkClass.MeshQualityCheck(self.selectedMesh)
      self.MQC.checkMesh()
      NonOrth = self.MQC.getNonOrth()
      Skew = self.MQC.getSkew()
      self.ui.plot_no.plotHist(NonOrth, 18, xlab='Non orthogonality angle (°)', ylab='Number of volume', title='', xlim=None, ylim=None, grid=True)
      self.ui.plot_skew.plotHist(Skew, 18, xlab='Skewness', ylab='Number of volume', title='', xlim=None, ylim=None, grid=True)
      return
      
    ### GROUP
    def makeNonOrthGroup(self):
      if self.MQC is None: self.computeStats()
      self.MQC.createNonOrthGroup(float(self.ui.le_group_no.text()))
      if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
      return
      
    def makeSkewGroup(self):
      if self.MQC is None: self.computeStats()
      self.MQC.createSkewGroup(float(self.ui.le_group_skew.text()))
      if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
      return
    
    ### EXPORT
    def saveQuality(self):
      dialog = QFileDialog()
      f_out = dialog.getSaveFileName(None, "Select an output filename", 
                                     "", "Text file (*.txt)")
      f_out = f_out[0]
      if not f_out:
        return
      if f_out[-4:] != ".txt":
        f_out += ".txt"
      if self.MQC is None: self.computeStats()
      self.MQC.exportQuality(f_out)
      return
      
  
  ### LAUNCH WINDOWS
  window = ExportDialog()
  window.exec_()
  result = window.result()
    
  return
    

