#!/usr/bin/env python3
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

import sys
import os
import importlib
import time

try:
  import h5py
except:
  print("\nh5py package not installed.")
  print("You will not be able to export in HDF5 format\n")

#import plugin component
import exportMesh
import exportSubMesh
import UI_PFLOTRAN_Tools
#reload it to make modification reloaded
importlib.reload(exportMesh)
importlib.reload(exportSubMesh)
importlib.reload(UI_PFLOTRAN_Tools)

#import salome stuff
from salome.smesh import smeshBuilder
from salome.gui import helper
from qtsalome import QDialog, QMessageBox, QFileDialog, QTableWidgetItem
import SMESH
import salome


def PFLOTRANMeshExport(context):

  class ExportDialog(QDialog):
    
    def __init__(self):
      QDialog.__init__(self)
      # Set up the user interface from Designer.
      #self.ui = EDZ_permeability_dataset_GUI.Ui_Dialog()
      self.ui = UI_PFLOTRAN_Tools.Ui_Dialog()
      self.ui.setupUi(self)
      self.show()
      
      # Connect up the selectionChanged() event of the object browser.
      #sg.getObjectBrowser().selectionChanged.connect(self.select)
      self.selectMesh = False
      self.selectedMesh = None
      self.selectSubmesh = False
      self.availableSubmesh = {}
      self.selectedSubmesh = []
      self.binaryOutput = True #default
      self.format = True #implicit or false = explicit
      self.autocomplete = False
      
      # Connect up the buttons.
      self.ui.pb_origMeshFile.clicked.connect(self.setMeshInput)
      self.ui.pb_origOutputFile.clicked.connect(self.setOutputFile,)
      self.ui.pb_help.clicked.connect(self.helpMessage)
      self.ui.cb_enableSubmesh.clicked.connect(self.enableSubmesh)
      self.ui.pb_addSubmesh.clicked.connect(self.addGroup)
      self.ui.pb_removeSubmesh.clicked.connect(self.removeGroup)
      self.ui.pb_okCancel.accepted.connect(self.checkValue)
