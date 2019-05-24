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
# 2D element test
# parallelize code with multiprocessing ?

import sys



def meshToPFLOTRAN(meshToExport, activeFolder, outputFileFormat, outputMeshFormat, name=None):
  import salome
  import SMESH
  smesh = salome.smesh.smeshBuilder.New()
  #Get mesh input type
  if isinstance(meshToExport,salome.smesh.smeshBuilder.meshProxy):
    fatherMesh = smesh.Mesh(meshToExport)
    if not name: name = fatherMesh.GetName()
    if fatherMesh.GetElementsByType(SMESH.VOLUME):
      meshType = SMESH.VOLUME
    else:
      meshType = SMESH.FACE
    n_nodes = fatherMesh.NbNodes()
    n_elements = len(fatherMesh.GetElementsByType(meshType))
    nodesList = iter(range(1,n_nodes+1))
    elementsList = iter(fatherMesh.GetElementsByType(meshType))
    
  elif isinstance(meshToExport,SMESH._objref_SMESH_Group):
    if SMESH.VOLUME in meshToExport.GetTypes():
      meshType = SMESH.VOLUME
    elif SMESH.FACE in meshToExport.GetTypes():
      meshType = SMESH.FACE
    else: raise RuntimeError('1D mesh not supported')
    fatherMesh = smesh.Mesh(meshToExport.GetMesh())
    n_nodes = len(meshToExport.GetNodeIDs())
    n_elements = len(meshToExport.GetIDs())
    nodesList = iter(meshToExport.GetNodeIDs())
    elementsList = iter(meshToExport.GetIDs())
    if not name: name = salome.smesh.smeshBuilder.GetName(meshToExport)
    
  elif isinstance(meshToExport,salome.smesh.smeshBuilder.submeshProxy):
    if meshToExport.GetElementsByType(SMESH.VOLUME):
      meshType = SMESH.VOLUME
    elif meshToExport.GetElementsByType(SMESH.FACE):
      meshType = SMESH.FACE
    else: raise RuntimeError('1D mesh not supported')
    fatherMesh = smesh.Mesh(meshToExport.GetMesh())
    n_nodes = meshToExport.GetNumberOfNodes(1)
    n_elements = meshToExport.GetNumberOfElements()
    nodesList = iter(meshToExport.GetNodesId())
    elementsList = iter(meshToExport.GetElementsId())
    if not name: name = salome.smesh.smeshBuilder.GetName(meshToExport)
    
  else:
    raise RuntimeError('Selection is not a mesh or part of a mesh. Interruption')
    
  #Export it
  PFlotranOutput = activeFolder + name
  if outputFileFormat == 1: #ASCII
    if outputMeshFormat == 1: #Implicit
      meshToPFLOTRANUntructuredASCII(fatherMesh, n_nodes, n_elements, nodesList, elementsList, meshType, PFlotranOutput + '.ugi')
    if outputMeshFormat == 2 and isinstance(fatherMesh, salome.smesh.smeshBuilder.Mesh): #Explicit
      meshToPFLOTRANUnstructuredExplicitASCII(fatherMesh, PFlotranOutput + '.uge')
      
  elif outputFileFormat == 2: #HDF5
    meshToPFLOTRANUnstructuredHDF5(meshToExport, fatherMesh, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput + '.h5')
    
  return
  
  
  
  
def pointsToVec(A,B,mesh):
  """
  Create a vector AB by giving node number (A,B)
  """
  X_A,Y_A,Z_A = mesh.GetNodeXYZ(A)
  X_B,Y_B,Z_B = mesh.GetNodeXYZ(B)
  vec = (X_B-X_A, Y_B-Y_A, Z_B-Z_A)
  return vec
  
def computeProdVec(vecX,vecY):
  prodVec = (vecX[1]*vecY[2]-vecY[1]*vecX[2], vecX[2]*vecY[0]-vecY[2]*vecX[0], vecX[0]*vecY[1]-vecY[0]*vecX[1])
  return prodVec
  
def computeDotVec(vecX,vecY):
  dot = vecX[0]*vecY[0]+vecX[1]*vecY[1]+vecX[2]*vecY[2]
  return dot      
  
