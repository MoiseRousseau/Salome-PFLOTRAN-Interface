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
# Author : Moise Rousseau (2021), email at moise.rousseau@polymtl.ca



import SMESH
import numpy as np
import salome
try:
  import h5py
except:
  pass


def ReadPFLOTRANMesh(f_in):
  #determine format
  extension = f_in.split('.')[-1]
  if extension not in ["h5", "uge", "ugi"]:
    print("Could not determine PFLOTRAN mesh format from input file extension")
    print("Try read the file")
    try:
      f = h5py.File(f_in, 'r')
      grp = f["Domain"]
      extension = 'h5'
    except:
      try:
        f = open(f_in, 'r')
        test = f.readline().split()[0].lower()
        if test == "cells": extension = 'uge'
        else: extension = 'ugi'
      except:
        f.close()
        print("Impossible to determine the format")
        return 1
  f.close()
  #create new mesh
  mesh_name = f_in.split('/')[-1]
  mesh_name = '.'.join(f_in.split('.')[:-1])
  mesh = smesh.Mesh(name=mesh_name)
  if extension == 'h5':
    f = h5py.File(f_in, 'r')
    grp = f["Domain"]
    if "Connections" in list(grp.keys()): 
      f.close()
      readPFLOTRANMeshExplicitHDF5(f_in,mesh)
    elif "Cells" in list(grp.keys()):
      f.close()
      readPFLOTRANMeshImplicitHDF5(f_in,mesh)
  elif extension == 'ugi':
    readPFLOTRANMeshImplicitASCII(f_in,mesh)
  elif extension == 'uge':
    readPFLOTRANMeshExplicitASCII(f_in,mesh)
  else:
    return 1
  return 0
  


def readPFLOTRANMeshImplictASCII(f_in, mesh):
  #add vertices first
  src = open(f_in, 'r')
  n_elements, n_vertices = [int(x) for x in src.readline().split()]
  for i in range(n_elements): src.readline() #pass elements
  #add vertices
  for i in range(n_vertices):
    X, Y, Z = [float(x) for x in src.readline().split()]
    mesh.AddNode(X,Y,Z)
  #close and reopen to go at first line
  src.close() 
  src = open(f_in, 'r')
  src.readline()
  #add elements
  for i in range(n_elements):
    line = src.readline().split()
    elem_type = line[0]
    nodes = [int(x) for x in line[1:]]
    nodes = PFLOTRANToSalomeIndexes(nodes)
    if not nodes:
      print(f"Element type not recognized {elem_type}")
      return 1
    mesh.AddVolume(nodes)
  return 0
  


def readPFLOTRANMeshImplictHDF5(f_in, mesh):
  print("Not Implemented")
  return 1



def readPFLOTRANMeshExplicitASCII(f_in, mesh):
  # TODO (moise) 
  # read if there is a vertices / elements section
  # if not, can not import
  print("Not Implemented")
  return 1



def readPFLOTRANMeshExplicitHDF5(f_in, mesh):
  print("Not Implemented")
  return 1



def PFLOTRANToSalomeIndexes(nodes):
  if len(nodes) == 8:
    nodes = [nodes[0],nodes[3],nodes[2],nodes[1],nodes[4],nodes[7],nodes[6],nodes[5]]
  elif len(nodes) == 6:
    nodes = [nodes[1],nodes[0],nodes[2],nodes[4],nodes[3],nodes[5]]
  elif len(nodes) == 5:
    nodes = [nodes[0],nodes[3],nodes[2],nodes[1],nodes[4]]
  elif len(nodes) == 4:
    nodes = [nodes[1],nodes[0],nodes[2],nodes[3]]
  else: 
    nodes = []
  return nodes
  
