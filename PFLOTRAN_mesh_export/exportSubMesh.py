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



import SMESH
import numpy as np
import salome
try:
  import h5py
except:
  pass


def submeshToPFLOTRAN(submesh, submeshName, activeFolder, meshFile=None, outputFileFormat=0, outputMeshFormat=0):
  #Get mesh input type
  if (isinstance(submesh,SMESH._objref_SMESH_Group) or
      isinstance(submesh,SMESH._objref_SMESH_GroupOnGeom) or
      isinstance(submesh,SMESH._objref_SMESH_GroupOnFilter)):
    elementsList = iter(submesh.GetIDs())
    n_elements = len(submesh.GetIDs())
    maxElement = max(submesh.GetIDs())
  #elif isinstance(submesh,salome.smesh.smeshBuilder.submeshProxy):
  #  elementsList = iter(submesh.GetElementsId())
  #  n_elements = submesh.GetNumberOfElements()
  #  maxElement = max(submesh.GetMesh().GetElementsId())
    
  #submesh and father mesh type
  submeshType = submesh.GetTypes()[0]
  fatherMesh = submesh.GetMesh() #meshProxy object
  if SMESH.VOLUME in fatherMesh.GetTypes():
    fatherMeshType = SMESH.VOLUME
  #elif SMESH.FACE in fatherMesh.GetTypes():
  #  fatherMeshType = SMESH.FACE
  else:
    raise RuntimeError('Father mesh not VOLUME, STOP')
    
    
  if outputMeshFormat == 1: #implicit
    if submeshType == SMESH.VOLUME and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        volumeSubmeshAsRegionHDF5(submesh, elementsList, maxElement, n_elements,  activeFolder + meshFile, name=None)
      elif outputFileFormat == 2: #ASCII
        volumeSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.vs')
    elif submeshType == SMESH.FACE and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        surfaceSubmeshAsRegionHDF5(submesh, elementsList, n_elements, 
                                   activeFolder+meshFile, submeshName)
        #print('Exported as ' + activeFolder+submeshName+'.ss')
        #surfaceSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.ss')
      elif outputFileFormat == 2: #ASCII
        surfaceSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.ss')
      return 
      
  elif outputMeshFormat == 2: #explicit
    if submeshType == SMESH.VOLUME and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        print("Non implemented yet") 
        volumeSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.vs')
      elif outputFileFormat == 2: #ASCII
        volumeSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.vs')
    elif submeshType == SMESH.FACE and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        print('Not implemented')
        surfaceSubmeshUnstructuredExplicit(submesh, elementsList, n_elements,  activeFolder+submeshName+'.ex')
      elif outputFileFormat == 2: #ASCII
        surfaceSubmeshUnstructuredExplicit(submesh, elementsList, n_elements,  activeFolder+submeshName+'.ex')
      return 
    
  return



def volumeSubmeshAsRegionASCII(submesh, elementsList, n_element, ASCIIOutput, name=None):
  #open pflotran file
  out = open(ASCIIOutput, 'w')
  
  #We need correspondance between mesh element in salome and in HDF5
  fatherMeshCells = submesh.GetMesh().GetElementsByType(SMESH.VOLUME)
  d = {fatherMeshCells[i]: i+1 for i in range(len(fatherMeshCells))}
  
  #grab element node list for each element and write it
  for x in elementsList:
    out.write(str(d[x])+'\n')
  out.close()
  return



def surfaceSubmeshAsRegionASCII(submesh, elementsList, n_element, ASCIIOutput, name=None):
  #open pflotran file
  out = open(ASCIIOutput, 'w')
  
  #write number of element
  out.write(str(n_element)+'\n')
  
  #grab element node list for each element and write it
  for x in elementsList:
    NodesId = submesh.GetMesh().GetElemNodes(x)
    if len(NodesId) == 3: out.write('T ')
    elif len(NodesId) == 4: out.write('Q ')
    else: 
      print("Implicit grid type does not support face element with more than 4 nodes.")
      print("You may try the explicit format mesh export.")
      return
    for x in NodesId:
      out.write(str(x)+' ')
    out.write('\n')
  out.close()
  return


def surfaceSubmeshAsRegionHDF5(submesh, elementsList, n_element, h5_output, name=None):
  #open pflotran file
  out = h5py.File(h5_output, 'r+')
  
  #size the array
  nodesArray = np.zeros((n_element,5), dtype="u8")
    
  #populate array
  for i,x in enumerate(elementsList):
    nodesId = submesh.GetMesh().GetElemNodes(x)
    if len(nodesId) == 3: nodesArray[i][0] = 3
    elif len(nodesId) == 4: nodesArray[i][0] = 4
    else:
      print("Implicit grid type does not support face element with more than 4 nodes.")
      print("You may try the explicit format mesh export.")
      return
    for j,nodeId in enumerate(nodesId):
      nodesArray[i][j+1] = nodeId
  
  #output it
  if "Regions" not in list(out.keys()): out.create_group('Regions')
  out.create_dataset(f"Regions/{name}/Vertex Ids", data=nodesArray)
  out.close()
  return
  
 
  
def volumeSubmeshAsRegionHDF5(submesh, elementsList, maxElement, n_elements, PFlotranOutput, name=None):
  
  #region name
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
    
  #open pflotran file
  out = h5py.File(PFlotranOutput, 'r+')
  try:
    regionGroup = out["Regions"]
  except:
    regionGroup = out.create_group("Regions")
  
  #create region
  submeshGroup = regionGroup.create_group(name)

  int_type = np.log(submesh.GetMesh().GetElementsByType(SMESH.VOLUME).index(maxElement)+1)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'

  #export the submesh
  elementData = np.zeros(n_elements, dtype=int_type)
  fatherMeshCells = submesh.GetMesh().GetElementsByType(SMESH.VOLUME)
  #We need correspondance between mesh element in salome and in HDF5
  d = {fatherMeshCells[i]: i+1 for i in range(len(fatherMeshCells))}
  count = 0
  for x in elementsList:
    elementData[count] = d[x]
    count += 1
    
  out.create_dataset('Regions/%s/Cell Ids' %name, data=elementData)

  out.close()
  return




def surfaceSubmeshUnstructuredExplicit(submesh, elementList, n_elements, name=None):
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
  
  out = open(name, 'w')
  out.write("CONNECTIONS {}\n".format(n_elements))
  
  smesh = salome.smesh.smeshBuilder.New()
  fatherMesh = smesh.Mesh(submesh.GetMesh()) #Mesh object
  fatherMeshCells = fatherMesh.GetElementsByType(SMESH.VOLUME)
  #We need correspondance between mesh element in salome and in HDF5
  d = {fatherMeshCells[i]: i+1 for i in range(len(fatherMeshCells))}
  
  for faceId in elementList:
    nodes = fatherMesh.GetElemNodes(faceId)
    element = fatherMesh.GetElementsByNodes(nodes, SMESH.VOLUME)[0]
    out.write("{} ".format(d[element]))
    center = fatherMesh.BaryCenter(faceId)
    area = fatherMesh.GetArea(faceId)
    for x in center:
      out.write("{} ".format(x))
    out.write("{}\n".format(area))
  
  out.close()
  return



