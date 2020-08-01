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



import sys
import salome
import SMESH
import numpy as np
import h5py
import gc
import common
import depreciated
import importlib
#importlib.reload(common)


#TODO: add support for polyhedral format
# CELLS number_of_cells
# id nb_face nb_vertices center_coordinate volume
# FACES number_of_faces
# id cell_which_get_the_face number_of_point point_not_ordered face_center_coordinate area
# VERTICES number_of_points
# coordinates



def meshToPFLOTRAN(meshToExport, activeFolder, outputFileFormat, outputMeshFormat, name=None, fullCalculation = False):
  
  n_nodes = meshToExport.NbNodes()
  n_elements = len(meshToExport.GetElementsByType(SMESH.VOLUME))
  nodesList = iter(range(1,n_nodes+1))
  elementsList = iter(meshToExport.GetElementsByType(SMESH.VOLUME))
  success = 0
  
  PFlotranOutput = activeFolder + name
  if outputFileFormat == 2: #ASCII
    if outputMeshFormat == 1: #Implicit
      success = meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput, fullCalculation)
    elif outputMeshFormat == 2: #Explicit
      meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput)
      success = meshToPFLOTRANUnstructuredExplicitASCII(meshToExport, PFlotranOutput)
      
  elif outputFileFormat == 1: #HDF5
    if outputMeshFormat == 1: #Implicit
      success = meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput, fullCalculation)
    elif outputMeshFormat == 2: #Explicit
      raise RuntimeError('Explicit HDF5 exportation not implemented in PFLOTRAN')
    
  return success
  
  


def salomeToPFLOTRANNodeOrder(elementNumber, mesh):
  nodes = mesh.GetElemNodes(elementNumber)
  elemType = mesh.GetElementGeomType(elementNumber)
  if elemType == SMESH.Entity_Tetra: #tetrahedron
    nodes = [nodes[1],  nodes[0], nodes[2], nodes[3]]
  elif elemType == SMESH.Entity_Pyramid: #pyramid
    nodes = [nodes[0],  nodes[3], nodes[2], nodes[1], nodes[4]]
  elif elemType == SMESH.Entity_Penta: #prism
    nodes = [nodes[1],  nodes[0], nodes[2], nodes[4], nodes[3], nodes[5]]
  elif elemType == SMESH.Entity_Hexa: #hexa
    nodes = [nodes[0],  nodes[3], nodes[2], nodes[1], nodes[4],  nodes[7], nodes[6], nodes[5]]
  elif elemType == SMESH.Entity_Polyhedra: #polyhedra
    print("Implicit grid does not support polyhedral mesh, but explicit does. Please switch to explicit format.")
    return []
  else:
    print("Warning: node order for given type {} not supported".format(elemType))
    print("I need to add quadratic elem type")
    return []
  return nodes
  



def meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput, fullCalculation):
   
  #open pflotran file
  out = open(PFlotranOutput, 'w')
 
  #initiate 3D element type
  elementCode = {4:'T', 5:'P', 6:'W', 8:'H'}
  
  #pflotran line 1
  out.write(str(n_elements) + ' ' + str(n_nodes) + '\n')

  #pflotran line 2 to n_element_3D +1
  for i in elementsList:
    
    if fullCalculation:
      elementNode = depreciated.OrderNodes(i, meshToExport)
    else: elementNode = salomeToPFLOTRANNodeOrder(i, meshToExport)
    if not elementNode: return 0 #fail
    
    out.write(elementCode[len(elementNode)] + ' ')
    
    for x in elementNode: #write
      out.write(str(x) + ' ')
    out.write('\n')
  
  #pflotran line n_element+1 to end
  #write node coordinates
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    out.write(str(X) + ' ' + str(Y) + ' ' + str(Z) + '\n')
  
  out.close()
  return 1 #success
    
    

def meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput, fullCalculation):
  
  #open pflotran output file
  out = h5py.File(PFlotranOutput, mode='w')
    
  #initialise array
  #integer length
  int_type = np.log(n_nodes)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  
  #only linear element
  if meshToExport.GetMeshInfo()[SMESH.Entity_Hexa]: #hexa
    elementsArray = np.zeros((n_elements,9), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Penta]: #prisms
    elementsArray = np.zeros((n_elements,7), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Pyramid]: #pyr
    elementsArray = np.zeros((n_elements,6), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Tetra]: #tetra
    elementsArray = np.zeros((n_elements,5), dtype=int_type)
  #elif meshToExport.GetMeshInfo()[4]: #tri
  #  elementsArray = np.zeros((n_elements,4), dtype=int_type)
  else:
    raise RuntimeError('No linear element of dimension 3 found.')
  
  #hdf5 element
  count = 0
  print('Creating Domain/Cells dataset:')
  for i in elementsList:
    common.progress_bar(count, n_elements, barLength=50)
    if fullCalculation:
      elementNode = depreciated.OrderNodes(i, meshToExport)
    else: elementNode = salomeToPFLOTRANNodeOrder(i, meshToExport)
    if not elementNode: return 0 #fail
    elementsArray[count,0] = len(elementNode)
    for j in range(len(elementNode)):
      elementsArray[count,j+1] = elementNode[j]
    count += 1

  out.create_dataset('Domain/Cells', data=elementsArray)
  del elementsArray
  gc.collect()
  
  
  #hdf5 node coordinates
  print('\nCreating Domain/Vertices dataset: ')
  vertexArray = np.zeros((n_nodes, 3), dtype='f8')
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    vertexArray[i-1,0] = X
    vertexArray[i-1,1] = Y
    vertexArray[i-1,2] = Z
  out.create_dataset('Domain/Vertices', data=vertexArray)
  del vertexArray
  gc.collect()
  
  out.close()
  return 1 #success



