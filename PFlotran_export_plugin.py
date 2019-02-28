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
# line 2 to n_element+1 : code(T,P,W,H) list_of_node
# line n_element+2 to n_element+n_node+1 : x y z
#
# note : list of node in element line need to respect right hand rule
# for tetrahedron, the 4th need need to be in the direction of the right hand rule

# Tested only for tetrahedral meshes, until new update ...



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
  print ("    Add check for right hand rule \n")
  print ("Tested only with tetrahedral meshes\n")
  print ("###################################\n")
  
  def GetFolder(path):
    l = path.split('/')
    path = ''
    for i in range(0,len(l)-1):
      path = path + l[i] + '/'
    return path


  def meshSalomeToPFlotranAscii(salomeInput, PFlotranOutput, Mesh3D=True):
    
    #open salome and pflotran file
    src = open(salomeInput, 'r')
    out = open(PFlotranOutput, 'w')
    
    #read salome input first line
    line = src.readline().split(' ')
    n_node = int(line[0])
    n_element_tot = int(line[1])
    n_element_write = n_element_tot
    
    #save node coordinate for verifing right hand rule
    #initiate list
    X = [0.0]*n_node
    Y = [0.0]*n_node
    Z = [0.0]*n_node
    for i in range(0, n_node):
      line = src.readline().split(' ')
      X[i] = float(line[1])
      Y[i] = float(line[2])
      Z[i] = float(line[3])
   
    #initiate 2D/3D element type
    if Mesh3D:
      elementCode = {'304':'T', '305':'P', '306':'W', '308':'H'}
    else:
      elementCode = {'203':'T', '204':'Q'}
    #Go to 2D/3D element
    for i in range(0, n_element_tot):
      line = src.readline().split(' ')
      elementType = line[1]
      if not elementType in elementCode.keys():
        n_element_write -= 1
        continue
      break
      
    #pflotran line 1
    out.write(str(n_element_write) + ' ' + str(n_node) + '\n')
    
    #pflotran line 2 to n_element_2D/3D +1
    for i in range(0, n_element_write):
      out.write(elementCode[elementType] + ' ')
      elementNode = [int(x) for x in line[2:-1]]
      
      elementNode = checkRightHandRule(elementType, elementNode, X, Y, Z)
      
      for x in elementNode: #write
        out.write(str(x) + ' ')
      out.write('\n')
      line = src.readline().split(' ')
    
    #pflotran line n_element+1 to end
    #write node coordinates
    for i in range(0,len(X)):
      out.write(str(X[i]) + ' ' + str(Y[i]) + ' ' + str(Z[i]) + '\n')
    
    src.close()
    out.close()
    
    

