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
#
# Author : Moise Rousseau (2019), email at moise.rousseau@polymtl.ca

import salome_pluginsmanager

ACTIVATE_PLUGIN = True

if ACTIVATE_PLUGIN:
  # Check that GEOM and SMESH modules are present
  try:
    import GEOM
    from salome.geom import geomBuilder
    geompy = geomBuilder.New()
    
    import SMESH, SALOMEDS
    from salome.smesh import smeshBuilder
    smesh =  smeshBuilder.New()
  except:
    ACTIVATE_PLUGIN = False

if ACTIVATE_PLUGIN:
  exec(open('[SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/PFLOTRAN_Tools/Pflotran_export_plugin.py').read())