def meshToPFLOTRANUnstructuredExplicitASCII(mesh, PFlotranOutput, center0DElem=True):

  print("Note: We use Qhull to compute the element volume since Salome has a error (https://salome-platform.org/forum/forum_10/547695356/view). We build first the convex hull and then get the volume. Thus, for non convex polyhedra, the exported volume will be false. The Salome error should be corrected on its next release.\n")
  
  #open pflotran output file
  out = open(PFlotranOutput, mode='w')

  #CELLS part
  print("Write cell ids, center and volume")
  n_elements = len(mesh.GetElementsByType(SMESH.VOLUME))
  out.write("CELLS %s\n" %n_elements)
  count = 1
  corresp = {}
  if center0DElem:
    elem0Ds = mesh.GetElementsByType(SMESH.ELEM0D)
    if not len(elem0Ds): center0DElem = False
    
  center0DElem = False
  for count_center,i in enumerate(mesh.GetElementsByType(SMESH.VOLUME)):
    #get info (center and volume)
    if center0DElem:
      node = mesh.GetElemNodes(elem0Ds[count_center])[0]
      center = mesh.GetNodeXYZ(node)
    else:
      center = mesh.BaryCenter(i)
    volume = mesh.GetVolume(i)
    #volume = common.computeVolumeFromNodeList(mesh.GetElemNodes(i),mesh)
    #write info
    out.write("%s " %int(count))
    for x in center:
      out.write("%s " %x)
    out.write("%s\n" %volume)
    corresp[i]=count
    count += 1
    
  #CONNECTIONS part
  print("Build connections between cells")
  sharedFaceDict = {}
  faceArea = {}
  faceCenter = {}
  volIDs = mesh.GetElementsByType( SMESH.VOLUME )
  count_bar = 0
  n_elements = len(volIDs)
  for v in volIDs:
    count_bar += 1
    if not count_bar % 100:
      common.progress_bar(count_bar, n_elements, barLength=50)
    nbF = mesh.ElemNbFaces( v )
    for f in range(0,nbF):
      vFNodes = mesh.GetElemFaceNodes( v, f )
      dictKey = tuple(sorted(vFNodes))
      if dictKey not in sharedFaceDict:
        sharedFaceDict[ dictKey ] = [ v ]
      else:
        sharedFaceDict[ dictKey ].append( v )
        faceArea[tuple(sharedFaceDict[ dictKey ])] = common.computeAreaFromNodeList(vFNodes,mesh)
        faceCenter[tuple(sharedFaceDict[ dictKey ])] = common.computeCenterFromNodeList(vFNodes,mesh)
  
  print('\nWrite connections')
  num_connection = 0
  for v in sharedFaceDict.values():
    if len(v) == 2: num_connection += 1
  out.write("CONNECTIONS {}\n".format(num_connection)) 
       
  for f,v in sharedFaceDict.items():
    if len(v) == 2:
      area = faceArea[tuple(v)]
      center = faceCenter[tuple(v)]
      out.write(str(corresp[v[0]])+ ' ' + str(corresp[v[1]]) + ' ')
      for x in center: out.write(str(x) + ' ')
      out.write(str(area) + '\n')
   
  out.close()

  return 1



def meshToPFLOTRANUnstructuredExplicitHDF5(mesh, PFlotranOutput):
  raise RuntimeError('HDF5 unstructureed explicit seems not to be implemented in PFLOTRAN')
  return
  


def meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFLOTRANOutput):
  print("Create XDMF file for visualisation")
  
  prefix = PFLOTRANOutput.split('.')[:-1]
  PFLOTRANOutput = ''
  for x in prefix:
    PFLOTRANOutput += x
  PFLOTRANOutput += "_Domain.h5"
  
  #open pflotran output file
  out = h5py.File(PFLOTRANOutput, mode='w')
  
  #hdf5 node coordinates
  print('Creating Domain/Vertices dataset')
  vertexArray = np.zeros((n_nodes, 3), dtype='f8')
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    vertexArray[i-1,0] = X
    vertexArray[i-1,1] = Y
    vertexArray[i-1,2] = Z
  out.create_dataset('Domain/Vertices', data=vertexArray)
  
  #HDF5 cells
  #initialise array
  #integer length
  print('Creating Domain/Cells dataset\n')
  int_type = np.log(n_nodes)/np.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  
  temp_list = []

  for c in elementsList:
    temp_list.append(16) #we say it is a polyhedron
    nbF = meshToExport.ElemNbFaces( c )
    temp_list.append(nbF) #write number of face 
    for f in range(0,nbF):
      vFNodes = meshToExport.GetElemFaceNodes( c, f )
      temp_list.append(len(vFNodes)) #write face length
      temp_list.extend([x-1 for x in vFNodes])
        
  out.create_dataset('Domain/Cells', data=np.array(temp_list, dtype=int_type))
  
  #store number of cells
  out.create_dataset('Domain/Cell_number', data=np.array([n_elements], dtype=int_type))
  
  out.close()
  
  return 1
  
  
  

  


