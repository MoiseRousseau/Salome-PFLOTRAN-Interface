# Salome PFLOTRAN Interface

Interface the Salome CAD software (https://www.salome-platform.org/) with the finite volume PFLOTRAN reactive transport subsurface simulator (https://www.pflotran.org/). This interface take the form of a Python plugin in Salome software (write in Python 3) and export mesh and groups created by Salome mesh module into a readable format by PFLOTRAN code. Various PFLOTRAN input format are implemented (ASCII and HDF5 file and unstructured implicit/explicit grid description). This plugin was developped to facilitate simulation of several phenomenons in complex geometries which can not be generated and/or meshed within PFLOTRAN. 

## Features
* Export 3D meshes created within Salome mesh module in a readable format by PFLOTRAN.
* Plugin writen in Python 3
* Unstructured implicit / explicit grid type format.
* Export 3D meshes in ASCII or HDF5 format.
* Around 400,000 elements per minutes on single thread and on a Intel Core i5 5300U.
* Export 3D groups (parts of the principal mesh) in HDF5 format to define region in PFLOTRAN.
* Export 2D groups in ASCII format to define boundary / initial condition (HDF5 format not implemented in PFLOTRAN yet).

## Features to come:
* Clipped Voronoi meshes
* PFLOTRAN input file autocompletion

## Getting Started

This plugin was tested on the latest release of Salome (which is up to date 9.4.0) running on Ubuntu 19.10. Nevertheles, it should work for newer release of Salome and for other platform. Note Salome switch to Python 3 since version 9.2.0 (February 2019) and consequently, the plugin could not compatible with older Salome version than 9.2.0.

### Prerequisites

The plugin should work as is for ASCII output. Yet, if you want to use the HDF5 file output (which is a better choice at my thought - faster and less hard drive space), you may have to install the h5py module within Salome:
1. Go to your Salome installation folder and open a terminal.
2. Make sure you have an C++ compiler installed, such as gcc (https://gcc.gnu.org/). If not, install it (or update it) with the command: 
```
sudo apt-get install gcc
```
3. Make a symbolic link from the Salome Python folder to the ```/usr/lib/``` directory. This step is needed for ```gcc``` to compile ```h5py``` source (Remplace ```$SalomeRootFolder``` by the Salome path): 
```
sudo ln -s $SalomeRootFolder/Python/lib/libpython3.6.so /usr/lib/libpython3.6.so
```
3. Setup the Salome environment with the command: 
```
./salome context
```
4. Install the `h5py` module with the command: 
```
pip3 install h5py
```
8. h5py is now installed. You can test it by launching Salome and typing the following command in the TUI: ```import h5py```. This command should not return an error.

### Installing

Installation of the plugin is done in three steps:
1. Download the repository in your machine
2. Unzip it into the folder `/home/$YOUR_USER_NAME/.config/salome/Plugins/`
3. You are ready to go

## Use the plugin

To export meshes from Salome to PFLOTRAN:
1. Click on `Mesh/SMESH plugins/Salome-PFLOTRAN-Interface/Export mesh to PFLOTRAN`
2. Select the mesh you want to export by clicking `Select` and select the mesh in Salome object browser
3. If you want to export group as PFLOTRAN regions, click on the corresponding checkbox and use to +/- pushbutton to add or remove groups. You can provide region name by changing the `Name` cell value
4. Select the desired output format and grid format (note explicit grid format with HDF output is not implemented in PFLOTRAN yet).
5. Provide an ouput file
6. If you want your PFLOTRAN input file autocompleted with minimum command you need to provide and grid and region already defined, check the corresponding box (not working yet).
7. Press `OK` to start the exportation

An example Salome study file is provided in the folder `example`. You can open it, load the SMESH module and have a look of the different meshes.

## Know limitations

Free volume meshing (like tetrahedral meshes) are the most convenient way to generate meshes. However, PFLOTRAN use a finite volume discretization and require a orthogonal mesh to be accurante. This mean all the vector linking two adjacent cells need to be normal to the face between those two cells. This condition is not meet when using tetrahedral mesh and can lead to significant error in the final solution.
A workaround  is to generate first a tetrahedral mesh and after, convert it into a Voronoi diagram. This way, we ensure every faces is normal to the vector linking the two cell centers. Moreover, the NETGEN algorithm seems to generate tetrahedral whose dual is a centroidal Voronoi diagram (CVD). I am currently working on this.

## Troubleshooting

If you got any difficulties in installing or using the plugin, or you would like new features to be implemented, feel free to email me. You could find my contact in header of ```PFLOTRAN_Tools.py``` file.

## Authors

* **Moïse Rousseau** - *Initial work*

## License

This project is licensed under the GPL version 3 License - see the [LICENSE.md](LICENSE.md) file for details


