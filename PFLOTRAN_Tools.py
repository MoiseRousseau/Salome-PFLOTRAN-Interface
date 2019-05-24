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



def PFLOTRANMeshExport(context):
  import importlib
  import exportMesh
  import exportSubMesh
  importlib.reload(exportMesh)
  importlib.reload(exportSubMesh)
  from salome.gui import helper
  print ("\n\n\n")
  print ("##################################\n")
  print (" Pflotran mesh converter for Salome 9.2.0 \n")
  print ("     By Moise Rousseau (2019)     \n")
  print ("  Export Salome meshes to Pflotran  \n")
  print ("###################################\n")
  
  def GetFolder(path):
    l = path.split('/')
    path = ''
    for i in range(0,len(l)-1):
      path = path + l[i] + '/'
    return path

  
  # get context study, studyId, salomeGui
  activeStudy = salome.myStudy

  #create folder for exportation
  activeFolder = activeStudy._get_URL()
  activeFolder = GetFolder(activeFolder)
  print ("Mesh to be save in the folder " + activeFolder)
  
  #Option selection
  outputFileFormat = 2 #1:ASCII or 2:HDF5
  outputMeshFormat = 1 #1:Implicit or 2:Explicit
  exportSubmesh = True
  
  #Export selected meshes
  print ("Export selected mesh")
  meshToExport = helper.getSObjectSelected()[0].GetObject()
  name = None #for future implementation of name chosen by user
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
  
  
salome_pluginsmanager.AddFunction('PFLOTRAN Tools GUI/Export mesh to PFLOTRAN_GUI',
                                  'Export mesh and submesh to PFLOTRAN readable format',
                                  PFLOTRANMeshExport)

