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
# 2D region ASCII not working yet

import sys


def submeshToPFLOTRAN(submesh, submeshName, activeFolder, meshFile=None, outputFileFormat=0, outputMeshFormat=0):
  import SMESH
  import salome
  #Get mesh input type
  if (isinstance(submesh,SMESH._objref_SMESH_Group) or
      isinstance(submesh,SMESH._objref_SMESH_GroupOnGeom)):
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
        #surfaceSubmeshAsRegionHDF5(submesh, elementsList, maxElement, n_elements, PFlotranOutput, name=None)
        print('Exported as ' + activeFolder+submeshName+'.ss')
        surfaceSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.ss')
      elif outputFileFormat == 2: #ASCII
        surfaceSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.ss')
      return 
      
  elif outputMeshFormat == 2: #explicit
    if submeshType == SMESH.VOLUME and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        print("Non implemented yet") 
        return
      elif outputFileFormat == 2: #ASCII
        volumeSubmeshAsRegionASCII(submesh, elementsList, n_elements, activeFolder+submeshName+'.vs')
    elif submeshType == SMESH.FACE and fatherMeshType == SMESH.VOLUME:
      if outputFileFormat == 1: #HDF5
        print('Not implemented')
      elif outputFileFormat == 2: #ASCII
        surfaceSubmeshUnstructuredExplicit(submesh, elementsList, n_elements, activeFolder+submeshName+'.ex')
      return 
    
  return



def volumeSubmeshAsRegionASCII(submesh, elementsList, n_element, ASCIIOutput, name=None):
  from SMESH import VOLUME, FACE
   
  #open pflotran file
  out = open(ASCIIOutput, 'w')
  
  #grab element node list for each element and write it
  for x in elementsList:
    out.write(str(x)+'\n')
  out.close()
  return



def surfaceSubmeshAsRegionASCII(submesh, elementsList, n_element, ASCIIOutput, name=None):
  from SMESH import VOLUME, FACE
   
  #open pflotran file
  out = open(ASCIIOutput, 'w')
  
  #write number of element
  out.write(str(n_element)+'\n')
  
  #grab element node list for each element and write it
  for x in elementsList:
    NodesId = submesh.GetMesh().GetElemNodes(x)
    if len(NodesId) == 3: out.write('T ')
    elif len(NodesId) == 4: out.write('Q ')
    else: sys.exit("PFLOTRAN does not support >4 nodes element type for instance")
    for x in NodesId:
      out.write(str(x)+' ')
    out.write('\n')
  out.close()
  return
  


def surfaceSubmeshAsRegionHDF5(submesh, elementsList, maxElement, n_elements, PFlotranOutput, name=None):
  import SMESH
  import numpy as np
  import h5py
  
  #region name
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
    
  #open pflotran file
  out = h5py.File(PFlotranOutput, 'r+')
  
  #create region folder
  try:
    regionGroup = out['Regions']
  except:
    regionGroup = out.create_group('Regions')

  #create region
  submeshGroup = regionGroup.create_group(name)

  int_type = np.log(submesh.GetMesh().GetElementsByType(SMESH.VOLUME).index(maxElement)+1)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'

  print("Caution: PFLOTRAN function for importing 2D submesh as designed here not implemented yet.")
  print("You could export it as ASCII, which work")
  elementList = np.zeros(n_element, dtype=int_type)
  faceList = np.zeros(n_element, dtype='u1')
  
  count = 0
  for x in submesh.GetElementsId():
    NodesId = submesh.GetMesh().GetElemNodes(x)
    ElementId = submesh.GetMesh().GetElementsByNodes(NodesId, VOLUME)[0]
    pos = submesh.GetMesh().GetElementsByType(VOLUME).index(ElementId)
    elementList[count] = pos+1
    ElementNodes = out['Domain']['Cells'][(pos)].tolist()
    ElementNodes.pop(0)
    ElementNodes = [x for x in ElementNodes if x]
    faceList[count] = detFace(NodesId, ElementNodes)+1
    count += 1
    
  out.create_dataset('Regions/%s/Cell Ids' %(name), data=elementList)
  out.create_dataset('Regions/%s/Face Ids' %(name), data=faceList)
  
  out.close()
  return
 
 
  
def volumeSubmeshAsRegionHDF5(submesh, elementsList, maxElement, n_elements, PFlotranOutput, name=None):
  import SMESH
  import numpy as np
  import h5py
  import salome
  
  #region name
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
    
  #open pflotran file
  out = h5py.File(PFlotranOutput, 'r+')
  
  #create region folder
  try:
    regionGroup = out['Regions']
  except:
    regionGroup = out.create_group('Regions')

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




def surfaceSubmeshUnstructuredExplicit(submesh, corresp, folder, name=None):
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
    
  import salome
  out = open(name, 'w')
  try:
    IDList = submesh.GetElementsId()
  except:
    IDList = submesh.GetListOfID()
  out.write("CONNECTIONS {}\n".format(len(IDList)))
  
  smesh = salome.smesh.smeshBuilder.New()
  motherMeshType = submesh.GetMesh().GetTypes()[-1]
  motherMesh = smesh.Mesh(submesh.GetMesh()) #Mesh object
  
  for faceId in IDList:
    nodes = motherMesh.GetElemNodes(faceId)
    elementList = motherMesh.GetElementsByNodes(nodes, motherMeshType)
    out.write("{} ".format(corresp[elementList[0]]))
    center = motherMesh.BaryCenter(faceId)
    area = motherMesh.GetArea(faceId)
    for x in center:
      out.write("{} ".format(x))
    out.write("{}\n".format(area))
  
  out.close()
  return


    
def detFace(Nodes, ElementNodes):
  """
  Determine the face Id in PFLOTRAN formalism
  """
  #sort the node first
  Nodes.sort()

  if len(ElementNodes) == 4: #Tetrahedron
    possibleFace = ((0,1,3), (1,2,3), (0,2,3), (0,1,2))
  
  elif len(ElementNodes) == 5: #pyramid
    if len(Nodes) == 4:
      return 5
    possibleFace = ((0,1,4), (1,2,4), (2,3,4), (0,3,4))
  
  elif len(ElementNodes) == 6: #prism
    possibleFace = ((0,1,3,4), (1,2,4,5), (0,2,3,5), (0,1,2), (3,4,5))
  
  elif len(ElementNodes) == 8: #hexahedron
    possibleFace = ((0,1,4,5), (1,2,5,6), (2,3,6,7), (0,3,4,7), (0,1,2,3), (4,5,6,7))
  
  else:
    print("%s nodes element type not supported" %len(ElementNodes))
  
  for x in possibleFace:
    testFace = [ElementNodes[i] for i in x]
    testFace.sort()
    if testFace == Nodes:
      return possibleFace.index(x)
  print(Nodes)
  print(ElementNodes)
  print(possibleFace)
  print('Error occured, face not found !')
  sys.exit("Error occured, face not found !")