#      self.ui.rb_outputFormat[0].toggled.connect( \
#                        lambda:self.excludeExplicit(self.ui.rb_outputFormat))
#      self.ui.rb_outputFormat[1].toggled.connect( \
#                        lambda:self.excludeExplicit(self.ui.rb_outputFormat))
      self.ui.rb_gridFormat[0].toggled.connect(self.compressOutputMesh)
      #self.ui.pb_OutputFile.clicked.connect(self.setOutputFile)
      #self.ui.pb_help.clicked.connect(self.helpMessage)
      
      #self.select()
      
      return
      
      
    def select(self):
      mesh = helper.getSObjectSelected()[0].GetObject()
      if self.selectMesh:
        self._selectMeshInput(mesh)
      return
      
    def _selectMeshInput(self,mesh):
      name = ''
      if isinstance(mesh,salome.smesh.smeshBuilder.meshProxy):
        self.selectedMesh = mesh.GetMesh()
        name = smeshBuilder.GetName(mesh)
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
      
    def setOutputFile(self):
      selection = ''
      h5_string = 'PFLOTRAN HDF5 File (*.h5)'
      ascii_exp_string = ';PFLOTRAN Explicit ASCII grid (*.uge)'
      ascii_imp_string = ';PFLOTRAN Implicit ASCII grid (*.ugi)'
      allFiles_string = 'All Files (*)'
      d = ';;'
      if self.ui.rb_outputFormat[0].isChecked(): #HDF5
        selection = h5_string+d+allFiles_string
        ext = 'h5'
      else:
        if self.ui.rb_gridFormat[0].isChecked(): #implicit
          selection = ascii_imp_string+d+allFiles_string
          ext = 'ugi'
        else: #explicit
          selection = ascii_exp_string+d+allFiles_string
          ext = 'uge'

      fd = QFileDialog(self, "Select an output file", self.ui.le_origOutputFile.text(), selection)
      if fd.exec_():
        text = fd.selectedFiles()[0]
        if text.split('.')[-1] != ext:
          text = text + '.' + ext
        self.ui.le_origOutputFile.setText(text)
      return
      
    def enableSubmesh(self):
      if self.selectSubmesh:
        self.selectedSubmesh = []
        self.availableSubmesh = {}
        self.ui.table_availableMesh.setRowCount(0)
        self.ui.table_toExport.setRowCount(0)
        self.selectSubmesh = False
      elif self.selectedMesh:
        groups = []
        for x in self.selectedMesh.GetGroups():
          if not x.GetTypes(): continue
          if (x.GetTypes()[0] == SMESH.VOLUME or x.GetTypes()[0] == SMESH.FACE):
            groups.append(x)
        self.ui.table_availableMesh.setRowCount(len(groups))
        for i,x in enumerate(groups):
          item = QTableWidgetItem()
          item.setText(x.GetName())
          self.ui.table_availableMesh.setItem(i,0, item)
          self.ui.table_availableMesh.itemChanged.connect(self.restaureGroupName)
          self.availableSubmesh[item.text()] = x
        self.selectSubmesh = True
      return
      
    def restaureGroupName(self):
      print('todo')
      #TODO
      return
      
    def addGroup(self):
      self.exchangeTable(self.ui.table_availableMesh, self.ui.table_toExport)
      return
    
    def removeGroup(self):
      self.exchangeTable(self.ui.table_toExport, self.ui.table_availableMesh)
      
    def exchangeTable(self,dep,fin):
      itemsSelected = dep.selectedItems()
      itemsSelectedIndex = dep.selectedIndexes()
      n = fin.rowCount()
      fin.setRowCount(n+len(itemsSelected))
      for i,x in enumerate(itemsSelected):
        group = self.availableSubmesh[x.text()]
        item = QTableWidgetItem()
        item.setText(group.GetName())
        fin.setItem(n+i,0, item)
        fin.setItem(n+i,1, QTableWidgetItem(group.GetName()))
        if group.GetTypes()[0] == SMESH.VOLUME:
          fin.setItem(n+i,2, QTableWidgetItem('VOLUME'))
        elif group.GetTypes()[0] == SMESH.FACE:
          fin.setItem(n+i,2, QTableWidgetItem('FACE'))
        else:
          pass
        #self.selectedSubmesh.append(group)
      for x in itemsSelectedIndex:
        dep.removeRow(x.row())
      return
      
