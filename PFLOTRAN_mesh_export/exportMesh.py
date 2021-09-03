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
import gc
import common
import depreciated
import importlib
importlib.reload(common)

try:
  import h5py
except:
  pass


#########
# UTILS #
#########
    
def salomeToPFLOTRANNodeOrder(elementNumber, mesh):
  """
  Convert element node list from Salome to PFLOTRAN order
  """
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
  

def buildInternalFaces(mesh, project_area=False):
  #project_area = True #uncomment to compute projected instead of true area
  sharedFaceDict = {}
  volIDs = mesh.GetElementsByType( SMESH.VOLUME )
  count_bar = 0
  n_elements = len(volIDs)
  faceArea = {}
  faceCenter = {}
  faceNormal = {}
  n_faces = 0
  for v in volIDs:
    count_bar += 1
    if not count_bar % 100:
      common.progress_bar(count_bar, n_elements, barLength=50)
    nbF = mesh.ElemNbFaces( v )
    for f in range(0,nbF):
      vFNodes = mesh.GetElemFaceNodes( v, f )
      dictKey = tuple(sorted(vFNodes))
      b = False
      try:
        sharedFaceDict[ dictKey ].append( v )
        b = True
      except:
        sharedFaceDict[ dictKey ] = [ v ]
      if b:
        b = False
        n_faces += 1
        area = common.computeAreaFromNodeList(vFNodes,mesh)
        faceCenter[ dictKey ] = common.computeCenterFromNodeList(vFNodes,mesh)
        normal = common.getNormalFromNodeList(vFNodes, mesh)
        faceNormal[dictKey] = normal
        if project_area:
          cellCenterVector = common.computeCellCenterVectorFromCellIds(
                                                sharedFaceDict[ dictKey ], mesh)
          cellCenterVector /= np.linalg.norm(cellCenterVector)
          faceArea[ dictKey ] = area * np.dot(normal, cellCenterVector)
        else:
          faceArea[ dictKey ] = area
  return n_faces, sharedFaceDict, faceArea, faceCenter, faceNormal





###################
### MAIN DRIVER ###
###################

def meshToPFLOTRAN(meshToExport, activeFolder, outputFileFormat, outputMeshFormat, name=None, compressH5Output = False, fullCalculation=False):
  """
  Main driver for Salome to PFLOTRAN mesh conversion
  """
  n_nodes = meshToExport.NbNodes()
  n_elements = len(meshToExport.GetElementsByType(SMESH.VOLUME))
  nodesList = iter(range(1,n_nodes+1))
  elementsList = iter(meshToExport.GetElementsByType(SMESH.VOLUME))
  success = 0
  
  PFlotranOutput = activeFolder + name
  if outputFileFormat == 2: #ASCII
    if outputMeshFormat == 1: #Implicit
      success = meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput)
    elif outputMeshFormat == 2: #Explicit
      domain_file = '.'.join(PFlotranOutput.split('.')[:-1]) + "_Domain.h5"
      meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, 
                             elementsList, domain_file)
      success = meshToPFLOTRANUnstructuredExplicitASCII(meshToExport, PFlotranOutput)
    elif outputMeshFormat == 3: #Polyhedra
      success = meshToPFLOTRANUnstructuredPolyhedraASCII(meshToExport, PFlotranOutput)
      
  elif outputFileFormat == 1: #HDF5
    if outputMeshFormat == 1: #Implicit
      success = meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, \
                                               n_elements, nodesList, \
                                               elementsList, PFlotranOutput, \
                                               compressH5Output)
    elif outputMeshFormat == 2: #Explicit
      meshToPFLOTRANUnstructuredExplicitHDF5(meshToExport, PFlotranOutput)
      domain_file = '.'.join(PFlotranOutput.split('.')[:-1]) + "_Domain.h5"
      meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, elementsList, domain_file, mode="w")
    elif outputMeshFormat == 3: #Polyhedra
      success = meshToPFLOTRANUnstructuredPolyhedraHDF5(meshToExport, PFlotranOutput)
    
  return success
  
  


  
###################################
# UNSTRUCTURED GRID FORMAT EXPORT #
###################################

def meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput):
  """
  Export a Salome mesh as PFLOTRAN implicit unstructured grid in ASCII
  """
  #open pflotran file
  out = open(PFlotranOutput, 'w')
  #initiate 3D element type
  elementCode = {4:'T', 5:'P', 6:'W', 8:'H'}
  #pflotran line 1
  out.write(str(n_elements) + ' ' + str(n_nodes) + '\n')
  #pflotran line 2 to n_element_3D +1
  for i in elementsList:
    elementNode = salomeToPFLOTRANNodeOrder(i, meshToExport)
    if not elementNode: return 0 #fail
    out.write(elementCode[len(elementNode)] + ' ')
    for x in elementNode: #write
      out.write(str(x) + ' ')
    out.write('\n')
  #pflotran line n_element+1 to end
  #write node coordinates
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    out.write("{} {} {}\n".format(X,Y,Z))
  out.close()
  return 0 #success
    
    

def meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput, compress=False):
  """
  Export a Salome mesh as PFLOTRAN implicit unstructured grid in HDF5
  """
  #open pflotran output file
  out = h5py.File(PFlotranOutput, mode='w')
    
  #initialise array
  elementsArray = np.zeros((n_elements,9), dtype='i8')
  
  #hdf5 element
  count = 0
  print('Creating Domain/Cells dataset:')
  for i in elementsList:
    common.progress_bar(count, n_elements, barLength=50)
    elementNode = salomeToPFLOTRANNodeOrder(i, meshToExport)
    if not elementNode: return 0 #fail
    elementsArray[count,0] = len(elementNode)
    for j in range(len(elementNode)):
      elementsArray[count,j+1] = elementNode[j]
    count += 1
  if compress:
    out.create_dataset('Domain/Cells', data=elementsArray, 
                       compression="gzip", compression_opts=9)
  else:
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
  if compress:
    out.create_dataset('Domain/Vertices', data=vertexArray, 
                       compression="gzip", compression_opts=9)
  else:
    out.create_dataset('Domain/Vertices', data=vertexArray)
  del vertexArray
  gc.collect()
  
  out.close()
  return 0 #success





############################################
# UNSTRUCTURED EXPLICIT GRID FORMAT EXPORT #
############################################

def meshToPFLOTRANUnstructuredExplicitASCII(mesh, PFlotranOutput, center0DElem=True,
                                            project_area = False):
  """
  Export a Salome mesh as PFLOTRAN explicit unstructured grid in ASCII
  """
  #print("Note: We use Qhull to compute the element volume since Salome has a error (https://salome-platform.org/forum/forum_10/547695356/view). We build first the convex hull and then get the volume. Thus, for non convex polyhedra, the exported volume will be false. The Salome error should be corrected on its next release.\n")
  
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
    
  for count_center,i in enumerate(mesh.GetElementsByType(SMESH.VOLUME)):
    #get info (center and volume)
    if center0DElem:
      node = mesh.GetElemNodes(elem0Ds[count_center])[0]
      center = mesh.GetNodeXYZ(node)
    else:
      center = mesh.BaryCenter(i)
    volume = mesh.GetVolume(i)
    if volume < 0.:
      #print("Negative cell volume for cell {}, use Qhull instead but volume could be false if cell is non-convex".format(i))
      #error = True
      #volume = common.computeVolumeFromNodeList(mesh.GetElemNodes(i),mesh)
      print(f"Negative cell volume for cell {i}, exporting absolute value instead")
      volume = -volume
    #write info
    out.write(f"{count} {center[0]:.6e} {center[1]:.6e} {center[2]:.6e} {volume:.6e}\n")
    corresp[i]=count
    count += 1
  
  #CONNECTIONS part
  print("Build connections between cells")
  n_faces, sharedFaceDict, faceArea, faceCenter, faceNormal = buildInternalFaces(mesh, project_area)
  print('\nWrite connections')
  out.write("CONNECTIONS {}\n".format(n_faces)) 
  for keys, cellIds in sharedFaceDict.items():
    if len(cellIds) != 2: continue
    area = faceArea[keys]
    center = faceCenter[keys]
    id1,id2 = cellIds
    out.write(f"{corresp[id1]} {corresp[id2]} {center[0]:.6e} {center[1]:.6e} {center[2]:.6e} {area:.6e}\n")
   
  out.close()
  return 0



