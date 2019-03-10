# PFLOTRANTools
Interface the Salome (https://www.salome-platform.org/) preprocessor to create mesh, region and dataset for PFLOTRAN subsurface simulator (https://www.pflotran.org/)

To be use as a plugin for Salome
Work with the latest Salome 9.2.1 release
Only tested on Linux Ubuntu 18.04

For instance, only ASCII and HDF5 monomaterial mesh export is implemented. Switching between ASCII and HDF5 export is controled by 2 booleans in the "PFlotran_export_plugin.py". These boolean are "asciiOut" line 503 and "hdf5out" line 504.


# Installation instruction
To install PFLOTRANTools, follow the nest steps:
1. Download the repository and unzip it
2. Create a new folder nammed "PFLOTRAN_Tools" in the [SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/
3. Copy/paste files "PFlotran_export_plugin.py" and "salome_plugin.py" in the new folder [SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/PFLOTRAN_Tools/
4. Open the file "salome_plugin.py"
5. Modify the last line :
exec(open('[SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/PFLOTRAN_Tools//PFLOTRAN_Tools.py').read())
by adding the path to the Salome root folder
6. The plugin is now installed. You can check it by opening Salome and click on Tools/Plugins/PFLOTRAN Tools/Export mesh to PFLOTRAN


# How to use the HDF5 output
PFLOTRANTools uses the h5py module to create HDF5 files for PFLOTRAN. This module is not installed by default in the Salome TUI.
