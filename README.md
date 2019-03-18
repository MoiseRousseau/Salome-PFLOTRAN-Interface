# TO BE UPDATE
Follow the template https://gist.github.com/PurpleBooth/109311bb0361f32d87a2

# PFLOTRANTools
Interface the Salome (https://www.salome-platform.org/) preprocessor to create mesh, region and dataset for PFLOTRAN subsurface simulator (https://www.pflotran.org/)

To be use as a plugin for Salome
Work with the latest Salome 9.2.1 release
Only tested on Linux Ubuntu 18.04

For instance, only ASCII and HDF5 monomaterial mesh export is implemented. Switching between ASCII and HDF5 export is controled by 2 booleans in the "PFlotran_export_plugin.py". These boolean are "asciiOut" line 503 and "hdf5out" line 504.


# Installation instruction
To install PFLOTRANTools, you need to follow the next steps:
1. Download the repository and unzip it
2. Create a new folder nammed "PFLOTRAN_Tools" in the "[SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/" where [SalomeRootFolder] is the folder where you unzip Salome.
3. Copy/paste files "PFlotran_export_plugin.py" and "salome_plugin.py" in the new folder [SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/PFLOTRAN_Tools/
4. Open the file "salome_plugin.py"
5. Modify the last line :
exec(open('[SalomeRootFolder]/BINARIES-UB18.04/GUI/share/salome/plugins/gui/PFLOTRAN_Tools//PFLOTRAN_Tools.py').read())
by adding the path to the Salome root folder
6. The plugin is now installed. You can check it by opening Salome and click on Tools/Plugins/PFLOTRAN Tools/Export mesh to PFLOTRAN


# How to use the HDF5 output
PFLOTRANTools uses the h5py module (https://www.h5py.org/) to create HDF5 files for PFLOTRAN. This module is not installed by default in the Salome TUI. To install the module h5py, you need to follow the next steps:
1. Download the following package:
1.1. Pip wheel installator (https://pypi.org/project/pip/) - for example, the "pip-19.0.3-py2.py3-none-any.whl"
1.2. pkgconfig wheel installator (https://pypi.org/project/pkgconfig/) - for example, the "pkgconfig-1.4.0-py2.py3-none-any.whl" file
1.3. h5py source (https://pypi.org/project/h5py/) - for example, the "h5py-2.9.0.tar.gz" file

2. Copy these files in the "[SalomeRootFolder]/BINARIES-UB18.04/" folder and open a terminal in this folder
3. Make sure you have an C++ compiler installed, such as gcc (https://gcc.gnu.org/). If not, install it (or update it) with the command:
sudo apt-get install gcc
4. Make a symbolic link for gcc to found the Salome Python installation directory with:
sudo ln -s [SalomeRootFolder]/BINARIES-UB18.04/Python/lib/libpython3.5.so /usr/lib/libpython3.5.so
5. Setup the Salome environment with the command: ./../salome context
6. Install the pkgconfig module with the following command (depending of pkgconfig version you downloaded):
python pip-19.0.3-py2.py3-none-any.whl/pip install pkgconfig-1.4.0-py2.py3-none-any.whl 
7. Install the h5py module with the command: 
python pip-10.0.1-py2.py3-none-any.whl/pip install h5py-2.9.0.tar.gz
8. h5py is now installed. You can test it by launching Salome and typping the following command in the TUI: "import h5py". This command should not return an error.