def nonConvex(elementList,mesh):
  #we make hypothese that saome doesnt create self intersecting object
  #if not, to be completed
  return elementList
  



def meshToPFLOTRANUntructuredASCII(fatherMesh, n_nodes, n_elements, nodesList, elementsList, meshType, PFlotranOutput):
  from SMESH import VOLUME, FACE
   
  #open pflotran file
  out = open(PFlotranOutput, 'w')
 
  #initiate 2D/3D element type
  if meshType == VOLUME:
    elementCode = {4:'T', 5:'P', 6:'W', 8:'H'}
  else:
    elementCode = {3:'T', 4:'Q'}
  
  #pflotran line 1
  out.write(str(n_element) + ' ' + str(n_nodes) + '\n')

  #pflotran line 2 to n_element_2D/3D +1
  for i in elementsList:
    elementNode = fatherMesh.GetElemNodes(i)
    out.write(elementCode[len(elementNode)] + ' ')
    
    elementNode = OrderNodes(elementNode, mesh)
    
    for x in elementNode: #write
      out.write(str(x) + ' ')
    out.write('\n')
  
  #pflotran line n_element+1 to end
  #write node coordinates
  for i in nodesList:
    X,Y,Z = fatherMesh.GetNodeXYZ(i)
    out.write(str(X) + ' ' + str(Y) + ' ' + str(Z) + '\n')
  
  out.close()
  return
    
    

def meshToPFLOTRANUnstructuredHDF5(meshToExport, fatherMesh, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput):
  import numpy
  try:
    import h5py
  except:
    raise RuntimeError('h5py is not installed.')
  import gc
  
  #open pflotran output file
  out = h5py.File(PFlotranOutput, mode='w')
    
  #initialise array
  #integer length
  int_type = numpy.log(n_nodes)/numpy.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  
  #only linear element
  if meshToExport.GetMeshInfo()[16]: #hexa
    elementsArray = numpy.zeros((n_elements,9), dtype=int_type)
  elif meshToExport.GetMeshInfo()[19]: #prisms
    elementsArray = numpy.zeros((n_elements,7), dtype=int_type)
  elif meshToExport.GetMeshInfo()[14]: #pyr
    elementsArray = numpy.zeros((n_elements,6), dtype=int_type)
  elif meshToExport.GetMeshInfo()[7] or meshToExport.GetMeshInfo()[12]: #quad or tetra
    elementsArray = numpy.zeros((n_elements,5), dtype=int_type)
  elif meshToExport.GetMeshInfo()[4]: #tri
    elementsArray = numpy.zeros((n_elements,4), dtype=int_type)
  else:
    raise RuntimeError('No linear element of dimension superior to 2 found.')
  
  #hdf5 element
  count = 0
  for i in elementsList:
    elementNode = OrderNodes(i, fatherMesh)
    elementsArray[count,0] = len(elementNode)
    for j in range(len(elementNode)):
      elementsArray[count,j+1] = elementNode[j]
    count += 1

  out.create_dataset('Domain/Cells', data=elementsArray)
  del elementsArray
  gc.collect()
  
  
  #hdf5 node coordinates
  vertexArray = numpy.zeros((n_nodes, 3), dtype='f8')
  for i in nodesList:
    X,Y,Z = fatherMesh.GetNodeXYZ(i)
    vertexArray[i-1,0] = X
    vertexArray[i-1,1] = Y
    vertexArray[i-1,2] = Z
  out.create_dataset('Domain/Vertices', data=vertexArray)
  del vertexArray
  gc.collect()
  
  out.close()
  return



