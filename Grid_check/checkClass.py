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



import numpy as np
import SMESH

class MeshQualityCheck:

  def __init__(self, MESH, nonOrthThreshold = None, skewThreshold = None):
    self.mesh = MESH
    
    self.nonOrthogonalityCheck = True
    self.skewnessCheck = True
    
    self.outputPreSting = "MeshQualityCheck:\t\t"
    self.sharedFaceDict = {}
    self.nbInternalFaces = 0

    self.orthAngle = None
    self.skewness = None
    self.avNonOrth = 0
    self.maxNonOrth = 0
    self.avSkew = 0
    self.maxSkew = 0
    
    self.salomeid_to_idhere = {}
    self.face_normal = None
    self.cell_center = None
    self.cell_center_vector = None
    self.cell_center_distance = None
    return
    
  def getNonOrth(self):
    return self.orthAngle
  
  def getSkew(self):
    return self.skewness
    
  ### MESH CHECK FUNCTION ###
  def buildInternalFaces(self):
    volIDs = self.mesh.GetElementsByType( SMESH.VOLUME )
    for v in volIDs:
      nbF = self.mesh.ElemNbFaces( v )
      for f in range(0,nbF):
        vFNodes = self.mesh.GetElemFaceNodes( v, f )
        dictKey = tuple(sorted(vFNodes))
        try:
          self.sharedFaceDict[ dictKey ][1] = v
          self.nbInternalFaces += 1
        except:
          self.sharedFaceDict[ dictKey ] = [v , 0]
    #0 based index for mesh element
    count = 0
    self.idhere_to_salomeid = {}
    for v in volIDs:
      self.salomeid_to_idhere[v] = count
      self.idhere_to_salomeid[count] = v
      count += 1
    self.sharedFaceDict = {x:y for x,y in self.sharedFaceDict.items() if y[1]}
    self.connections = np.array([[self.salomeid_to_idhere[x], self.salomeid_to_idhere[y]]
                                 for x,y in self.sharedFaceDict.values()], dtype='i8')
    return
  
  def compute_cell_center(self):
    volIDs = self.mesh.GetElementsByType( SMESH.VOLUME )
    self.cell_center = np.zeros((len(volIDs), 3), dtype='f8')
    for i,v in enumerate(volIDs):
      self.cell_center[i] = self.mesh.BaryCenter(v)
    return
    
  def compute_unit_cell_center_vector(self):
    self.cell_center_vector = self.cell_center[self.connections[:,0],:] \
                              - self.cell_center[self.connections[:,1],:]
    self.cell_center_distance = np.linalg.norm(self.cell_center_vector, axis=1)
    self.cell_center_vector /= self.cell_center_distance[:,np.newaxis]
    return
    
  def compute_face_normal(self):
    self.vertices = np.zeros((self.mesh.NbNodes(), 3), dtype='f8')
    for i,v in enumerate(self.mesh.GetNodesId()):
      self.vertices[i,:] = self.mesh.GetNodeXYZ(v)
    self.face_normal = np.zeros((self.nbInternalFaces,3), dtype='f8')
    for i,face_vs in enumerate(self.sharedFaceDict.keys()):
      u = self.vertices[face_vs[1]-1] - self.vertices[face_vs[0]-1] #Warning, contiguous numbering
      v = self.vertices[face_vs[2]-1] - self.vertices[face_vs[1]-1]
      n = np.cross(u,v)
      self.face_normal[i] = n / np.linalg.norm(n)
    return
    
  def checkMesh(self):
    print("\n")
    print(self.outputPreSting + "checking mesh")
      
    # 1. build internal face
    print(self.outputPreSting + "finding internal faces")
    self.buildInternalFaces()
    print(self.outputPreSting + "number of connections: ", self.nbInternalFaces)
    
    # 2. compute unit cell center vector
    print(self.outputPreSting + "compute cell center")
    self.compute_cell_center()
    print(self.outputPreSting + "compute unit cell center vector")
    self.compute_unit_cell_center_vector()
    
    # 3. compute face normal
    print(self.outputPreSting + "compute face normal")
    self.compute_face_normal()
    
    # 4. compute orthogonality angle
    print(self.outputPreSting + "compute orthogonality angle")
    #both face_normal and cell_center_vector are unitary
    dot = self.face_normal[:,0] * self.cell_center_vector[:,0] \
          + self.face_normal[:,1] * self.cell_center_vector[:,1] \
          + self.face_normal[:,2] * self.cell_center_vector[:,2]
    self.orthAngle = np.arccos(np.abs(dot)) * 180 / np.pi
    self.avNonOrth = np.mean(self.orthAngle)
    self.maxNonOrth = np.max(self.orthAngle)
    
    # 5. compute skewness
    print(self.outputPreSting + "compute skewness")
    face_center = np.zeros((self.nbInternalFaces, 3), dtype='f8')
    for i,f_vs in enumerate(self.sharedFaceDict.keys()):
      f_vs = [x-1 for x in f_vs]
      face_center[i] = np.sum(self.vertices[f_vs,:],axis=0) / len(f_vs)
    w = face_center - self.cell_center[self.connections[:,0]]
    s = (self.face_normal[:,0] * w[:,0] + self.face_normal[:,1] * w[:,1] 
           + self.face_normal[:,2] * w[:,2])
    s /= (self.face_normal[:,0] * self.cell_center_vector[:,0] \
          + self.face_normal[:,1] * self.cell_center_vector[:,1] \
          + self.face_normal[:,2] * self.cell_center_vector[:,2])
    P = self.cell_center[self.connections[:,0]] + s[:,np.newaxis]*self.cell_center_vector
    self.skewness = np.linalg.norm(face_center - P, axis=1) / self.cell_center_distance
    self.avSkew = np.mean(self.skewness)
    self.maxSkew = np.max(self.skewness)
 
    self.printStats()
    return

  def printStats(self):
    if( self.nonOrthogonalityCheck ):
      print(self.outputPreSting + "average non-orthogonality: ", self.avNonOrth)
      print(self.outputPreSting + "max non-orthogonality: ", self.maxNonOrth)
    if( self.skewnessCheck ):
      print(self.outputPreSting + "average skewness: ", self.avSkew)
      print(self.outputPreSting + "max skewness: ", self.maxSkew)
    return
   
   
  ### GROUP CREATION ###
  def createNonOrthGroup(self, value):
    volToAdd = set()
    for i,angle in enumerate(self.orthAngle):
      if angle > value:
        ids = self.connections[i]
        volToAdd.add(self.idhere_to_salomeid[ids[0]])
        volToAdd.add(self.idhere_to_salomeid[ids[1]])
    interimGroup = self.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "Non-orthogonality > " + str(value) )
    interimGroup.Add(list(volToAdd))
    return
    
  def createSkewGroup(self, value):
    volToAdd = set()
    for i,skew in enumerate(self.skewness):
      if skew > value:
        ids = self.connections[i]
        volToAdd.add(self.idhere_to_salomeid[ids[0]])
        volToAdd.add(self.idhere_to_salomeid[ids[1]])
    interimGroup = self.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "Skewness > " + str(value) )
    interimGroup.Add(list(volToAdd))
    return

    
