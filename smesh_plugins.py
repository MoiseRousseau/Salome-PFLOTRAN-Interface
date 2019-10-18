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

ACTIVATE_PLUGIN = True

if ACTIVATE_PLUGIN:
  #get user
  import os
  user = os.getlogin()
  #load plugin
  path = '/home/%s/.config/salome/Plugins/' %(user)
  exec(open(path + 'PFLOTRAN_mesh_export/PFLOTRAN_Tools.py').read())
  exec(open(path + 'PFLOTRAN_EDZ_perm_dataset_creator/EDZ_permeability_dataset.py').read())