def OrderNodes(elementNumber, mesh):
  """
  right hand rule organize and check
  """
  from SMESH import Geom_QUADRANGLE

  elementNode = mesh.GetElemNodes(elementNumber)
  
  if len(elementNode) == 3: #Tri
    raise RuntimeError('2D element type not supported yet...')


  elif mesh.GetElementShape(elementNumber) == Geom_QUADRANGLE: #Quad
    raise RuntimeError('2D element type not supported yet...')
    elementNode = nonConvex(elementNode,mesh)

  
  elif len(elementNode) == 4: #tetrahedron
    #method : compute normal and dot product
    #and if over the plane (>0) it's ok
    vecX = pointsToVec(elementNode[0], elementNode[1],mesh)
    vecY = pointsToVec(elementNode[0], elementNode[2],mesh)
    vecZ = pointsToVec(elementNode[0], elementNode[3],mesh)
    prodVecXY = computeProdVec(vecX, vecY)
    dotXZ = computeDotVec(prodVecXY,vecZ)

    if not dotXZ > 0: #right hand rule not respected !
      #inverse vertex 0 and 1 to turn in the right direction
      elementNode = [elementNode[1], elementNode[0], elementNode[2], elementNode[3]]
    
      
  elif len(elementNode) == 5: #Pyramid
    #the fourth 4 nodes need to be in the same plane
    #and the 5th in the direction of the right hand rule
    #see rules for hexahedron for detail
    
    #1.
    for faceId in range(5):
      base = mesh.GetElemFaceNodes(elementNumber, faceId)
      if len(base) == 4:
        break
    base =  nonConvex(base,mesh)
    lastNode = [x for x in elementNode if x not in base]
    elementNode = base + lastNode
    #4.
    normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1],mesh), pointsToVec(elementNode[1], elementNode[2],mesh)) #from 1 to 2, and from 2 to 3
    ref = computeDotVec(normal, pointsToVec(elementNode[0], elementNode[4],mesh))
    if ref < 0:
      elementToMove = elementNode.pop(3)
      elementNode.insert(1, elementToMove)
      elementToMove = elementNode.pop(2)
      elementNode.insert(3, elementToMove)
    
  elif len(elementNode) == 6: #Prism
    #algoritm rules :
    #1. identify quads
    #2. get segments between triangles
    #3. assure RHD point out second triangle
    quads = []
    tri = None
    for faceId in range(5):
      nodes = mesh.GetElemFaceNodes(elementNumber, faceId)
      if len(nodes) == 4:
        quads += [nodes]
      if len(nodes) == 3 and not tri:
        tri = nodes
      if len(quads) == 3 and tri:
        break
  
    #here we get aligned nodes
    corresNodes = {node:-1 for node in tri}
    segments = [[x for x in quads[0] if x in quads[1]]]
    segments.append([x for x in quads[1] if x in quads[2]])
    segments.append([x for x in quads[2] if x in quads[0]])
    for seg in segments:
      if seg[0] in corresNodes.keys():
        corresNodes[seg[0]] = seg[1]
      else:
        corresNodes[seg[1]] = seg[0]
  
    #construct output
    #need to know which node is up or down to order it
    for i in range(3):
      elementNode[i] = tri[i]
      elementNode[i+3] = corresNodes[tri[i]]
    
    #and ensure RHD
    vec1 = pointsToVec(elementNode[0],elementNode[1],mesh)
    vec2 = pointsToVec(elementNode[1],elementNode[2],mesh)
    normal1 = computeProdVec(vec1,vec2)
    if computeDotVec(normal1,pointsToVec(elementNode[0],elementNode[3],mesh)) < 0:
      #RHD not respected: invert triangle
      elementNode = elementNode[3:] + elementNode[0:3]    
  
  elif len(elementNode) == 8: #hexahedron
    #algoritm rules :
    #1. take a quad and isole other node
    #2. get other quads
    #2. get segments between the two quads of 1
    #3. assure RHD point out second quad
    
    #1.
    base = mesh.GetElemFaceNodes(elementNumber, 0)
    base = nonConvex(base, mesh)
    
    #2.
    quads = []
    for faceId in range(5):
      quad = mesh.GetElemFaceNodes(elementNumber, faceId+1)
      inter = [x for x in quad if x in base]
      if inter:
        quads.append(quad)
    
    #3
    segments = []
    for chosenQuad in range(4):
      for otherQuad in range(3):
        seg = [x for x in quads[otherQuad] if x in quads[chosenQuad]] #intersection quad
        seg.sort()
        if seg not in segments and len(seg) == 2:
          segments.append(seg)
          if len(segments) == 4:
            break
      if len(segments) == 4:
            break
    
    corresNodes = {node:-1 for node in base}
    #print(segments)
    #print(base)
    for seg in segments:
      if seg[0] in corresNodes.keys():
        corresNodes[seg[0]] = seg[1]
      else:
        corresNodes[seg[1]] = seg[0]
    #print(corresNodes)
            
    #4.
    #construct output
    for i in range(4):
      elementNode[i] = base[i]
      elementNode[i+4] = corresNodes[base[i]]
    #print(elementNode)
    normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1],mesh), pointsToVec(elementNode[1], elementNode[2],mesh)) #from 1 to 2, and from 2 to 3
    ref = computeDotVec(normal, pointsToVec(elementNode[0], elementNode[4],mesh))
    if ref < 0:
      elementNode = elementNode[4:] + elementNode[:4]
      
  else:
    raise RuntimeError('Element not supported by PFLOTRAN implicit grid format')

  return elementNode



