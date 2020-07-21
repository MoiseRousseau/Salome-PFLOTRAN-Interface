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



import EDZ_permeability_dataset_GUI
import importlib
import EDZFN_class
#importlib.reload(EDZ_permeability_dataset_GUI)

import salome
from salome.smesh import smeshBuilder
from qtsalome import QDialog, QFileDialog
import SMESH
import GEOM

import h5py
import time
import common
import numpy as np



#Salome function
def computeNodePositionFromSurface(mesh, surface, elementNumber, point, geompy):
  #element position
  X,Y,Z = mesh.BaryCenter(elementNumber)
  #translate geom point
  X_p, Y_p, Z_p = geompy.PointCoordinates(point)
  point = geompy.TranslateDXDYDZ(point, X-X_p, Y-Y_p, Z-Z_p)
  #get distance and vector
  [distance, DX, DY, DZ] = geompy.MinDistanceComponents(point, surface)
  #angle
  normal = [DX,DY,DZ]
  return [distance, normal]
  


def createDistanceAndNormalDataset(mesh, surface, output):
  
  smesh = salome.smesh.smeshBuilder.New()
  fatherMesh = mesh.GetMesh()
  
  fatherCells = fatherMesh.GetElementsByType(SMESH.VOLUME)
  fatherCellNumber = len(fatherMesh.GetElementsByType(SMESH.VOLUME))
  if isinstance(mesh,salome.smesh.smeshBuilder.meshProxy):
    cellsToExport = set(fatherMesh.GetElementsByType(SMESH.VOLUME))
  if (isinstance(mesh,SMESH._objref_SMESH_Group) or
      isinstance(mesh,SMESH._objref_SMESH_GroupOnGeom) or
      isinstance(mesh,SMESH._objref_SMESH_GroupOnFilter)):
    cellsToExport = set(mesh.GetIDs())
  cellNumber = len(cellsToExport)
  
  #init groups
  int_type = np.log(cellNumber)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  cellIds = np.zeros(fatherCellNumber, dtype=int_type)
  D = np.zeros(fatherCellNumber, dtype='f8')
  normal = np.zeros((fatherCellNumber,3), dtype='f8')
  
  geompy = salome.geom.geomBuilder.New()
  point = geompy.MakeVertex(0, 0, 0)
  for count, cellId in enumerate(fatherCells):
    if cellId in cellsToExport:
      #print progression
      common.progress_bar(count, cellNumber, barLength=50)
      #compute distance and normal
      D[count], normal[count] = computeNodePositionFromSurface(fatherMesh, surface, cellId, point, geompy)
    else:
      D[count] = -1
    cellIds[count] = count+1
    count += 1
     
  #writeoutput
  out = h5py.File(output, mode='w')
  out.create_dataset('Cell Ids', data=cellIds)
  out.create_dataset('Distance', data=D)
  out.create_dataset('Normal', data=normal)
  out.close()
  
  print('\n')
  
  return
  
  
def computePermeabilityDataset(output, EDZClass, name, new_h5_file_name=''):
  src = h5py.File(output, mode='r+')
  distance = np.array(src["Distance"])
  normal = np.array(src["Normal"]) 
  cellNumber = len(distance)
  if new_h5_file_name:
    out = h5py.File(new_h5_file_name,'w')
    out.create_dataset('Cell Ids', data = src['Cell Ids'])
  else:
    out = src
  
  if EDZClass.getAnisotropy(): #anisotropic EDZ
    K = EDZClass.computePermeability(distance, normal)
    groupsName = ('X','XY','XZ','Y','YZ','Z')
    for Ki in K:
      out.create_dataset(name +groupsName[i], data=K[i])
      
  else:
    K = EDZClass.computePermeability(distance, normal)[0]
    out.create_dataset(name + '_ISO', data=K)
    
  src.close()
  return





