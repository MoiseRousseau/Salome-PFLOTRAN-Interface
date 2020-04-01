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



################################
# 
# Slightly modified version of 
# https://github.com/FynnAschmoneit/nonOrthogonalityCheckSalome
# 
################################


import numpy as np
import SMESH

class MeshQualityCheck:

  def __init__(self, MESH, nonOrthThreshold = None, skewThreshold = None):
    self.mesh = MESH
    
    if(nonOrthThreshold is None): 
      self.nonOrthogonalThreshold = 65
    else:
      self.nonOrthogonalThreshold = nonOrthThreshold

    if(skewThreshold is None):
      self.skewnessThreshold = 0.5
    else:
      self.skewnessThreshold = skewThreshold
    
    self.nonOrthogonalityCheck = True
    self.skewnessCheck = True
    if( self.nonOrthogonalThreshold == 0):
      self.nonOrthogonalityCheck = False
    if( self.skewnessThreshold == 0):
      self.skewnessCheck = False

    self.progressOutput = True
    self.groupsForFailedVolumePairs = True
    
    self.outputPreSting = "MeshQualityCheck:\t\t"
    self.sharedFaceDict = {}
    self.nbInternalFaces = 0

    self.nonOrthogonalVolPairs = {}
    self.avNonOrth = 0
    self.maxNonOrth = 0

    self.SkewVolPairs = {}
    self.avSkew = 0
    self.maxSkew = 0

    #random.seed(1)    # for coloring of volume pair groups

    if(self.progressOutput):
      print(self.outputPreSting + "finding internal faces")

    volIDs = self.mesh.GetElementsByType( SMESH.VOLUME )
    for v in volIDs:
      nbF = self.mesh.ElemNbFaces( v )
      for f in range(0,nbF):
        vFNodes = self.mesh.GetElemFaceNodes( v, f )
        dictKey = tuple(sorted(vFNodes))
        if dictKey not in self.sharedFaceDict:
          self.sharedFaceDict[ dictKey ] = [ v ]
        else:
          self.sharedFaceDict[ dictKey ].append( v )

    self.nbInternalFaces = len(self.sharedFaceDict) 
    return

  def COMsLineDist(self, v_ar):
    bC1 = self.mesh.BaryCenter(v_ar[0])
    p1 = np.array(bC1, dtype = 'f8')
    bC2 = self.mesh.BaryCenter(v_ar[1])
    p2 = np.array(bC2, dtype = 'f8')
    line = p2 - p1
    #print(p2,p1)
    centerDistance = np.sqrt(np.dot(line, line))
    return [line, centerDistance]

  def faceNormalDir(self, faceCoord):
    p1 = np.array(faceCoord[0], dtype='f8')
    p2 = np.array(faceCoord[1], dtype='f8')
    p3 = np.array(faceCoord[2], dtype='f8')
    v1 = p2 - p1
    v1 /= np.sqrt(np.dot(v1,v1))
    v2 = p3 - p1
    v2 /= np.sqrt(np.dot(v2,v2))
    v3 = np.cross(v1, v2)
    i = 3
    while np.dot(v3,v3) < 1e-3:
      if i == len(faceCoord): break
      pi = np.array(faceCoord[i], dtype='f8')
      v2 = pi - p1
      v2 /= np.sqrt(np.dot(v2,v2))
      v3 = np.cross(v1, v2)
      i += 1
    return v3
    
  def getAngle(self, v1, v2):
    tol = 1e-6
    ang = np.dot(v1,v2)/np.sqrt(np.dot(v1,v1)*np.dot(v2,v2))
    #print(v1,v2,ang)
    if ang > 1-tol:
      return 0
    elif ang < -1+tol:
      return 0
    ang = np.arccos(ang)
    #print(ang)
    ang = ang/np.pi*180
    #print(ang)
    if ang > 90: ang = 180 - ang
    return ang

  def checkNonOrth(self, COMsLine, fNorm, volPair, append):
    ang = self.getAngle(COMsLine, fNorm)
    if append:
      self.nonOrthogonalVolPairs[ tuple(volPair) ] = ang
    return ang

  def COMofFace(self, faceCoord, nbNodesOfFace):
    comFaceComp = np.array([0,0,0], dtype='f8')
    for j in range(0, nbNodesOfFace):
      comFaceComp += faceCoord[j]
    comFaceComp /= nbNodesOfFace
    return comFaceComp
  
  def checkSkewness(self, pFCom, COMsLine, centerDistance, volPair, append):
    bC1 = np.array(self.mesh.BaryCenter(volPair[0]), dtype = 'f8')
    test = pFCom - bC1
    a = np.dot(test,COMsLine)/centerDistance
    b = np.sqrt(np.dot(test,test))
    skewness = np.sqrt(b-a)/centerDistance
    if append:
      self.SkewVolPairs[ tuple(volPair) ] = skewness
    return skewness

  def calcAverages(self):
    if( self.nonOrthogonalityCheck ):  
      self.avNonOrth = np.mean(list(self.nonOrthogonalVolPairs.values()))
      self.maxNonOrth = np.max(list(self.nonOrthogonalVolPairs.values()))
    if( self.skewnessCheck ): 
      self.avSkew = np.mean(list(self.SkewVolPairs.values()))
      self.maxSkew = np.max(list(self.SkewVolPairs.values()))
    return

  def printStats(self):
    print("\n%s statistics " %(self.mesh.GetName()))
    print(self.outputPreSting + "no faces: ", self.nbInternalFaces)

    if( self.nonOrthogonalityCheck ):
      #print(self.outputPreSting + "non-orthogonality threshold: ", self.nonOrthogonalThreshold)
      #print(self.outputPreSting + "number of non-orthogonal faces: ", len(self.nonOrthogonalVolPairs))
      print(self.outputPreSting + "average non-orthogonality: ", self.avNonOrth)
      print(self.outputPreSting + "max non-orthogonality: ", self.maxNonOrth)
    if( self.skewnessCheck ):
      #print(self.outputPreSting + "skewness threshold: ", self.skewnessThreshold)
      #print(self.outputPreSting + "number of skew faces: ", len(self.tooSkewVolPairs))
      print(self.outputPreSting + "average skewness: ", self.avSkew)
      print(self.outputPreSting + "max skewnes: ", self.maxSkew)
    return
    
  def createNonOrthGroup(self, value):
    volToAdd = set()
    for volPair,ang in self.nonOrthogonalVolPairs.items():
      if ang > value:
        volToAdd.add(volPair[0])
        volToAdd.add(volPair[1])
    interimGroup = self.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "Non-orthogonality > " + str(value) )
    interimGroup.Add(list(volToAdd))
    return
    
  def createSkewGroup(self, value):
    volToAdd = set()
    for volPair,ang in self.SkewVolPairs.items():
      if ang > value:
        volToAdd.add(volPair[0])
        volToAdd.add(volPair[1])
    interimGroup = self.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "Skewness > " + str(value) )
    interimGroup.Add(list(volToAdd))
    return
  
  def getNonOrth(self):
    res = [x for x in self.nonOrthogonalVolPairs.values()]
    return res
    
  def getSkew(self):
    res = [x for x in self.SkewVolPairs.values()]
    return res
        
  def computeHistNonOrth(self, nb_inter):
    inters = {}
    for i in range(nb_inter):
      mini = i*self.maxNonOrth/nb_inter
      maxi = (i+1)*self.maxNonOrth/nb_inter
      inters[(mini,maxi)] = 0
    for (volIds,ang) in self.nonOrthogonalVolPairs.items():
      for inter in inters.keys():
        if inter[0] < ang and ang < inter[1]:
          inters[inter] += 1
          break
    return inters
    
  def computeHistSkew(self, nb_inter):
    inters = {}
    for i in range(nb_inter):
      mini = i*self.maxSkew/nb_inter
      maxi = (i+1)*self.maxSkew/nb_inter
      inters[(mini,maxi)] = 0
    for (volIds,ang) in self.SkewVolPairs.items():
      for inter in inters.keys():
        if inter[0] < ang and ang < inter[1]:
          inters[inter] += 1
          break
    return inters
  
    
  def checkMesh(self):
    #TODO Convert this in cython ??
    
    #else:
    if(self.progressOutput):
      print(self.outputPreSting + "checking mesh")

    faceIterNumber = 1
    for k, v in self.sharedFaceDict.items():
      if len(v) == 2:  
      # k is the list of face node Ids for internal faces if corresponding volume vector consists of 2 elements 

        # calculation line connecting volumes' centers of mass and its distance
        COMsLine, centerDistance = self.COMsLineDist(v)
        
        # convert string of face node Ids k to list of corresp coordinates
        faceIDList = list(k)
        nbNodesOfFace = len(faceIDList)
        faceCoord = [ self.mesh.GetNodeXYZ( faceIDList[i] ) for i in range(0, nbNodesOfFace) ]

        if( self.nonOrthogonalityCheck ):
        # calculating face normal direction
          fNorm = self.faceNormalDir(faceCoord)
        #calculating the angle between faceNormal and com-connecting line
          self.checkNonOrth(COMsLine, fNorm, v, True)

        if( self.skewnessCheck ):
        #calculation skewness as the minimum distance between the com-connecting line and com of the face
          pFCom = self.COMofFace(faceCoord, nbNodesOfFace)
          self.checkSkewness(pFCom, COMsLine, centerDistance, v, True)
      
      relProg = faceIterNumber/self.nbInternalFaces*100
      if( self.progressOutput and relProg % 5 < 99/self.nbInternalFaces  ):
        print(self.outputPreSting + "progress: " +str(relProg//1) +"%")
      faceIterNumber = faceIterNumber + 1

    self.calcAverages()  
    self.printStats()
    #if( self.groupsForFailedVolumePairs ):
    #  self.createGroupsOfPairs()
    return

    
