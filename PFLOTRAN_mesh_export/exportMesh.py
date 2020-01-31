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


def progress_bar(iteration, total, barLength=50):
  #https://gist.github.com/azlux/7b8f449ac7fa308d45232c3a281be7bb
  percent = int(round((iteration / total) * 100))
  nb_bar_fill = int(round((barLength * percent) / 100))
  bar_fill = '#' * nb_bar_fill
  bar_empty = ' ' * (barLength - nb_bar_fill)
  sys.stdout.write("\r  [{0}] {1}%".format(str(bar_fill + bar_empty), percent))
  sys.stdout.flush()
  return


def meshToPFLOTRAN(meshToExport, activeFolder, outputFileFormat, outputMeshFormat, name=None):
  import salome
  import SMESH
  if 0:
    smesh = salome.smesh.smeshBuilder.New()
    #Get mesh input type
    if isinstance(meshToExport,salome.smesh.smeshBuilder.meshProxy):
      meshToExport = smesh.Mesh(meshToExport)
      if not name: name = meshToExport.GetName()
      if meshToExport.GetElementsByType(SMESH.VOLUME):
        meshType = SMESH.VOLUME
      else:
        meshType = SMESH.FACE
      n_nodes = meshToExport.NbNodes()
      n_elements = len(meshToExport.GetElementsByType(meshType))
      nodesList = iter(range(1,n_nodes+1))
      elementsList = iter(meshToExport.GetElementsByType(meshType))
      
    elif isinstance(meshToExport,SMESH._objref_SMESH_Group):
      if SMESH.VOLUME in meshToExport.GetTypes():
        meshType = SMESH.VOLUME
      elif SMESH.FACE in meshToExport.GetTypes():
        meshType = SMESH.FACE
      else: raise RuntimeError('1D mesh not supported')
      meshToExport = smesh.Mesh(meshToExport.GetMesh())
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
      meshToExport = smesh.Mesh(meshToExport.GetMesh())
      n_nodes = meshToExport.GetNumberOfNodes(1)
      n_elements = meshToExport.GetNumberOfElements()
      nodesList = iter(meshToExport.GetNodesId())
      elementsList = iter(meshToExport.GetElementsId())
      if not name: name = salome.smesh.smeshBuilder.GetName(meshToExport)
      
    else:
      raise RuntimeError('Selection is not a mesh or part of a mesh. Interruption')
    
  #Export it
  n_nodes = meshToExport.NbNodes()
  n_elements = len(meshToExport.GetElementsByType(SMESH.VOLUME))
  nodesList = iter(range(1,n_nodes+1))
  elementsList = iter(meshToExport.GetElementsByType(SMESH.VOLUME))
  
  PFlotranOutput = activeFolder + name
  if outputFileFormat == 2: #ASCII
    if outputMeshFormat == 1: #Implicit
      meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput)
    elif outputMeshFormat == 2: #Explicit
      meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput)
      meshToPFLOTRANUnstructuredExplicitASCII(meshToExport, PFlotranOutput)
      
  elif outputFileFormat == 1: #HDF5
    if outputMeshFormat == 1: #Implicit
      meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput)
    elif outputMeshFormat == 2: #Explicit
      raise RuntimeError('Explicit HDF5 exportation not implemented in PFLOTRAN')
    
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
  



def meshToPFLOTRANUntructuredASCII(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput):
  from SMESH import VOLUME, FACE
   
  #open pflotran file
  out = open(PFlotranOutput, 'w')
 
  #initiate 3D element type
  elementCode = {4:'T', 5:'P', 6:'W', 8:'H'}
  
  #pflotran line 1
  out.write(str(n_elements) + ' ' + str(n_nodes) + '\n')

  #pflotran line 2 to n_element_3D +1
  for i in elementsList:
    
    elementNode = OrderNodes(i, meshToExport)
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
  return
    
    