#    def excludeExplicit(self, rb_list):
#      if rb_list[0].isChecked(): #exclude
#        self.ui.rb_gridFormat[1].setCheckable(False)
#      if rb_list[1].isChecked(): #include
#        self.ui.rb_gridFormat[1].setCheckable(True)
#      return
      
    def compressOutputMesh(self):
      if self.ui.rb_gridFormat[1].isChecked():
        self.ui.cb_compressH5Output.setCheckable(False)
      else:
        self.ui.cb_compressH5Output.setCheckable(True)
      return
     
    def helpMessage(self):
      import subprocess
      subprocess.Popen(['firefox'], shell=False)
      return
      
    def printErrorMessage(self, text):
      #import qtsalome
      #msg = qtsalome.QMessageBox()
      msg = QMessageBox()
      #msg.setTitle('Error!')
      msg.setText(text)
      msg.setIcon(QMessageBox.Critical)
      msg.setStandardButtons(QMessageBox.Ok)
      msg.exec_()
      return
      
    def printInformationMessage(self, text):
      #import qtsalome
      msg = QMessageBox()
      #msg.setTitle('Error!')
      msg.setText(text)
      msg.setIcon(QMessageBox.Information)
      msg.setStandardButtons(QMessageBox.Ok)
      msg.exec_()
      return
      
    def printMessageYesNo(self, text):
      #import qtsalome
      msg = QMessageBox()
      #msg.setTitle('Error!')
      msg.setText(text)
      msg.setIcon(QMessageBox.Information)
      msg.setStandardButtons(QMessageBox.Yes| QMessageBox.No)
      reply = msg.exec_()
      if reply == QMessageBox.Yes: return True
      else: return False
      
    def checkValue(self):
      #check output file
      if not self.ui.le_origOutputFile.text():
        self.printErrorMessage('Please provide an output file')
        return
      if os.path.isfile(self.ui.le_origOutputFile.text()):
        res = self.printMessageYesNo('The output file you provided already exist and will be ecrased. Continue ?')
        if not res:
          return
      #h5py module
      if self.ui.rb_outputFormat[0].isChecked(): 
        try:
          import h5py
        except:
          self.printErrorMessage('h5py module not installed. You should install it before to export meshes in HDF5 format.')
          return
      #export group in explicit
      #if self.selectSubmesh and not self.ui.rb_gridFormat[0].isChecked():
      #  res = self.printMessageYesNo('Explicit format group exportation not implemented so far. Group exportation will be ignored. Continue ?')
      #  if not res:
      #    return
      
      #for row in range(window.ui.table_toExport.rowCount()):
      
      self.accept()
      return


  window = ExportDialog()
  window.exec_()
  result = window.result()
  
  if result:
    start_time = time.time()
    
    print ("\n\n\n")
    print ("##########################################\n")
    print (" PFLOTRAN mesh converter for Salome 9.4.0 \n")
    print ("        By Moise Rousseau (2020)     \n")
    print ("    Export Salome meshes to PPFLOTRAN  \n")
    print ("##########################################\n")
    
    #retrieve data from the GUI
    #mesh to export
    meshToExport = window.selectedMesh #Mesh object
    #destination file
    name = window.ui.le_origOutputFile.text().split('/')[-1]
    folder = window.ui.le_origOutputFile.text()[0:-len(name)]
    #output format
    HDF5 = 1 ; ASCII = 2
    if window.ui.rb_outputFormat[0].isChecked(): outFormat = HDF5
    else: outFormat = ASCII
    #grid format
    IMPLICIT = 1 ; EXPLICIT = 2
    if window.ui.rb_gridFormat[0].isChecked(): gridFormat = IMPLICIT
    else: gridFormat = EXPLICIT
    #group to export
    groupsToExport = []
    if window.selectSubmesh: 
      groups = meshToExport.GetGroups()
      for row in range(window.ui.table_toExport.rowCount()):
        groupNameInSalome = window.ui.table_toExport.item(row,0).text()
        groupNameInOut = window.ui.table_toExport.item(row,1).text()
        if window.ui.table_toExport.item(row,2).text() == 'VOLUME':
          groupType = SMESH.VOLUME
        elif window.ui.table_toExport.item(row,2).text() == 'FACE':
          groupType = SMESH.FACE
        count = 0
        for group in groups:
          if group.GetName() == groupNameInSalome:
            count += 1
            group_to_add = group
        #warning / error message
        if count != 1:
          window.printErrorMessage('Two or more groups have the same name in Salome. Please assign different group name for each group to export and retry')
          return
        groupsToExport.append([group_to_add, groupNameInOut])
    if window.ui.cb_compressH5Output.isChecked() and gridFormat == IMPLICIT:
      forceFullCalculation = True
    else: forceFullCalculation = False
    
    #Export selected meshes
    print ("Export mesh: " + smeshBuilder.GetName(meshToExport))
    success = exportMesh.meshToPFLOTRAN(meshToExport, folder, outFormat, gridFormat, name, forceFullCalculation)
    #if not success: 
    #  print("Some error happen and the mesh have not been exported correctly...")
    #  return
    
    #retrieve submesh
    if groupsToExport:
      print ("%s group(s) to export: " %len(groupsToExport))    
      for (group,groupName) in groupsToExport:
        print(groupName)
        exportSubMesh.submeshToPFLOTRAN(group, groupName, folder, name, outFormat, gridFormat)
    else:
      print("There is no group to export")
    
    print(f"\nTotal runtime: {time.time() - start_time}\n")
    
    print ("    END \n")
    print ("####################\n\n")

  return
  

