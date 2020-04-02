# -*- coding: iso-8859-1 -*-
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
# See http://www.salome-platform.org/
#
# Author : Moise Rousseau (2019), email at moise.rousseau@polymtl.ca

import salome_pluginsmanager
import importlib

ACTIVATE_PLUGIN = True

if ACTIVATE_PLUGIN:
  #get user
  import os
  import sys

  #common to all plugin in .config/salome/Plugins folder
  try:
    user = '/home/' + os.getlogin()
  except:
    user = os.environ['HOME']
  path = '%s/.config/salome/Plugins/' %(user)
  
  
  # ==== PFLOTRAN PLUGINS ====
  #common path
  sys.path.append(path)
  
  #folder in Salome GUI
  common_folder = "Salome-PFLOTRAN-Interface/"
  
  #load Export plugin 
  sys.path.append(path+"PFLOTRAN_mesh_export/")
  import PFLOTRAN_Tools
  importlib.reload(PFLOTRAN_Tools)
  salome_pluginsmanager.AddFunction(common_folder + 'Export mesh to PFLOTRAN',
                                    'Export mesh and groups to PFLOTRAN readable format',
                                     PFLOTRAN_Tools.PFLOTRANMeshExport)
  
  #load grid check
  sys.path.append(path+'Grid_check/') #path to plugin component for importation
  import makeChecks
  salome_pluginsmanager.AddFunction('Salome-PFLOTRAN-Interface/Check mesh quality',
                                    'Compute statistics for mesh non orthogonality and skewness',
                                    makeChecks.checkNonOrthogonality)
  
  #load integral flux
  sys.path.append(path+'PFLOTRAN_integral_flux/')
  import Integral_flux  
  importlib.reload(Integral_flux)
  salome_pluginsmanager.AddFunction(common_folder + 'Integral Flux',
                                    'Export surface mesh for integral flux',
                                     Integral_flux.integralFluxExport)
  
  #load EDZ permeability plugin
  sys.path.append(path+'PFLOTRAN_EDZ_perm_dataset_creator/')
  import EDZ_permeability_dataset
  importlib.reload(EDZ_permeability_dataset)
  salome_pluginsmanager.AddFunction(common_folder + 'Create permeability dataset',
                                    'Create a permeability dataset corresponding to a EDZ',
                                     EDZ_permeability_dataset.EDZPermeabilityDataset)
                                     
  # ===== ADD OTHER PLUGIN BELOW ====