def meshToPFLOTRANUnstructuredExplicitASCII(mesh, PFlotranOutput):
  from SMESH import VOLUME, FACE
  
  def ordonateNodes(nodesList):
    index = nodesList.index(min(nodesList))
    if index:
      nodesList = nodesList[index:]+nodesList[:index]
    if nodesList[-1] < nodesList[1]:
      nodesList = [nodesList[0]]+nodesList[1:][::-1]
    return nodesList
  
  def createInternalFace(mesh):
    nodesFaceOrdered = set()
    for cell in mesh.GetElementsByType(meshType):
      faceId = 0
      while mesh.GetElemFaceNodes(cell, faceId):
        nodes = mesh.GetElemFaceNodes(cell, faceId)
        nodes = tuple(ordonateNodes(nodes))
        connectivity = len(mesh.GetElementsByNodes(nodes, meshType))
        if nodes not in nodesFaceOrdered and connectivity == 2:
          nodesFaceOrdered.add(nodes)
        faceId += 1
    count = 0
    newFacesIds = [int(0) for x in range(len(nodesFaceOrdered))]
    for face in nodesFaceOrdered:
      if len(face) == 4: newFaceId = mesh.AddFace(face)
      elif len(face) == 3: newFaceId = mesh.AddFace(face)
      else: newFaceId = mesh.AddPolygonalFace(face)
      newFacesIds[count] = newFaceId
      count += 1
    if 0:
      mesh.MakeGroupByIds("Internal faces", FACE, newFacesIds)
    return newFacesIds
 
  #open pflotran output file
  out = open(PFlotranOutput, mode='w')
  
  #read salome input first line
  if mesh.GetElementsByType(VOLUME):
    meshType = VOLUME
  else:
    meshType = FACE
    sys.exit("2D mesh not implemented yet")

  #CELLS part
  n_elements = len(mesh.GetElementsByType(meshType))
  out.write("CELLS %s\n" %n_elements)
  count = 1
  corresp = {}
  for i in mesh.GetElementsByType(meshType):
    #get info (center and volume)
    center = mesh.BaryCenter(i)
    if meshType == VOLUME:
      volume = mesh.GetVolume(i)
    else : 
      volume = 0
      sys.exit("volume = 0 for 2D element")
    #write info
    out.write("%s " %int(count))
    for x in center:
      out.write("%s " %x)
    out.write("%s\n" %volume)
    corresp[i]=count
    count += 1
    
  #CONNECTIONS part
  #number of connection
  if meshType == VOLUME:
    connectionType = FACE
  else:
    connectionType = EDGE
    sys.exit("EDGE connection not supported yet")

  faceIds = createInternalFace(mesh)
  out.write("CONNECTIONS {}\n".format(len(faceIds)))
  for faceId in faceIds:
    nodes = mesh.GetElemNodes(faceId)
    elementList = mesh.GetElementsByNodes(nodes, meshType)
    for x in elementList:
      out.write("{} ".format(corresp[x]))
    center = mesh.BaryCenter(faceId)
    area = mesh.GetArea(faceId)
    for x in center:
      out.write("{} ".format(x))
    out.write("{}\n".format(area))
  
  out.close()

  return corresp



def meshToPFLOTRANUnstructuredExplicitHDF5(mesh, PFlotranOutput):
  raise RuntimeError('HDF5 unstructureed explicit seems not to be implemented in PFLOTRAN')
  return




