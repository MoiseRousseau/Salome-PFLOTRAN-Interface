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

import numpy as np
import sys



# ================== PRINT FUNCTIONS =================

def progress_bar(iteration, total, barLength=50):
  #https://gist.github.com/azlux/7b8f449ac7fa308d45232c3a281be7bb
  if iteration % int(total/barLength): return #update every 2%
  percent = int(round((iteration / total) * 100))
  nb_bar_fill = int(round((barLength * percent) / 100))
  bar_fill = '#' * nb_bar_fill
  bar_empty = ' ' * (barLength - nb_bar_fill)
  sys.stdout.write("\r  [{0}] {1}%".format(str(bar_fill + bar_empty), percent))
  sys.stdout.flush()
  return





# ================== GEOMETRY FUNCTIONS =================

def getNormalFromNodeList(nodesId, mesh):
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
  return v3/np.linalg.norm(v3)

 
def computeAreaFromNodeList(nodesId,mesh):
  #http://geomalgorithms.com/a01-_area.html#2D%20Polygons
  if len(nodesId) < 3: return 0
  #initiate
  normal = getNormalFromNodeList(nodesId,mesh)
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
  

def computeCenterFromNodeList(nodesId,mesh):
  #https://stackoverflow.com/questions/18305712/how-to-compute-the-center-of-a-polygon-in-2d-and-3d-space
  center = np.zeros((3), dtype='f8')
  sL = 0
  for i in range(len(nodesId)):
    x0,y0,z0 = mesh.GetNodeXYZ(nodesId[i-1])
    x1,y1,z1 = mesh.GetNodeXYZ(nodesId[i])
    L = ((x1 - x0)**2 + (y1 - y0)**2 + (z1 - z0)**2) ** 0.5
    center[0] += (x0 + x1)/2 * L
    center[1] += (y0 + y1)/2 * L
    center[2] += (z0 + z1)/2 * L
    sL += L
  center /= sL
  return center
  

def computeCellCenterVectorFromCellIds(cellIds, mesh):
  X1,Y1,Z1 = mesh.BaryCenter(cellIds[0])
  X2,Y2,Z2 = mesh.BaryCenter(cellIds[1])
  return [X1-X2, Y1-Y2, Z1-Z2]
  
 
def computeVolumeFromNodeList(nodesId, mesh):
  from scipy.spatial import ConvexHull
  nodesId = set(nodesId)
  coord = np.zeros((len(nodesId),3), dtype='f8')
  for i,node in enumerate(nodesId):
    coord[i] = mesh.GetNodeXYZ(node)
  try:
    volume = ConvexHull(coord).volume
  except:
    print("Qhull error on nodes:\n")
    print(coord)
    print('Use Salome volume function instead\n')
    volume = -1
  return volume