def meshToPFLOTRANUnstructuredExplicitHDF5(mesh, PFlotranOutput, center0DElem=True,
                                            project_area = False):
  """
  Export a Salome mesh as PFLOTRAN explicit unstructured grid in HDF5
  """
  print("\nWarning! PFLOTRAN explicit grid in HDF5 format only supported in developpement version")
  #open pflotran output file
  out = h5py.File(PFlotranOutput, mode='w')
  
  #CELLS part
  print("Write cell ids, center and volume")
  n_elements = len(mesh.GetElementsByType(SMESH.VOLUME))
  centers = np.zeros((n_elements,3), dtype='f8')
  volumes = np.zeros(n_elements, dtype='f8')
  count = 1
  corresp = {}
  if center0DElem:
    elem0Ds = mesh.GetElementsByType(SMESH.ELEM0D)
    if not len(elem0Ds): center0DElem = False
    
  for count_center,i in enumerate(mesh.GetElementsByType(SMESH.VOLUME)):
    #get info (center and volume)
    if center0DElem:
      node = mesh.GetElemNodes(elem0Ds[count_center])[0]
      center = mesh.GetNodeXYZ(node)
    else:
      center = mesh.BaryCenter(i)
    volume = mesh.GetVolume(i)
    if volume < 0.:
      #print("Negative cell volume for cell {}, use Qhull instead but volume could be false if cell is non-convex".format(i))
      #error = True
      #volume = common.computeVolumeFromNodeList(mesh.GetElemNodes(i),mesh)
      print(f"Negative cell volume for cell {i}, exporting absolute value instead")
      volume = -volume
    #write info
    centers[count_center] = center
    volumes[count_center] = volume
    corresp[i]=count
    count += 1
  out.create_dataset("Domain/Cells/Centers",data=centers)
  out.create_dataset("Domain/Cells/Volumes",data=volumes)
  
  #CONNECTIONS part
  print("Build connections between cells")
  n_faces, sharedFaceDict, faceArea, faceCenter, faceNormal = buildInternalFaces(mesh, project_area)
  
  ids = np.zeros((n_faces,2), dtype='i8')
  areas = np.zeros(n_faces, dtype='f8')
  centers = np.zeros((n_faces,3), dtype='f8')
  normals = np.zeros((n_faces,3), dtype='f8')
  
  count = 0
  print("Get face cell ids, areas, centers and normals")
  for keys, cellIds in sharedFaceDict.items():
    if len(cellIds) != 2: continue
    areas[count] = faceArea[keys]
    centers[count] = faceCenter[keys]
    normals[count] = faceNormal[keys]
    cellIds = [corresp[x] for x in cellIds]
    ids[count] = cellIds
    count += 1
  
  print("Write face cell ids, areas, centers and normals")
  out.create_dataset("Domain/Connections/Areas", data=np.resize(areas,count))
  out.create_dataset("Domain/Connections/Cell Ids", data=np.resize(ids,(count,2)))
  out.create_dataset("Domain/Connections/Centers", data=np.resize(centers,(count,3)))
  out.create_dataset("Domain/Connections/Normals", data=np.resize(normals,(count,3)))
  
  out.close()
  return 0


def meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, 
                           elementsList, PFLOTRANOutput, center0DElem=True, 
                           mode="w"):
  """
  Create the HDF5 file so that DOMAIN_FILENAME can use it for visualization purpose
  """
  print("\nCreate Domain file to use with DOMAIN_FILENAME for visualization")
  #open pflotran output file
  out = h5py.File(PFLOTRANOutput, mode=mode)
  
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
  print('Creating Domain/Cells dataset')
  temp_list = []
  for c in elementsList:
    temp_list.append(16) #we say it is a polyhedron, whatever it is really
    nbF = meshToExport.ElemNbFaces( c )
    temp_list.append(nbF) #write number of face 
    for f in range(0,nbF):
      vFNodes = meshToExport.GetElemFaceNodes( c, f )
      temp_list.append(len(vFNodes)) #write face length
      temp_list.extend([x-1 for x in vFNodes])
  out.create_dataset('Domain/Cells', data=np.array(temp_list, dtype='i8'))
  #write number of cell in attribute
  out["Domain/Cells"].attrs.create("Cell number", [n_elements], dtype='i8')
  
  #store cell center
  print('Creating Domain/[XC,YC,ZC] datasets\n')
  XC = np.zeros(n_elements, dtype='f8')
  YC = np.zeros(n_elements, dtype='f8')
  ZC = np.zeros(n_elements, dtype='f8')
  if center0DElem:
    elem0Ds = meshToExport.GetElementsByType(SMESH.ELEM0D)
    if not len(elem0Ds): center0DElem = False
  for count_center,i in enumerate(meshToExport.GetElementsByType(SMESH.VOLUME)):
    #get info (center and volume)
    if center0DElem:
      node = meshToExport.GetElemNodes(elem0Ds[count_center])[0]
      X,Y,Z = meshToExport.GetNodeXYZ(node)
    else:
      X,Y,Z = meshToExport.BaryCenter(i)
    #write info
    XC[count_center] = X
    YC[count_center] = Y
    ZC[count_center] = Z
  
  out.create_dataset("Domain/XC", data=XC)
  out.create_dataset("Domain/YC", data=YC)
  out.create_dataset("Domain/ZC", data=ZC)
  
  #store number of cells
  #out.create_dataset('Domain/Cell_number', data=np.array([n_elements], dtype="i8"))

  out.close()
  
  return 0
  


############################################
# POLYHEDRAL GRID FORMAT EXPORT #
############################################

def meshToPFLOTRANUnstructuredPolyhedraASCII(meshToExport, PFlotranOutput):
  return 1
  
def meshToPFLOTRANUnstructuredPolyhedraHDF5(meshToExport, PFlotranOutput):
  return 1
