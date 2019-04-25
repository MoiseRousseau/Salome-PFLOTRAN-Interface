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
# 3D element not working with transport ???
# 2D element test
# parallelize code with multiprocessing ?

import sys


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
  



def meshToPFLOTRANUntructuredASCII(mesh, PFlotranOutput):
  from SMESH import VOLUME, FACE
   
  #open pflotran file
  out = open(PFlotranOutput, 'w')
 
  #initiate 2D/3D element type
  if mesh.GetElementsByType(VOLUME):
    elementCode = {4:'T', 5:'P', 6:'W', 8:'H'}
    meshType = VOLUME
  else:
    elementCode = {3:'T', 4:'Q'}
    meshType = FACE
  
  #pflotran line 1
  n_node = mesh.NbNodes()
  n_element = len(mesh.GetElementsByType(meshType))
  out.write(str(n_element) + ' ' + str(n_node) + '\n')

  #pflotran line 2 to n_element_2D/3D +1
  for i in mesh.GetElementsByType(meshType):
    elementNode = mesh.GetElemNodes(i)
    out.write(elementCode[len(elementNode)] + ' ')
    
    elementNode = OrderNodes(elementNode, mesh)
    
    for x in elementNode: #write
      out.write(str(x) + ' ')
    out.write('\n')
  
  #pflotran line n_element+1 to end
  #write node coordinates
  for i in range(1,n_node+1):
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    out.write(str(X) + ' ' + str(Y) + ' ' + str(Z) + '\n')
  
  out.close()
  return
    
    

def meshToPFLOTRANUnstructuredHDF5(mesh, PFlotranOutput):
  import time
  tt = time.time()
  import numpy
  from SMESH import VOLUME, FACE
  try:
    import h5py
  except:
    sys.exit("ERROR: h5py module not installed")
  import gc
  
  #open pflotran output file
  out = h5py.File(PFlotranOutput, mode='w')
  
  #read salome input first line
  if mesh.GetElementsByType(VOLUME):
    meshType = VOLUME
  else:
    meshType = FACE
  
  n_node = mesh.NbNodes()
  n_elements = len(mesh.GetElementsByType(meshType))
    
  #initialise array
  #integer length
  int_type = numpy.log(n_node)/numpy.log(2)/8
  if int_type <= 1: int_type = 'u1'
  elif int_type <= 2: int_type = 'u2'
  elif int_type <= 4: int_type = 'u4'
  else: int_type = 'u8'
  
  if mesh.NbHexas():
    elementsArray = numpy.zeros((n_elements,9), dtype=int_type)
  elif mesh.NbPrisms():
    elementsArray = numpy.zeros((n_elements,7), dtype=int_type)
  elif mesh.NbPyramids():
    elementsArray = numpy.zeros((n_elements,6), dtype=int_type)
  elif mesh.NbTetras() or mesh.NbQuads():
    elementsArray = numpy.zeros((n_elements,5), dtype=int_type)
  elif mesh.NbTriangles():
    elementsArray = numpy.zeros((n_elements,4), dtype=int_type)
  
  #hdf5 element
  count = 0
  for i in mesh.GetElementsByType(meshType):
    elementNode = OrderNodes(i, mesh)
    elementsArray[count,0] = len(elementNode)
    for j in range(len(elementNode)):
      elementsArray[count,j+1] = elementNode[j]
    count += 1

  out.create_dataset('Domain/Cells', data=elementsArray)
  del elementsArray
  gc.collect()
  
  
  #hdf5 node coordinates
  vertexArray = numpy.zeros((n_node, 3), dtype='f8')
  for i in range(0, n_node):
    X,Y,Z = mesh.GetNodeXYZ(i+1)
    vertexArray[i,0] = X
    vertexArray[i,1] = Y
    vertexArray[i,2] = Z
  out.create_dataset('Domain/Vertices', data=vertexArray)
  del vertexArray
  gc.collect()
  
  out.close()
  print(time.time()-tt)
  return



