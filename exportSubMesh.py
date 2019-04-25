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
# 2D element test
# parallelize code with multiprocessing ?

import sys


def determineType(mesh):
  from SMESH import VOLUME, FACE, EDGE
  if VOLUME in mesh.GetTypes():
    meshDim = 3
  elif FACE in mesh.GetTypes():
    meshDim = 2
  elif EDGE in mesh.GetTypes():
    meshDim = 1
  else:
    sys.exit("Impossible !")
  return meshDim


def submeshAsRegionASCII(submesh, ASCIIOutput, name=None):
  from SMESH import VOLUME, FACE
  
  if submesh.GetTypes()[0] == VOLUME:
    print("3D region not supported yet for ASCII region input")
    print("This submesh will be ignored")
    return
   
  #open pflotran file
  out = open(ASCIIOutput, 'w')
  
  #write number of element
  n_element = submesh.GetNumberOfElements()
  out.write(str(n_element)+'\n')
  
  #grab element node list for each element and write it
  for x in submesh.GetElementsId():
      NodesId = submesh.GetMesh().GetElemNodes(x)
      if len(NodesId) == 3: out.write('T ')
      elif len(NodesId) == 4: out.write('Q ')
      else: sys.exit("PFLOTRAN does not support >4 nodes element type")
      #TODO: check RHD here ??
      for x in NodesId:
        out.write(str(x)+' ')
      out.write('\n')
  out.close()
  return
    
  
def submeshAsRegionHDF5(submesh, PFlotranOutput, name=None):
  from SMESH import VOLUME, FACE, EDGE
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
  #cellIds = submeshGroup.create_group('Cell Ids')
  
  #initiate 2D/3D region element type
  n_element = submesh.GetNumberOfElements()
  maxElement = max(submesh.GetMesh().GetElementsId())
  int_type = np.log(submesh.GetMesh().GetElementsByType(VOLUME).index(maxElement)+1)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  
  if submesh.GetTypes()[0] == VOLUME:
    #father is a VOLUME mesh
    elementList = np.zeros(n_element, dtype=int_type)
    count = 0
    for x in submesh.GetElementsId():
      elementList[count] = submesh.GetMesh().GetElementsByType(VOLUME).index(x)+1
      count += 1
    out.create_dataset('Regions/%s/Cell Ids' %name, data=elementList)
    
  elif submesh.GetTypes()[0] == FACE:
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
  
  else:
    #3D father and 1D element
    #n_element = len(submesh.GetMesh().GetElementsByType(EDGE))
    #elementsArray = np.zeros((n_elements,3), dtype=int_type)
    print('1D element not supported. The submesh %s will be ignored' %name)
    
  out.close()
  return



def submeshToPFLOTRANUnstructuredExplicit(submesh, corresp, folder, name=None):
  if not name:
    name = salome.smesh.smeshBuilder.GetName(submesh)
    
  motherMesh = submesh.GetMesh() #meshProxy object
  motherMeshType = determineType(motherMesh)
  submeshType = determineType(submesh)
  
  if submeshType == motherMeshType:
    HDF5File = motherMesh.GetName() + '.h5'
    submeshToHDF5SameDimension(submesh, folder + HDF5File, name)
  elif submeshType == motherMeshType - 1:
   submeshToASCIIDimensionMinus1IExplicit(submesh, corresp, folder+name+'.ex')
  return

def submeshToPFLOTRANUnstructuredImpplicit():
  return


def submeshToHDF5SameDimension():
  return
  
def submeshToHDF5DimensionMinus1Implicit():
  return
 
 
def submeshToASCIISameDimension():
  print("3D region not supported yet for ASCII region input")
  print("This submesh will be ignored")
  return
  
def submeshToASCIIDimensionMinus1Implicit():
  return
  
  
  
def submeshToASCIIDimensionMinus1IExplicit(submesh, corresp, name):
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


