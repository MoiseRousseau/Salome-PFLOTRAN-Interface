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




def PFLOTRANMeshExport(context):
  from PyQt5 import QtCore
  import sys
  sys.path.insert(1,'/home/moise/Ecole/Doc/plugin SALOME/Salome-PFLOTRAN-Interface/')
  import importlib
  import exportMesh
  import exportSubMesh
  import UI_PFLOTRANTools
  importlib.reload(exportMesh)
  importlib.reload(exportSubMesh)
  importlib.reload(UI_PFLOTRANTools)
  from salome.gui import helper
  import SMESH


  class ExportDialog(QDialog):
    
    def __init__(self):
      QDialog.__init__(self)
      # Set up the user interface from Designer.
      #self.ui = EDZ_permeability_dataset_GUI.Ui_Dialog()
      self.ui = UI_PFLOTRANTools.Ui_Dialog()
      self.ui.setupUi(self)
      self.show()
      
      # Connect up the selectionChanged() event of the object browser.
      #sg.getObjectBrowser().selectionChanged.connect(self.select)
      self.selectMesh = False
      self.selectedMesh = None
      self.outputFile = '~/' #home bu default
      self.selectSubmesh = False
      self.availableSubmesh = {}
      self.selectedSubmesh = []
      self.binaryOutput = True #default
      self.format = True #implicit or false = explicit
      self.autocomplete = False
      
      # Connect up the buttons.
      self.ui.pb_origMeshFile.clicked.connect(self.setMeshInput)
      self.ui.pb_origOutputFile.clicked.connect(self.setOutputFile)
      self.ui.pb_help.clicked.connect(self.helpMessage)
      self.ui.cb_enableSubmesh.clicked.connect(self.enableSubmesh)
      self.ui.pb_addSubmesh.clicked.connect(self.addGroup)
      self.ui.pb_removeSubmesh.clicked.connect(self.removeGroup)
      #self.ui.pb_OutputFile.clicked.connect(self.setOutputFile)
      #self.ui.pb_help.clicked.connect(self.helpMessage)
      
      #self.select()
      
      return
      
      
    def select(self):
      #sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      objId = salome.sg.getSelected(0)
      if self.selectMesh:
        self._selectMeshInput(objId)
      return
      
    def _selectMeshInput(self, objId):
      self.selectedMesh = salome.IDToObject(objId)
      if isinstance(self.selectedMesh,salome.smesh.smeshBuilder.meshProxy):
        name = salome.smesh.smeshBuilder.GetName(self.selectedMesh)
        smesh = salome.smesh.smeshBuilder.New()
        self.selectedMesh = smesh.Mesh(self.selectedMesh)
        if not self.selectedMesh.GetElementsByType(SMESH.VOLUME):
          self.printErrorMessage('PFLOTRAN mesh need to 3-dimensional. Please select a 3D mesh. If you mesh is 1 or 2-dimensional, extrude it in the others direction with an unit length.')
          self.ui.le_origMeshFile.setText('')
          self.selectedMesh = None
          return
#      elif isinstance(self.selectedMesh,SMESH._objref_SMESH_Group):
#        name = salome.smesh.smeshBuilder.GetName(self.selectedMesh)
#      elif isinstance(self.selectedMesh,salome.smesh.smeshBuilder.submeshProxy):
#        name = salome.smesh.smeshBuilder.GetName(self.selectedMesh)
#      else:
#        return
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
      fd = QFileDialog(self, "Select an output name", self.ui.le_origOutputFile.text(), "PFLOTRAN HDF5 File (*.h5);;PFLOTRAN Implicit ASCII grid (*.ugi);;PFLOTRAN Explicit ASCII grid (*.uge);;All Files (*)")
      if fd.exec_():
        self.outputFile = fd.selectedFiles()[0]
        self.ui.le_origOutputFile.setText(self.outputFile)
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
      
    def helpMessage(self):
      import subprocess
      subprocess.Popen(['firefox'], shell=False)
      return
      
    def printErrorMessage(self, text):
      import qtsalome
      msg = qtsalome.QMessageBox()
      msg.setText(text)
      msg.setIcon(QMessageBox.Critical)
      msg.setStandardButtons(QMessageBox.Ok)
      msg.exec_()
      return


  window = ExportDialog()
  window.exec_()
  result = window.result()
  
  if result:
    print ("\n\n\n")
    print ("##########################################\n")
    print (" PFLOTRAN mesh converter for Salome 9.3.0 \n")
    print ("        By Moise Rousseau (2019)     \n")
    print ("    Export Salome meshes to PPFLOTRAN  \n")
    print ("##########################################\n")
    
    #retrieve data from the GUI
    meshToExport = window.selectedMesh #Mesh object
    name = window.outputFile.split('/')[-1]
    folder = window.outputFile[0:-len(name)]
    HDF5 = 1 ; ASCII = 2
    if window.ui.rb_outputFormat[0].isChecked(): 
      try:
        import h5py
        outFormat = HDF5
      except:
        window.printErrorMessage('h5py module not installed. You should install it before to export meshes in HDF5 format.')
        return
    else: outFormat = ASCII
    IMPLICIT = 1 ; EXPLICIT = 2
    if window.ui.rb_gridFormat[0].isChecked(): gridFormat = IMPLICIT
    else: gridFormat = EXPLICIT
    groupsToExport = []
    for row in range(window.ui.table_toExport.rowCount()):
      groupNameInSalome = window.ui.table_toExport.item(row,0).text()
      groupNameInOut = window.ui.table_toExport.item(row,1).text()
      if window.ui.table_toExport.item(row,2).text() == 'VOLUME':
        groupType = SMESH.VOLUME
      elif window.ui.table_toExport.item(row,2).text() == 'FACE':
        groupType = SMESH.FACE
      group = meshToExport.GetGroupByName(groupNameInSalome, groupType)
      if len(group) != 1:
        window.printErrorMessage('Two or more groups have the same name in Salome. Please assign different group name for each group to export')
      groupsToExport.append([group[0], groupNameInOut])
    
      
  #Export selected meshes
  print ("Export mesh: " + meshToExport.GetName())
  exportMesh.meshToPFLOTRAN(meshToExport, folder, outFormat, gridFormat, name)
  
  #retrieve submesh
  if groupsToExport:
    print ("%s group(s) to export: " %len(groupsToExport))    
    for (group,groupName) in groupsToExport:
      exportSubMesh.submeshToPFLOTRAN(group, folder, groupName, name, outFormat, gridFormat)
  else:
    print("There is no group to export")
  
  print ("    END \n")
  print ("####################\n\n")

  return
  
  
salome_pluginsmanager.AddFunction('PFLOTRAN Tools GUI/Export mesh to PFLOTRAN_GUI_real',
                                  'Export mesh and submesh to PFLOTRAN readable format',
                                  PFLOTRANMeshExport)

