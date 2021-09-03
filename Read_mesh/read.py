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
# See http://www.salome-platform.org/
#
# Author : Moise Rousseau (2021), email at rousseau.moise@gmail.ca

import salome
import SMESH
from salome.smesh import smeshBuilder
from qtsalome import QFileDialog, QMessageBox
import numpy as np
import h5py



def gui_input_file():
  dialog = QFileDialog()
  exts = "All File (*);;PFLOTRAN implicit mesh (*.ugi);; PFLOTRAN implicit binary mesh (*.h5)"
  f_in = dialog.getOpenFileName(None, "Select an input mesh", 
                                 "", exts)
  f_in = f_in[0]
  if not f_in:
    return None
  return f_in
  

def elem_reshape(elem):
  n = len(elem)
  i = 0
  while i < n:
    n_node = elem[i]
    n_z = np.sum(elem[i+1:i+n_node] == 0)
    if n_z != 0:
      size = n_z + n_node
      break
    i += n_node
  if n%size:
    print("ERROR")
    return None
  return elem.reshape(elem, (n//size,size))
  

def read_ugi(src):
  mesh = open(src,'r')
  n_e, n_v = [int(x) for x in mesh.readline().split()]
  elem = np.zeros((n_e,8),dtype='i8')
  for iline in range(n_e):
    line = [int(x) for x in mesh.readline().split()[1:]]
    elem[0:len(line)] = line
  vert = np.zeros((n_v,3),dtype='i8')
  for iline in range(n_v):
    vert[0:len(line)] = [float(x) for x in mesh.readline().split()]
  mesh.close()
  return vert, elem
  
def read_h5(src):
  mesh = h5py.File(src, 'r')
  vert = np.array(mesh["Domain/Vertices"])
  elem = np.array(mesh["Domain/Cells"])[:,1:]
  #if len(elem.shape) == 1:
  #  print("Flat element array, reshape it")
  #  elem = elem_reshape(elem)
  mesh.close()
  return vert, elem


def pflotran_to_salome_order(n):
  n = [int(x) for x in n if x]
  if len(n) == 4:
    new_nodes = [n[0],n[2],n[1],n[3]]
  elif len(n) == 5:
    new_nodes = [n[0],n[3],n[2],n[1],n[4]]
  elif len(n) == 6:
    new_nodes = [n[3],n[4],n[5],n[0],n[1],n[2]]
  elif len(n) == 8:
    new_nodes = [n[0],n[3],n[2],n[1],n[4],n[7],n[6],n[5]]
  return new_nodes
  

def pflotran_read(context):
  #get file
  src = gui_input_file()
  if src is None:
    return
  ext = src.split('.')[-1]
  if ext not in ['h5','ugi']:
    print("Trying autodetect mesh format (binary or ascii)")
    try:
      mesh = h5py.File(src,'r')
      mesh.close()
      ext = 'h5'
      print("Mesh is binary")
    except:
      ext = 'ugi'
      print("Mesh is probably ascii")
  
  #read mesh
  print("Read mesh")
  if ext == "ugi":
    vert, elem = read_ugi(src)
  else:
    vert, elem = read_h5(src)
  print(f"Read {len(vert)} vertices and {len(elem)} cells")
  
  #publish mesh
  smesh = smeshBuilder.New()
  M = smesh.Mesh()
  M.SetName(src.split('/')[-1])
  print("Add vertices")
  for (X,Y,Z) in vert:
    M.AddNode(float(X),float(Y),float(Z))
  print("Add cells")
  for cell in elem:
    M.AddVolume(pflotran_to_salome_order(cell))
      
  print("Create groups")
  if ext == 'h5':
    mesh = h5py.File(src,'r')
    if "Regions" in mesh.keys(): 
      for reg in list(mesh["Regions"].keys()):
        grp = M.CreateEmptyGroup(SMESH.VOLUME, reg)
        grp.Add([int(x) for x in np.array(mesh[f"Regions/{reg}/Cell Ids"])])
  
  if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()
  print("End!")
  return
  
  

