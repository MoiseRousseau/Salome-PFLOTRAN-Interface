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
sk = geompy.Sketcher2D()
sk.addPoint(1.000000, 100.000000)
sk.addSegmentAbsolute(100.000000, 100.000000)
sk.addArcAbsolute(200.000000, 150.000000)
sk.addArcAbsolute(410.000000, 300.000000)
Sketch_1 = sk.wire()
domain = geompy.MakeBoxDXDYDZ(400, 400, 100)
src = geompy.MakeDividedDisk(10, 2, GEOM.SQUARE)
geompy.TranslateDXDYDZ(src, 0, 100, 0)
Pipe_1 = geompy.MakePipe(src, Sketch_1)
geompy.TranslateDXDYDZ(Pipe_1, -5, 0, 50)
Tunnel = geompy.MakePartition([domain], [Pipe_1], [], [], geompy.ShapeType["SOLID"], 0, [], 0)
[rock] = geompy.SubShapes(Tunnel, [2])
tunnel = geompy.CreateGroup(Tunnel, geompy.ShapeType["SOLID"])
geompy.UnionIDs(tunnel, [222, 189, 238, 106, 156])
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( domain, 'domain' )
geompy.addToStudy( src, 'src' )
geompy.addToStudy( Sketch_1, 'Sketch_1' )
geompy.addToStudy( Pipe_1, 'Pipe_1' )
geompy.addToStudy( Tunnel, 'Tunnel' )
geompy.addToStudyInFather( Tunnel, tunnel, 'tunnel' )
geompy.addToStudyInFather( Tunnel, rock, 'rock' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

model = smesh.Mesh(Tunnel)
NETGEN_1D_2D_3D = model.Tetrahedron(algo=smeshBuilder.NETGEN_1D2D3D)
NETGEN_3D_Parameters_1 = NETGEN_1D_2D_3D.Parameters()
NETGEN_3D_Parameters_1.SetMinSize( 5 )
NETGEN_3D_Parameters_1.SetSecondOrder( 0 )
NETGEN_3D_Parameters_1.SetOptimize( 1 )
NETGEN_3D_Parameters_1.SetChordalError( -1 )
NETGEN_3D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_3D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_3D_Parameters_1.SetFuseEdges( 1 )
NETGEN_3D_Parameters_1.SetQuadAllowed( 0 )
Regular_1D = model.Segment(geom=tunnel)
Number_of_Segments_1 = Regular_1D.NumberOfSegments(15)
Quadrangle_2D = model.Quadrangle(algo=smeshBuilder.QUADRANGLE,geom=tunnel)
Hexa_3D = model.Hexahedron(algo=smeshBuilder.Hexa,geom=tunnel)
rock_1 = model.GroupOnGeom(rock,'rock',SMESH.VOLUME)
tunnel_1 = model.GroupOnGeom(tunnel,'tunnel',SMESH.VOLUME)
[ rock_1, tunnel_1 ] = model.GetGroups()
NETGEN_3D_Parameters_1.SetMaxSize( 20 )
NETGEN_3D_Parameters_1.SetFineness( 2 )
NETGEN_3D_Parameters_1.SetCheckChartBoundary( 0 )
[ rock_1, tunnel_1 ] = model.GetGroups()
Number_of_Segments_1.SetNumberOfSegments( 8 )
[ rock_1, tunnel_1 ] = model.GetGroups()
[ rock_1, tunnel_1 ] = model.GetGroups()
tunnel_2 = Regular_1D.GetSubMesh()
#isDone = model.Compute()


## Set names of Mesh objects
smesh.SetName(tunnel_2, 'tunnel')
smesh.SetName(NETGEN_1D_2D_3D.GetAlgorithm(), 'NETGEN 1D-2D-3D')
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Hexa_3D.GetAlgorithm(), 'Hexa_3D')
smesh.SetName(tunnel_1, 'tunnel')
smesh.SetName(rock_1, 'rock')
smesh.SetName(model.GetMesh(), 'model')
smesh.SetName(Number_of_Segments_1, 'Number of Segments_1')
smesh.SetName(NETGEN_3D_Parameters_1, 'NETGEN 3D Parameters_1')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
