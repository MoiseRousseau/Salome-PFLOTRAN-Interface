# Salome PFLOTRAN Interface

Interface the Salome CAD software (https://www.salome-platform.org/) with the finite volume PFLOTRAN reactive transport subsurface simulator (https://www.pflotran.org/). This interface take the form of a Python plugin in Salome software (write in Python 3) and export mesh and region created by Salome mesh module into a readable format by PFLOTRAN code. Various PFLOTRAN input format are implemented (ASCII and HDF5 file and unstructured implicit/explicit grid description). This plugin was developped to facilitate simulation of several phenomenons in complex geometries which can not be generated and/or meshed within PFLOTRAN. 

## Features
* Export 3D meshes created within Salome mesh module in a readable format by PFLOTRAN.
* Plugin writen in Python 3
* Unstructured implicit / explicit grid type format.
* Export 3D meshes in ASCII or HDF5 format.
* Around 400,000 elements per minutes on single thread and on a Intel Core i5 5300U.
* Export 3D submeshes (parts of the principal mesh) in HDF5 format to define region in PFLOTRAN.
* Export 2D submeshes in ASCII format to define boundary / initial condition (HDF5 format not implemented in PFLOTRAN yet).

## Features to come:
* Unstructured polyhedra format
* GUI
* Submeshes to export selection
* PFLOTRAN input file autocompletion

## Getting Started

This plugin was tested on the latest release of Salome (which is up to date 9.3.0) running on Ubuntu 18.04.2 LTS. Nevertheles, it should work for newer release of Salome and for other platform. Note Salome switch to Python 3 since version 9.2.0 (February 2019) and consequently, the plugin could not compatible with older version than 9.2.0.

### Prerequisites

The plugin should work as is for ASCII output. Yet, if you want to use the HDF5 file output (which is a better choice at my thought - faster and less hard drive space), you will need to install the h5py module within Salome. To do so, you can follow the following step:
1. Download the following package:
* **pip wheel installator**: https://pypi.org/project/pip/ - for example, the "pip-19.1.1-py2.py3-none-any.whl" one
* **pkgconfig wheel installator**: https://pypi.org/project/pkgconfig/ - for example, the "pkgconfig-1.5.1-py2.py3-none-any.whl" one
* and finally, the **h5py source**: https://pypi.org/project/h5py/ - for example, the "h5py-2.9.0.tar.gz" archive
2. Copy these files in the ```$SalomeRootFolder/BINARIES-UB18.04/``` folder and open a terminal in this folder (remplace ```$SalomeRootFolder``` with the path to your Salome installation)
3. Make sure you have an C++ compiler installed, such as gcc (https://gcc.gnu.org/). If not, install it (or update it) with the command: 
```
sudo apt-get install gcc
```
4. Setup the Salome environment with the command: 
```
./../salome context
```
5. Install first the ```pkgconfig``` module with: (the exact command may differ due to your version of `pip` and `pkgconfig` you downloaded): 
```
python pip-19.1.1-py2.py3-none-any.whl/pip install pkgconfig-1.5.1-py2.py3-none-any.whl
```
6. Make a symbolic link from the ```/usr/lib/``` directory to the Salome Python library. This step is needed for ```gcc``` to compile ```h5py``` source (for Salome 9.2.0 to 9.2.2, ```libpython3.6.so``` should be remplaced by ```libpython3.5.so```): 
```
sudo ln -s $SalomeRootFolder/Python/lib/libpython3.6.so /usr/lib/libpython3.6.so
```
7. Install the `h5py` module with the command: 
```
python pip-19.1.1-py2.py3-none-any.whl/pip install h5py-2.9.0.tar.gz
```
8. h5py is now installed. You can test it by launching Salome and typing the following command in the TUI: ```import h5py```. This command should not return an error.

### Installing

Installation of the plugin is done in three steps:
1. Download it.
2. Unzip it into the folder ```$SalomeRootFolder/BINARIES-UB18.04/GUI/share/salome/plugins/gui/``` where `$SalomeRootFolder` is the path to your Salome installation.

## Use the plugin

To export your mesh from Salome to PFLOTRAN:
1. Select the mesh, submesh or group of meshes you want to export
2. Click on `Tool/Plugins/PFLOTRAN Tools GUI/Export mesh to PFLOTRAN_GUI`
3. Your mesh and all its submeshes will be exported in the folder where you save your Salome study.

## Troubleshooting

If you got any difficulties in installing or using the plugin, or you would like new features to be implemented, feel free to email me. You could find my contact in header of ```PFLOTRAN_Tools.py``` file.

## Authors

* **Moïse Rousseau** - *Initial work*

## License

This project is licensed under the GPL version 3 License - see the [LICENSE.md](LICENSE.md) file for details