def OrderNodes(elementNumber, mesh):
  """
  right hand rule organize and check
  """
  from SMESH import Geom_QUADRANGLE

  elementNode = mesh.GetElemNodes(elementNumber)
  
  if len(elementNode) == 3: #Tri
    sys.exit('2D element type not supported yet...')


  elif mesh.GetElementShape(elementNumber) == Geom_QUADRANGLE: #Quad
    sys.exit('2D element type not supported yet...')
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
  
  
  elif len(elementNode) == -6: #Prism
    #algoritm rules :
    #1. separate the 2 triangles
    #2. check if right
    #3. arrange first triangle for right hand rule
    #4. arrange second triangle
    elementNode = []
    for faceId in range(5):
      tri = mesh.GetElemFaceNodes(elementNumber, faceId)
      if len(tri) == 3:
        elementNode += tri
    #order 1st triangle to RHD point out 2nd triangle
    vec1 = pointsToVec(elementNode[0],elementNode[1],mesh)
    vec2 = pointsToVec(elementNode[1],elementNode[2],mesh)
    normal1 = computeProdVec(vec1,vec2)
    if computeDotVec(normal1,pointsToVec(elementNode[0],elementNode[3],mesh)) < 0:
      elementToMove = elementNode.pop(1)
      elementNode.insert(2, elementToMove)
      #and recompute vec
      vec1 = pointsToVec(elementNode[0],elementNode[1],mesh)
      vec2 = pointsToVec(elementNode[1],elementNode[2],mesh)
      normal1 = computeProdVec(vec1,vec2)
    vec3 = pointsToVec(elementNode[3],elementNode[4],mesh)
    vec4 = pointsToVec(elementNode[4],elementNode[5],mesh)
    normal2 = computeProdVec(vec3,vec4)
    if computeDotVec(normal1,normal2) < 0:
      #second triangle not in the right order
      elementToMove = elementNode.pop(-1)
      elementNode.insert(-1, elementToMove)
    #check for 1254 is a plan
    #get test plan
    A = elementNode[0]
    B = elementNode[1]
    C = elementNode[4]
    D = elementNode[5]
    for faceId in range(5):
      planElem = mesh.GetElemFaceNodes(elementNumber, faceId)
      planElem.sort()
      if len(planElem) == 4:
        if A in planElem and B in planElem:
          break
    planTest = [A,B,C,D]
    planTest.sort()
    while planElem != planTest:
      elementToMove = elementNode.pop(-1)
      elementNode.insert(3, elementToMove)
      C = elementNode[5]
      D = elementNode[4]
      planTest = [A,B,C,D]
      planTest.sort()
  
  
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

    
  elif len(elementNode) == -8: #hexahedron
    #algorithm rule :
    #4. Check if normal point in the direction of other points
    #5. Make other turn for left hand rule x,y,z,a
    #6. 1x2y should be in the same plan
    #6bis. if not, turn xyza
          
    #1.
    #print(elementNode)
    base = mesh.GetElemFaceNodes(elementNumber, 0)
    base = nonConvex(base,mesh)
    normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1],mesh), pointsToVec(elementNode[1], elementNode[2],mesh)) #from 1 to 2, and from 2 to 3
    ref = computeDotVec(normal, pointsToVec(elementNode[0], elementNode[4],mesh))
    if ref < 0:
      elementToMove = elementNode.pop(3)
      elementNode.insert(1, elementToMove)
      elementToMove = elementNode.pop(2)
      elementNode.insert(3, elementToMove)
    #add other points
    top = [x for x in mesh.GetElemNodes(elementNumber) if x not in base]
    top = nonConvex(top,mesh)
    elementNode = base + top
    #5.
    #recall convention of #2
    normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1],mesh), pointsToVec(elementNode[1], elementNode[2],mesh)) #recalculate normal if change
    #point are normally in the right order from findFourth function
    normal2 = computeProdVec(pointsToVec(elementNode[4], elementNode[5],mesh), pointsToVec(elementNode[5], elementNode[6],mesh))
    if computeDotVec(normal, normal2) < 0: #turn in the wrong direction
      elementToMove = elementNode.pop(7)
      elementNode.insert(5, elementToMove)
      elementToMove = elementNode.pop(6)
      elementNode.insert(7, elementToMove)
    #6.
    #get test plan
    A = elementNode[0]
    B = elementNode[1]
    C = elementNode[4]
    D = elementNode[5]
    for faceId in range(8):
      planElem = mesh.GetElemFaceNodes(elementNumber, faceId)
      planElem.sort()
      if A in planElem and B in planElem and elementNode[3] not in planElem:
        break
    planTest = [A,B,C,D]
    planTest.sort()
    while planElem != planTest:
      elementToMove = elementNode.pop(-1)
      elementNode.insert(4, elementToMove)
      C = elementNode[4]
      D = elementNode[5]
      planTest = [A,B,C,D]
      planTest.sort()
      
  else:
    print('Element type not supported by PFLOTRAN structured implicit grid...')

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
  sys.exit("HDF5 unstructureed explicit seems not to be implemented in PFLOTRAN")
  return