def EDZPermeabilityDataset(context):
  
  importlib.reload(EDZ_permeability_dataset_GUI)
  importlib.reload(EDZFN_class)
  sg = context.sg
  smesh = smeshBuilder.New()
  
  class EDZDialog(QDialog):
    def __init__(self):
      QDialog.__init__(self)
      # Set up the user interface from Designer.
      self.ui = EDZ_permeability_dataset_GUI.Ui_Dialog()
      self.ui.setupUi(self)
      self.show()
      
      # Connect up the selectionChanged() event of the object browser.
      #sg.getObjectBrowser().selectionChanged.connect(self.select)
      self.selectMesh = False
      self.selectSurface = False
      self.enableAnisoBool = False
      self.mesh = None
      self.surface = None
      self.outputFile = None
      
      # Connect up the buttons.
      self.ui.pb_origMeshFile.clicked.connect(self.setMeshInput)
      self.ui.pb_origSurfaceFile.clicked.connect(self.setSurfaceInput)
      self.ui.pb_origOutputFile.clicked.connect(self.setOutputFile)
      self.ui.pb_help.clicked.connect(self.helpMessage)
      self.ui.cb_enable.clicked.connect(self.enableAnisotropy)
      #self.ui.pb_OutputFile.clicked.connect(self.setOutputFile)
      #self.ui.pb_help.clicked.connect(self.helpMessage)
      
      #self.select()
      
      return
      
      
    def select(self):
      #sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      objId = salome.sg.getSelected(0)
      if self.selectMesh:
        self._selectMeshInput(objId)
      elif self.selectSurface:
        self._selectSurfaceInput( objId)
      return
      
      
    def _selectMeshInput(self, objId):
      self.mesh = salome.IDToObject(objId)
      if isinstance(self.mesh,salome.smesh.smeshBuilder.meshProxy):
        name = salome.smesh.smeshBuilder.GetName(self.mesh)
      elif (isinstance(self.mesh,SMESH._objref_SMESH_Group) or
           isinstance(self.mesh,SMESH._objref_SMESH_GroupOnGeom) or
           isinstance(self.mesh,SMESH._objref_SMESH_GroupOnFilter)):
        name = salome.smesh.smeshBuilder.GetName(self.mesh)
      #elif isinstance(self.mesh,salome.smesh.smeshBuilder.submeshProxy):
      #  name = salome.smesh.smeshBuilder.GetName(self.mesh)
      else:
        return
      self.ui.le_origMeshFile.setText(name)
      return
      
      
    def _selectSurfaceInput(self, objId):
      self.surface = salome.IDToObject(objId)
      if isinstance(self.surface,GEOM._objref_GEOM_Object):
        name = salome.smesh.smeshBuilder.GetName(self.surface)
      else:
        return
      self.ui.le_origSurfaceFile.setText(name)
      return
      
    
    def setMeshInput(self):
      if self.selectMesh == True:
        self.selectMesh = False
        sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      else:
        self.selectSurface = False
        self.ui.pb_origSurfaceFile.setChecked(False)
        self.selectMesh = True
        sg.getObjectBrowser().selectionChanged.connect(self.select)
        self.select()
      return
      
      
    def setSurfaceInput(self):
      if self.selectSurface == True:
        self.selectSurface = False
        sg.getObjectBrowser().selectionChanged.disconnect(self.select)
      else:
        self.selectMesh = False
        self.ui.pb_origMeshFile.setChecked(False)
        self.selectSurface = True
        sg.getObjectBrowser().selectionChanged.connect(self.select)
        self.select()
      return
        
      
    def setOutputFile(self):
      fd = QFileDialog(self, "select an output h5 file", self.ui.le_origOutputFile.text(), "PFLOTRAN h5 File (*.h5);;All Files (*)")
      if fd.exec_():
        self.outputFile = fd.selectedFiles()[0]
        if not self.outputFile[-3:] == '.h5':
          self.outputFile += '.h5'
        self.ui.le_origOutputFile.setText(self.outputFile)
      return
      
      
    def enableAnisotropy(self):
      self.ui.le_anisoFactor.setReadOnly(not self.ui.cb_enable.isChecked())
      self.enableAnisoBool = self.ui.cb_enable.isChecked()
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


      
  window = EDZDialog()
  window.exec_()
  result = window.result()
  #compute perm here
  if result:
    #density distance law
    try:
      traceLength = float(window.ui.le_traceLength.text())
    except:
      window.printErrorMessage("invalid trace length input")
    try:
      attenuationLength = float(window.ui.le_attenuationLength.text())
    except:
      window.printErrorMessage("invalid attenuation length input")
    #fracture properties
    try:
      radius = float(window.ui.le_radius.text())
    except:
      window.printErrorMessage("invalid fracture radius input")
    try:
      aperture = float(window.ui.le_aperture.text())
    except:
      window.printErrorMessage("invalid fracture aperture input")
    #anisotropy
    if window.enableAnisoBool:
      try: anisoFactor = float(window.ui.le_anisoFactor.text())
      except: window.printErrorMessage("invalid anisotropic factor input")
    if window.ui.choice[0].isChecked():
      model = "MOURZENCKO_EDZ"
    elif window.ui.choice[1].isChecked():
      model = "SNOW"
    else: model = None
    #matrix properties
    if window.ui.rb_coupling[0].isChecked():
      matrixCoupling = False
    elif window.ui.rb_coupling[1].isChecked():
      matrixCoupling = True
    try:
      matrixPerm = float(window.ui.le_matrixPerm.text())
    except:
      window.printErrorMessage("invalid matrix permeability input")
    #if window.ui.cb_doNotComputeDistAndNormal.isChecked():
      
    mesh = window.mesh
    surface = window.surface
    output = window.outputFile
    #print(mesh, surface, output, model, anisoFactor, radius, aperture, attenuationLength, matrixCoupling, matrixPerm)
    
    #EDZ properties
    EDZClass = EDZFN_class.EDZFractureNetwork()
    EDZClass.setEDZModel(model)
    if window.enableAnisoBool: EDZClass.setAnisotropy(anisoFactor)
    EDZClass.setFractureProperties(radius,aperture)
    EDZClass.setAttenuationLength(attenuationLength)
    EDZClass.setMatrixPermeability(matrixPerm)
    EDZClass.setMatrixCoupling(matrixCoupling)
    #compute initial density from traceLength
    initialDensity = EDZClass.computeInitialDensityFromTraceLength(traceLength)
    EDZClass.setInitialDensity(initialDensity)
    EDZClass.printReducedParameter()
    
    #create normal and distance dataset
    print("Create distance to surface and normal dataset")
    tt=time.time()
    createDistanceAndNormalDataset(mesh, surface, output)
    print ("Total time to compute geometrical information: {} seconds".format(time.time()-tt))
    
    #compute perm dataset
    print("Compute permeability from the previous datasets")
    tt=time.time()
    computePermeabilityDataset(output, EDZClass, "Perm")

  return

