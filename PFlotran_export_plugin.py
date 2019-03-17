#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author : Moise Rousseau (2019)
#
# Convert Salome DAT file to Pflotran mesh input
# 
# Salome DAT ouput file description :
# line 1 : n_node n_element
# line 2 to n_node+1 : #node x y z
# line n+2 to n_node+n_element+1 : #element code list_of_node
# code = #dimension 0 #node_number, exemple : 203 for triangle, 304 for tetrahedron
#
# Pflotran input file description :
# line 1 : n_element n_node
# line 2 to n_element+1 : code(T,Q,P,W,H) list_of_node
# line n_element+2 to n_element+n_node+1 : x y z
#
# note : list of node in element line need to respect right hand rule



#TODO
# 2D region ASCII not working yet
# 3D quad not working with transport
# make test pour each element for Lange test (2003)
# add RHD for 2D element -> necessary ?
# 2D element test
# dialog box for path / ascii / region
# parallelize code with multiprocessing ?

import sys



def Pflotran_export(context):
  """Convert Salome DAT mesh to Pflotran readable ASCII grid
  And region as HDF5 file
  Need to add Pflotran HDF5 mesh file
  Tested only for tetrahedral elements
  For other type support, need to update the check right hand rule function
  Export first from Salome to DAT file and convert to Pflotran after
  """
  
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


  def meshSalomeToPFlotranAscii(mesh, PFlotranOutput):
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
    for i in meshToExport.GetElementsByType(meshType):
      elementNode = mesh.GetElemNodes(i)
      out.write(elementCode[len(elementNode)] + ' ')
      
      elementNode = checkRightHandRule(elementNode, mesh)
      
      for x in elementNode: #write
        out.write(str(x) + ' ')
      out.write('\n')
    
    #pflotran line n_element+1 to end
    #write node coordinates
    for i in range(1,n_node+1):
      X,Y,Z = meshToExport.GetNodeXYZ(i)
      out.write(str(X) + ' ' + str(Y) + ' ' + str(Z) + '\n')
    
    out.close()
    
    
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
    
    

  def meshSalomeToPFlotranHDF5(mesh, PFlotranOutput):
    import numpy
    from SMESH import VOLUME, FACE
    try:
      import h5py
    except:
      print('\n\nError : h5py module not installed...\n')
      print('Follow the procedure at ...\n')
      sys.exit("FAIL")
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
    for i in meshToExport.GetElementsByType(meshType):
      elementNode = mesh.GetElemNodes(i)
      elementNode = checkRightHandRule(elementNode, mesh)
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
      X,Y,Z = meshToExport.GetNodeXYZ(i+1)
      vertexArray[i,0] = X
      vertexArray[i,1] = Y
      vertexArray[i,2] = Z
    out.create_dataset('Domain/Vertices', data=vertexArray)
    del vertexArray
    gc.collect()
    
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

      
  def checkRightHandRule(elementNode, mesh):
    """
    right hand rule organize and check
    """
    
    def pointsToVec(A,B):
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

    def norm(vec):
      from numpy import sqrt
      normVec = sqrt(vec[0]*vec[0]+vec[1]*vec[1]+vec[2]*vec[2])
      return normVec
      
    def isPlan(A,B,C,D, tolCosAngle = 0.01):
      if A==B or A==C or A==D: return False
      if C==B or B==D or C==D: return False
      vecX = pointsToVec(A, B)
      vecY = pointsToVec(A, C)
      prodVecXY = computeProdVec(vecX, vecY)
      prodVecXY = prodVecXY/norm(prodVecXY)
      vecZ = pointsToVec(A, D)
      prodVecXZ = computeProdVec(vecX, vecZ)
      prodVecXZ = prodVecXZ/norm(prodVecXZ)
      cosAngle = computeDotVec(prodVecXY, prodVecXZ)
      if abs(cosAngle-1) < tolCosAngle:
        return True
      else:
        return False
      
    def findFourth(elementNode):
      #1. first 3 point
      A = elementNode[0]
      B = elementNode[1]
      C = elementNode[2]
      elementNodeWork = [x for x in elementNode]
      elementNodeWork.remove(elementNode[0])
      elementNodeWork.remove(elementNode[1])
      elementNodeWork.remove(elementNode[2])
      #1. find fourth
      for x in elementNodeWork:
        if isPlan(A,B,C,x):
          elementNodeWork.remove(x)
          elementNode = [A,B,C,x]
          #anticipe 3.
          while not checkOrder(elementNode):
            continue
          while not checkOrder(elementNodeWork):
            continue
          elementNode.append(elementNodeWork)
          return True
      return False
      
    def checkOrder(elementList):
      #dont forget all 4 points in the plan
      #follow each point in the order
      #if in the right order, all vectoriel product need to be in the same direction
      vec1 = pointsToVec(elementList[0], elementList[1])
      vec2 = pointsToVec(elementList[1], elementList[2])
      prodVec12 = computeProdVec(vec1, vec2)
      vec3 = pointsToVec(elementList[2], elementList[3])
      prodVec23 = computeProdVec(vec2, vec3)
      if computeDotVec(prodVec12,prodVec23) < 0: #not in the same direction
        #here, mean that 3rd and 4th point are inversed
        #make the draw and you will see
        elementList = [elementList[0], elementList[1], elementList[3], elementList[2]]
        return False
      vec4 = pointsToVec(elementList[3], elementList[1])
      prodVec34 = computeProdVec(vec3, vec4)
      if computeDotVec(prodVec23,prodVec34) < 0:
        #here, mean that 1st and 2nd point are diagonal
        #make the draw and you will see, again
        elementList = [elementList[0], elementList[2], elementList[1], elementList[3]]
        return False
      return True
      
    def separateTriangles(elementList):
      for x2 in elementList[1:]:
        for x3 in [x for x in elementList[1:] if x != x2]:
          tri = [elementList[0], x2, x3]
          tri2 = [x for x in elementList if not x in tri]
          for x in tri2: #take the other
            if not isPlan(tri[0],tri[1],tri[2],x): #if not in the plan
              #separe the 2 triangles
              vec1 = pointsToVec(tri[0],tri[1])
              vec2 = pointsToVec(tri[1],tri[2])
              normal = computeProdVec(vec1,vec2)
              ref = computeDotVec(normal, pointsToVec(tri[0],tri2[0]))
              for x in tri2[1:]: #check for same side
                if computeDotVec(normal, pointsToVec(tri[0],x))*ref < 0:
                  found = False
                  break #if no, stop
                found = True
              if found: #we found it
                if ref < 0: #not the right order
                  tri = [tri[0],tri[2],tri[1]]
                for x in tri2:
                  tri.append(x)
                return tri
    
    
    if len(elementNode) == 4: #tetrahedron
      #method : compute normal and dot product
      #and if over the plane (>0) it's ok
      vecX = pointsToVec(elementNode[0], elementNode[1])
      vecY = pointsToVec(elementNode[0], elementNode[2])
      vecZ = pointsToVec(elementNode[0], elementNode[3])
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
      while not isPlan(elementNode[0],elementNode[1],elementNode[2],elementNode[3]):
        elementToMove = elementNode.pop(-1)
        elementNode.insert(0, elementToMove)
      #4.
      normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1]), pointsToVec(elementNode[1], elementNode[2])) #from 1 to 2, and from 2 to 3
      ref = computeDotVec(normal, pointsToVec(elementNode[0], elementNode[4]))
      if ref < 0:
        elementToMove = elementNode.pop(3)
        elementNode.insert(1, elementToMove)
        elementToMove = elementNode.pop(2)
        elementNode.insert(3, elementToMove)
      
      
    elif len(elementNode) == 6: #Prism
      #algoritm rules :
      #1. separate the 2 triangles
      #2. check if every others points is in the same side
      #3. arrange first triangle for right hand rule
      #4. arrange second triangle
      elementNode = separateTriangles(elementNode)
      vec1 = pointsToVec(elementNode[0],elementNode[1])
      vec2 = pointsToVec(elementNode[1],elementNode[2])
      normal1 = computeProdVec(vec1,vec2)
      vec3 = pointsToVec(elementNode[3],elementNode[4])
      vec4 = pointsToVec(elementNode[4],elementNode[5])
      normal2 = computeProdVec(vec3,vec4)
      if computeDotVec(normal1,normal2) < 0:
        #second triangle not in the right order
        elementToMove = elementNode.pop(-1)
        elementNode.insert(-1, elementToMove)
      #check for 1254 is a plan
      A = elementNode[0]
      B = elementNode[1]
      C = elementNode[4]
      D = elementNode[3] 
      while not isPlan(A,B,C,D):
        elementToMove = elementNode.pop(-1)
        elementNode.insert(3, elementToMove)
        A = elementNode[0]
        B = elementNode[1]
        C = elementNode[4]
        D = elementNode[3]
    
      
    elif len(elementNode) == 8: #hexahedron
      #algorithm rule :
      #1. take 3 first point and found 4th in the same plan
      #2. check if all the other point are on the same side of the plan
      #2bis. if not, take another point random point not selected and restart
      #3. Organise points to "turn" in the same direction
      #4. Check if normal point in the direction of other points
      #5. Make other turn for left hand rule x,y,z,a
      #6. 1x2y should be in the same plan
      #6bis. if not, turn xyza
            
      #1.
      while not findFourth(elementNode):
        elementToMove = elementNode.pop(-1)
        elementNode.insert(2, elementToMove)
      #2.
      normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1]), pointsToVec(elementNode[1], elementNode[2])) #from 1 to 2, and from 2 to 3
      ref = computeDotVec(normal, pointsToVec(elementNode[0], elementNode[4]))
      for node in elementNode[5:]:
        if ref*computeDotVec(normal, pointsToVec(elementNode[0], node)) < 0:
          #2bis.
          elementToMove = elementNode.pop(4) #random, so the 5th
          elementNode.insert(2, elementToMove)
          #repeat 1.
          findFourth(elementNode)
      #3. already done in the findFourth function
      #4.
      if ref < 0:
        elementToMove = elementNode.pop(3)
        elementNode.insert(1, elementToMove)
        elementToMove = elementNode.pop(2)
        elementNode.insert(3, elementToMove)
      #5.
      #recall convention of #2
      normal = computeProdVec(pointsToVec(elementNode[0], elementNode[1]), pointsToVec(elementNode[1], elementNode[2])) #recalculate normal if change
      #point are normally in the right order from findFourth function
      normal2 = computeProdVec(pointsToVec(elementNode[4], elementNode[5]), pointsToVec(elementNode[5], elementNode[6]))
      if computeDotVec(normal, normal2) < 0: #turn in the wrong direction
        elementToMove = elementNode.pop(7)
        elementNode.insert(5, elementToMove)
        elementToMove = elementNode.pop(6)
        elementNode.insert(7, elementToMove)
      #6.
      A = elementNode[0]
      B = elementNode[4]
      C = elementNode[5]
      D = elementNode[1] 
      while not isPlan(A,B,C,D):
        elementToMove = elementNode.pop(-1)
        elementNode.insert(4, elementToMove)
        A = elementNode[0]
        B = elementNode[4]
        C = elementNode[5]
        D = elementNode[1]
        
        
    elif elementType == '204': #Quad
      print('2D element type not supported yet...')

    elif elementType == '203': #Tri
      print('2D element type not supported yet...')
        
    else:
      print('Element type not supported by PFLOTRAN...')

    return elementNode


  # get context study, studyId, salomeGui
  activeStudy = salome.myStudy

  #create folder for exportation
  activeFolder = activeStudy._get_URL()
  activeFolder = GetFolder(activeFolder)
  print ("Mesh to be save in the folder " + activeFolder)

  #retrieve selected meshes
  print ("Retrieve selected mesh")
  meshToExport = activeStudy.FindObjectID(salome.sg.getSelected(0)).GetObject()
  name = salome.smesh.smeshBuilder.GetName(meshToExport)
  submeshToExport = meshToExport.GetMeshOrder()[0]
  print ("%s submeshes in the corresponding mesh" %len(submeshToExport)) 

  #Export to Pflotran
  exportSubmeshFlag = False
  asciiOut = False
  hdf5Out = True
  print("Running mesh exportation")
  if asciiOut:
    meshSalomeToPFlotranAscii(meshToExport, activeFolder+name+'.mesh')
  if hdf5Out:
    meshSalomeToPFlotranHDF5(meshToExport, activeFolder+name+'.h5')
  print("Mesh exporation successful, go to submeshes now")
    
  if len(submeshToExport) and exportSubmeshFlag:
    if asciiOut:
      print("Warning ! Ascii output not compatible with 3D region assigning, please consider HDF5 output.\n")
      for submesh in submeshToExport:
        submeshName = salome.smesh.smeshBuilder.GetName(submesh)
        print("  Exporting submesh %s to ASCII file: %s" %(submeshName, submeshName+'.ss'))
        submeshAsRegionASCII(submesh, activeFolder+submeshName+'.ss', submeshName)
    if hdf5Out:
      for submesh in submeshToExport:
        submeshName = salome.smesh.smeshBuilder.GetName(submesh)
        print("  Exporting submesh to .h5 file: %s" %submeshName)
        submeshAsRegionHDF5(submesh, activeFolder+name+'.h5', submeshName)
  else: 
    print("You choose not to export submeshes")
    
  print ("    END \n")
  print ("####################\n\n")

  return
  
  
salome_pluginsmanager.AddFunction('Pflotran Tools/Export mesh to PFLOTRAN',
                                  'Export mesh and submesh to PFLOTRAN HDF5 format',
                                  Pflotran_export)
