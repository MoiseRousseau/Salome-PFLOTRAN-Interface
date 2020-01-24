#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.4.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/moise/Ecole/plugin SALOME_/Salome-PFLOTRAN-Interface/Example')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
domain = geompy.MakeBoxDXDYDZ(1000, 1000, 200)
injector = geompy.MakeVertex(112.5, 112.5, 22.5)
extrator = geompy.MakeVertex(887.5, 887.5, 177.5)
obs1 = geompy.MakeVertex(362.5, 612.5, 82.5)
obs2 = geompy.MakeVertex(762.5, 512.5, 112.5)
obs3 = geompy.MakeVertex(487.5, 662.5, 172.5)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( domain, 'domain' )
geompy.addToStudy( injector, 'injector' )
geompy.addToStudy( extrator, 'extrator' )
geompy.addToStudy( obs3, 'obs1' )
geompy.addToStudy( obs3, 'obs2' )
geompy.addToStudy( obs3, 'obs3' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

aFilterManager = smesh.CreateFilterManager()
quad_mesh = smesh.Mesh(domain)
Regular_1D = quad_mesh.Segment()
Number_of_Segments_1 = Regular_1D.NumberOfSegments(40,None,[])
Quadrangle_2D = quad_mesh.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Hexa_3D = quad_mesh.Hexahedron(algo=smeshBuilder.Hexa)
isDone = quad_mesh.Compute()

obs1Group = quad_mesh.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "obs1")
obs1Group.Add([47855])
obs2Group = quad_mesh.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "obs2")
obs2Group.Add([38111])
obs3Group = quad_mesh.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "obs3")
obs3Group.Add([19140])
injGroup = quad_mesh.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "injector")
injGroup.Add([66245])
extGroup = quad_mesh.mesh.GetMesh().CreateGroup(SMESH.VOLUME, "extractor")
extGroup.Add([17916])


## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Hexa_3D.GetAlgorithm(), 'Hexa_3D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Number_of_Segments_1, 'Number of Segments_1')
smesh.SetName(quad_mesh.GetMesh(), 'quad_mesh')






if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