def meshToPFLOTRANUnstructuredHDF5(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFlotranOutput):
  import numpy
  import h5py
  import gc
  import SMESH
  
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
  if meshToExport.GetMeshInfo()[SMESH.Entity_Hexa]: #hexa
    elementsArray = numpy.zeros((n_elements,9), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Penta]: #prisms
    elementsArray = numpy.zeros((n_elements,7), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Pyramid]: #pyr
    elementsArray = numpy.zeros((n_elements,6), dtype=int_type)
  elif meshToExport.GetMeshInfo()[SMESH.Entity_Tetra]: #tetra
    elementsArray = numpy.zeros((n_elements,5), dtype=int_type)
  #elif meshToExport.GetMeshInfo()[4]: #tri
  #  elementsArray = numpy.zeros((n_elements,4), dtype=int_type)
  else:
    raise RuntimeError('No linear element of dimension 3 found.')
  
  #hdf5 element
  count = 0
  print('Creating Domain/Cells dataset:')
  for i in elementsList:
    if not count % 100:
      progress_bar(count, n_elements, barLength=50)
    elementNode = OrderNodes(i, meshToExport)
    elementsArray[count,0] = len(elementNode)
    for j in range(len(elementNode)):
      elementsArray[count,j+1] = elementNode[j]
    count += 1

  out.create_dataset('Domain/Cells', data=elementsArray)
  del elementsArray
  gc.collect()
  
  
  #hdf5 node coordinates
  print('\nCreating Domain/Vertices dataset: ')
  vertexArray = numpy.zeros((n_nodes, 3), dtype='f8')
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
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
  import numpy as np
  
  def getNormal(nodesId):
    p1 = np.array(mesh.GetNodeXYZ(nodesId[0]), dtype='f8')
    p2 = np.array(mesh.GetNodeXYZ(nodesId[1]), dtype='f8')
    p3 = np.array(mesh.GetNodeXYZ(nodesId[2]), dtype='f8')
    v1 = p2 - p1
    v1 /= np.sqrt(np.dot(v1,v1))
    v2 = p3 - p1
    v2 /= np.sqrt(np.dot(v2,v2))
    v3 = np.cross(v1, v2)
    i = 3
    while np.dot(v3,v3) < 1e-3:
      if i == len(nodesId): break
      p3 = np.array(mesh.GetNodeXYZ(nodesId[i]), dtype='f8')
      v2 = p3 - p1
      v2 /= np.sqrt(np.dot(v2,v2))
      v3 = np.cross(v1, v2)
      i += 1
    return v3
  
  def computeArea(nodesId):
    #http://geomalgorithms.com/a01-_area.html#2D%20Polygons
    if len(nodesId) < 3: return 0
    #initiate
    normal = getNormal(nodesId)
    points = np.zeros((len(nodesId)+2,3), dtype='f8')
    for i in range(len(nodesId)):
      points[i] = mesh.GetNodeXYZ(nodesId[i])
    points[len(nodesId)] = mesh.GetNodeXYZ(nodesId[0])
    points[len(nodesId)+1] = mesh.GetNodeXYZ(nodesId[1])
    #select projection plane
    ic = 0
    jc = 1
    coord = 2
    if abs(normal[0]) > abs(normal[1]): 
      if abs(normal[0]) > abs(normal[2]): 
        ic = 1
        jc = 2
        coord = 0
    elif abs(normal[1]) > abs(normal[2]): 
      ic = 2
      jc = 0
      coord = 1
    #compute area
    area = 0
    for i in range(1,len(nodesId)+1):
      area += points[i][ic] * (points[i+1][jc] - points[i-1][jc])
    #scale to get get area before projection
    area *= np.sqrt(np.dot(normal,normal)) / (2*normal[coord])
    
    return abs(area)
     
  def computeCenter(nodesId):
    center = np.zeros((3), dtype='f8')
    for node in nodesId:
      center += mesh.GetNodeXYZ(node)
    center /= len(nodesId)
    return center
  
  #open pflotran output file
  out = open(PFlotranOutput, mode='w')
  
  #read salome input first line
  if mesh.GetElementsByType(VOLUME):
    meshType = VOLUME
  else:
    meshType = FACE
    sys.exit("2D mesh not implemented yet")

  #CELLS part
  print("Write cell ids, center and volume")
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
    
  print("Build connections between cells")
  sharedFaceDict = {}
  faceArea = {}
  faceCenter = {}
  volIDs = mesh.GetElementsByType( VOLUME )
  count_bar = 0
  n_elements = len(volIDs)
  for v in volIDs:
    count_bar += 1
    if not count_bar % 100:
      progress_bar(count_bar, n_elements, barLength=50)
    nbF = mesh.ElemNbFaces( v )
    for f in range(0,nbF):
      vFNodes = mesh.GetElemFaceNodes( v, f )
      dictKey = tuple(sorted(vFNodes))
      if dictKey not in sharedFaceDict:
        sharedFaceDict[ dictKey ] = [ v ]
      else:
        sharedFaceDict[ dictKey ].append( v )
        faceArea[tuple(sharedFaceDict[ dictKey ])] = computeArea(vFNodes)
        faceCenter[tuple(sharedFaceDict[ dictKey ])] = computeCenter(vFNodes)
  
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

  return 



def meshToPFLOTRANUnstructuredExplicitHDF5(mesh, PFlotranOutput):
  raise RuntimeError('HDF5 unstructureed explicit seems not to be implemented in PFLOTRAN')
  return
  


def meshToXDMFWhenExplicit(meshToExport, n_nodes, n_elements, nodesList, elementsList, PFLOTRANOutput):
  import h5py
  import numpy
  print("Create XDMF file for visualisation")
  
  prefix = PFLOTRANOutput.split('.')[:-1]
  PFLOTRANOutput = ''
  for x in prefix:
    PFLOTRANOutput += x
  PFLOTRANOutput += "_Domain.h5"
  
  #open pflotran output file
  out = h5py.File(PFLOTRANOutput, mode='w')
  
  #hdf5 node coordinates
  print('\nCreating Domain/Vertices dataset: ')
  vertexArray = numpy.zeros((n_nodes, 3), dtype='f8')
  for i in nodesList:
    X,Y,Z = meshToExport.GetNodeXYZ(i)
    vertexArray[i-1,0] = X
    vertexArray[i-1,1] = Y
    vertexArray[i-1,2] = Z
  out.create_dataset('Domain/Vertices', data=vertexArray)
  
  #HDF5 cells
  #initialise array
  #integer length
  print('\nCreating Domain/Cells dataset: ')
  int_type = numpy.log(n_nodes)/numpy.log(2)/8
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
        
  out.create_dataset('Domain/Cells', data=numpy.array(temp_list, dtype=int_type))
  
  #store number of cells
  out.create_dataset('Domain/Cell_number', data=numpy.array([n_elements], dtype=int_type))
  
  out.close()
  
  return
  
  
  

  