def meshSalomeToPFlotranHDF5(name, folder, PFlotranOutputName, i, Mesh3D=True):
    import h5py
    import gc
    
    #open salome and pflotran files
    src = open(folder+'DAT_raw_mesh/'+name+'.dat', 'r')
    out = h5py.File(PFlotranOutputName,mode='w')
    
    #read salome input first line
    line = src.readline().split(' ')
    n_node = int(line[0])
    n_element = int(line[1])
    
    #save node coordinate for verifing right hand rule
    #initiate list
    X = [0.0]*n_node
    Y = [0.0]*n_node
    Z = [0.0]*n_node
    for i in range(0, n_node):
      line = src.readline().split(' ')
      X[i] = float(line[1])
      Y[i] = float(line[2])
      Z[i] = float(line[3])
   
    #initiate 2D/3D element type
    if Mesh3D:
      elementCode = {'304':4, '305':5, '306':6, '308':8}
    else:
      elementCode = {'203':3, '204':4}
    
    #Go to 2D/3D element
    #TODO : Make 2D/3D recognition automatic
    while True:
      line = src.readline().split(' ')
      elementType = line[1]
      if not elementType in elementCode.keys():
        n_element -= 1
        continue
      break
      
    #initialise array
    elementsArray = [None]*n_element
    idCorrespondance = {key: int(0) for key in range(0,n_element)}
    
    #hdf5 element
    for i in range(0, n_element):
      elementArray = []
      idCorrespondance[i] = int(line[0])
      elementArray.append(elementCode[ilne[1]])
      elementNode = [int(x) for x in line[2:-1]]
      elementNode = checkRightHandRule(elementType, elementNode, X, Y, Z)
      for x in elementNode:
        elementArray.append(x)
      elementsArray[i] = elementArray
      line = src.readline().split(' ')
      
    out.create_dataset('Domain/Cells', data=elementsArray)
    del elementsArray, elementArray, elementNode, x, line #desallocate
    gc.collect()
    src.close()
    
    #hdf5 node coordinates
    vertexArray = [[float(0)]*3]*n_node
    for i in range(n_node):
      vextexArray[i][0] = X[i]
      vextexArray[i][1] = Y[i]
      vextexArray[i][2] = Z[i]
    out.create_dataset('Domain/Vertices', data=vertexArray)
    del vertexArray, X, Y, Z
    gc.collect()
    
    #Region id
    if i > 1:
    #TODO
      region_group = out.create_group("Regions")
      
    return


  
  def checkRightHandRule(elementType, elementNode, X, Y, Z):
    """
    right hand rule check, only for tetrahedron
    TODO for other type
    method : contruct a plane with the 3 first points given, determine its equation
    and if over the plane (>0) it's ok
    """
    from itertools import permutations
    
    if elementType == '304': #tetrahedron
      vecX = (X[elementNode[1]-1]-X[elementNode[0]-1], Y[elementNode[1]-1]-Y[elementNode[0]-1], Z[elementNode[1]-1]-Z[elementNode[0]-1])
      vecY = (X[elementNode[2]-1]-X[elementNode[0]-1], Y[elementNode[2]-1]-Y[elementNode[0]-1], Z[elementNode[2]-1]-Z[elementNode[0]-1])
      vecZ = (X[elementNode[3]-1]-X[elementNode[0]-1], Y[elementNode[3]-1]-Y[elementNode[0]-1], Z[elementNode[3]-1]-Z[elementNode[0]-1])
      prodVecXY = (vecX[1]*vecY[2]-vecY[1]*vecX[2], vecX[2]*vecY[0]-vecY[2]*vecX[0], vecX[0]*vecY[1]-vecY[0]*vecX[1])
      dotXZ = prodVecXY[0]*vecZ[0]+prodVecXY[1]*vecZ[1]+prodVecXY[2]*vecZ[2]
      if not dotXZ > 0: #right hand rule not respected !
        #inverse vertex 0 and 1 to turn in the right direction
        elementNode = [elementNode[1], elementNode[0], elementNode[2], elementNode[3]]
      return elementNode
        
        
    elif elementType == '305': #Wedge
      print('Element type not supported yet...')
      #the fourth 4 nodes need to be in the same plane
      #and the 5th in the direction of the right hand rule
      
    elif elementType == '306': #Prism
      print('Element type not supported yet...')
    elif elementType == '308': #hexahedron
      print('Element type not supported yet...')
    return False




  # get context study, studyId, salomeGui
  #activeStudy = context.study
  activeStudy = salome.myStudy

  #create folder for exportation
  activeFolder = activeStudy._get_URL()
  activeFolder = GetFolder(activeFolder)
  print ("Mesh to be save in the folder " + activeFolder)
  if not os.path.exists(activeFolder+'DAT_raw_mesh/'):
    os.makedirs(activeFolder+'DAT_raw_mesh/')

  #retrieve selected meshes
  exportSubmeshFlag = True
  print ("Retrieve selected mesh")
  meshToExport = activeStudy.FindObjectID(salome.sg.getSelected(0)).GetObject()
  name = salome.smesh.smeshBuilder.GetName(meshToExport)
  i = 1 #material to export
  if not len(meshToExport.GetMeshOrder()) or not exportSubmeshFlag: #only one material
    print ("No submesh, only one material")
    #Export from Salome
    print ("Mesh export in progress...")
    meshToExport.ExportDAT(activeFolder+'DAT_raw_mesh/'+name+'.dat')
    zone_assign = open(activeFolder+name+'_zone.assignment', 'w')
    zone_assign.write('%s.dat 1\n' %(name))
    zone_assign.close()

  else:
    submeshToExport = meshToExport.GetMeshOrder()[0]
    print ("%s submeshes in the corresponding mesh" %len(submeshToExport)) 

    #Export from Salome
    print ("Mesh export in progress...")
    meshToExport.ExportDAT(activeFolder+'DAT_raw_mesh/'+name+'.dat')
    zone_assign = open(activeFolder+name+'_region.assignment', 'w')
    for mesh in submeshToExport:
      name2 = salome.smesh.smeshBuilder.GetName(mesh)
      meshToExport.ExportPartToDAT(mesh, activeFolder+'DAT_raw_mesh/'+name2+'.dat')
      zone_assign.write('%s.dat %s\n' %(name2,i))
      i = i+1
    zone_assign.close()


  #Convertion to Pflotran
  asciiOut = False
  hdf5Out = True
  if asciiOut:
    meshSalomeToPFlotranAscii(activeFolder+'DAT_raw_mesh/'+name+'.dat', activeFolder+name+'.mesh')
    if i > 1:
      print("Warning ! Ascii output not compatible with region assigning, please consider HDF5 output.\n")
  if hdf5Out:
    meshSalomeToPFlotranHDF5(activeFolder+'DAT_raw_mesh/'+name+'.dat', activeFolder+name+'.h5', i)
    

  #Delete temporary files
  delete_raw_meshes = True
  if delete_raw_meshes:
      for x in os.listdir(activeFolder+'DAT_raw_mesh'):
          os.remove(activeFolder+'DAT_raw_mesh/'+x)
      os.rmdir(activeFolder+'DAT_raw_mesh')

  print (" END \n")
  print ("####################\n\n")

  return
  
  
salome_pluginsmanager.AddFunction('Pflotran Tools/Export mesh to PFLOTRAN',
                                  'Export mesh and submesh to PFLOTRAN HDF5 format',
                                  Pflotran_export)
