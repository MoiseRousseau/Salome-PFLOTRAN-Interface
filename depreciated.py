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
  


def OrderNodes(elementNumber, mesh):
  """
  right hand rule organize and check
  """
  elementNode = mesh.GetElemNodes(elementNumber)
  
  if len(elementNode) == 4: #tetrahedron
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


