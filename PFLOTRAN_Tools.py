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
  sys.path.append('/home/moise/Ecole/Doc/plugin SALOME/Salome-PFLOTRAN-Interface/')
  import importlib
  import exportMesh
  import exportSubMesh
  import UI_PFLOTRANTools
  importlib.reload(exportMesh)
  importlib.reload(exportSubMesh)
  importlib.reload(UI_PFLOTRANTools)
  from salome.gui import helper
  import SMESH
  print ("\n\n\n")
  print ("##################################\n")
  print (" Pflotran mesh converter for Salome 9.2.0 \n")
  print ("     By Moise Rousseau (2019)     \n")
  print ("  Export Salome meshes to Pflotran  \n")
  print ("###################################\n")
  
#  def GetFolder(path):
#    l = path.split('/')
#    path = ''
#    for i in range(0,len(l)-1):
#      path = path + l[i] + '/'
#    return path

  
  # get context study, studyId, salomeGui
  activeStudy = salome.myStudy

  #create folder for exportation
#  activeFolder = activeStudy._get_URL()
#  activeFolder = GetFolder(activeFolder)
#  print ("Mesh to be save in the folder " + activeFolder)

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
      fd = QFileDialog(self, "Select an output name", self.ui.le_origOutputFile.text(), "All Files (*)")
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
      
    def removeSubmesh(self):
      itemsSelected = self.ui.table_toExport.selectedItems()
      n = self.ui.table_toExport.rowCount()
      self.ui.table_toExport.setRowCount(n+len(itemsSelected))
      for i,x in enumerate(itemsSelected):
        group = self.availableSubmesh[x.text()]
        item = QTableWidgetItem()
        item.setText(group.GetName())
        self.ui.table_toExport.setItem(n+i,0, item)
        self.ui.table_toExport.setItem(n+i,1, QTableWidgetItem(group.GetName()))
        if group.GetTypes()[0] == SMESH.VOLUME:
          self.ui.table_toExport.setItem(n+i,2, QTableWidgetItem('VOLUME'))
        elif group.GetTypes()[0] == SMESH.FACE:
          self.ui.table_toExport.setItem(n+i,2, QTableWidgetItem('FACE'))
        else:
          pass
        self.selectedSubmesh.append(group)
      return
      
    def helpMessage(self):
      import subprocess
      subprocess.Popen(['firefox'], shell=False)
      return


  window = ExportDialog()
  window.exec_()
  result = window.result()
  
  return
  
  #Export selected meshes
  print ("Export selected mesh")
  exportMesh.meshToPFLOTRAN(meshToExport, activeFolder, outputFileFormat, outputMeshFormat, name)
  
  #retrieve submesh
  if exportSubmesh:
    smesh = salome.smesh.smeshBuilder.New()
    fatherMesh = smesh.Mesh(meshToExport.GetMesh())
    submeshToExport = []
    if fatherMesh.GetMeshOrder():
      submeshToExport = fatherMesh.GetMeshOrder()[0]
    for x in fatherMesh.GetGroups():
      submeshToExport.append(x)
    print ("%s submeshes in the corresponding mesh" %len(submeshToExport))    

    if submeshToExport:
      print("Running submesh exportation")
      for submesh in submeshToExport:
        submeshName = salome.smesh.smeshBuilder.GetName(submesh)
        exportSubMesh.submeshToPFLOTRAN(submesh, activeFolder, submeshName, name, outputFileFormat, outputMeshFormat)
  else:
    print("You choose not to export submeshes")
    
  if 0:   
   if unstructuredImplicit:
      if asciiOut:
        exportMesh.meshToPFLOTRANUntructuredASCII(meshToExport, activeFolder+name+'.ugi')
      if hdf5Out:
        exportMesh.meshToPFLOTRANUnstructuredHDF5(meshToExport, activeFolder+name+'.h5')
      print("Mesh exportation successful, go to submeshes now")
      
      if submeshToExport and exportSubmeshFlag:
        if asciiOut:
          print("Warning ! Ascii output not compatible with 3D region assigning, please consider HDF5 output.\n")
          for submesh in submeshToExport:
            submeshName = salome.smesh.smeshBuilder.GetName(submesh)
            print("  Exporting submesh %s to ASCII file: %s" %(submeshName, submeshName+'.ss'))
            submeshAsRegionASCII(submesh, activeFolder+submeshName+'.ss', submeshName)
        if hdf5Out:
          for submesh in submeshToExport:
            submeshName = salome.smesh.smeshBuilder.GetName(submesh)
            if submeshName == 'GrRock_Volumes' or submeshName == 'GrPit_Volumes':
              print("  Exporting submesh to .h5 file: %s" %submeshName)
              exportSubMesh.submeshAsRegionHDF5(submesh, activeFolder+name+'.h5', submeshName)
      else: 
        print("You choose not to export submeshes")
  
  print ("    END \n")
  print ("####################\n\n")

  return
  
  
salome_pluginsmanager.AddFunction('PFLOTRAN Tools GUI/Export mesh to PFLOTRAN_GUI_real',
                                  'Export mesh and submesh to PFLOTRAN readable format',
                                  PFLOTRANMeshExport)

