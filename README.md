# Salome PFLOTRAN Interface

Interface the Salome CAD software (https://www.salome-platform.org/) with the finite volume PFLOTRAN reactive transport subsurface simulator (https://www.pflotran.org/). This interface take the form of various Python scripts, and define Salome plugins which are callable from the GUI. This plugin was developed to facilitate simulation of several phenomenons in complex geometries which can not be generated and/or meshed within PFLOTRAN. It is intended to be used for engineering purpose.


## Features
*  Export mesh and groups created by Salome mesh module into a readable format by PFLOTRAN code. Various PFLOTRAN input format are implemented (ASCII and HDF5 file and unstructured implicit/explicit grid description). Export directly 3D and 2D groups as region in PFLOTRAN to easily define material repartition and boundary condition.
* Mesh quality assessment: non-orthogonality and skewness check.
* INTEGRAL_FLUX card creator. Export 2D groups in a readily file readable by PFLOTRAN in various format: by coordinates and normal, vertices (for implicit unstructured grid only) and by cell ids.
* Permeability dataset creator for excavated damaged zone. Given a 3D mesh group and a mesh group surface, compute for every cell in the considered mesh or group the distance to the considered surface and the unit vector direction, and store it into a HDF5 file. Create afterward a cell indexed dataset of permeability according to [Mourzenko et al. (2012)](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.86.026312).
* Useful examples in the Example folder, to have a quick look at what Salome is capable of.


## Getting Started

This plugin was tested on the latest release of Salome (which is up to date 9.6.0) running on Ubuntu 20.04. 
Nevertheless, it should work for newer release of Salome and for other platform. 
Note Salome switch to Python 3 since version 9.2.0 (February 2019) and consequently, the plugin is not compatible as is with Salome version older than 9.2.0.

### Installation

Installation of the plugin is done in three steps:
1. Download the repository in your machine
2. Unzip it and copy the content of the folder `Salome-PFLOTRAN-Interface` into `$HOME/.config/salome/Plugins/`
3. You are ready to go

Note the plugin should work as is for mesh export in ASCII output. However, if you want to use the HDF5 file output (which is a better choice at my thought - faster and less hard drive space), you may have to install the h5py module within Salome:

1. Go to your Salome installation folder and open a terminal.
2. Make sure you have an C++ compiler installed, such as GCC (https://gcc.gnu.org/). If not, install it (or update it) with the command ```sudo apt install gcc``` (On Ubuntu).
3. Install BLAS and LAPACK header:
```
sudo apt install libblas-dev liblapack-dev 
```
4. Make a symbolic link from the Salome Python folder to the ```/usr/lib/``` directory. This step is needed for GCC to compile h5py sources (Remplace ```$SalomeRootFolder``` by your path to Salome): 
```
sudo ln -s $SalomeRootFolder/BINARIES-UB20.04/Python/lib/libpython3.6.so /usr/lib/libpython3.6.so
```
5. Setup the Salome environment with the command: 
```
./salome context
```
6. Upgrade the `pip` version of Salome and install the whell package:
```
pip3 install --upgrade pip
pip3 install wheel
```
7. Since Salome 9.6.0, the header file `xlocate.h` lack in Salome Python installation which results in error during h5py compilation. So you have to manually copy the header (available at the root of this repository) into the folder `$SalomeRootFolder$/BINARIES-UB20.04/Python/include/python3.6/`
6. Finally, install the `h5py` module with the command: 
```
pip3 install h5py
```
8. h5py is now installed. You can test it by launching Salome and typing the following command in the TUI: ```import h5py```. This command should not return an error.


## Use the plugin

### Export a mesh

To export meshes from Salome to PFLOTRAN:
1. Click on `Mesh/SMESH plugins/Salome-PFLOTRAN-Interface/Export mesh to PFLOTRAN`
2. Select the mesh you want to export by clicking `Select` and select the mesh in Salome object browser
3. If you want to export group as PFLOTRAN regions, click on the corresponding checkbox and use to +/- push-button to add or remove groups. You can provide region name by changing the `Name` cell value
4. Select the desired output format and grid format (note explicit grid format with HDF5 output is not implemented in PFLOTRAN yet).
5. Provide an output file
6. If output format is HDF5, you may like to compress the output to reduce the size of your HDF5 mesh. In this case, HDF5 library in PETSC and in Salome need to be compiled with the `zlib` library. Compression could reduce mesh size by a 10 factor in a 300K elements mesh.
6. Press `OK` to start the exportation.

Note: if you use the explicit grid format, the plugin also create another file called `..._Domain.h5`.
It is intended to be used with the Python script `pflotran_explicit_binder.py`, and to allow proper visualization of your simulation. 

### Mesh quality 

Free volume meshing (like tetrahedral meshes) are the most convenient way to generate meshes. However, PFLOTRAN use a finite volume discretization and require orthogonal mesh to be accurate. This mean all the vector linking two adjacent cells need to be normal to the face between those two cells. This condition is not meet when using tetrahedral mesh and can lead to significant error in the final solution.

Mesh quality can be assessed through the `Salome-PFLOTRAN-Interface/Check mesh quality` function, which computes statistics about mesh non-orthogonality (the angle between the face normal and the two-cells centroïd vector) and mesh skewnesss (distance between face centroid and face / the two-cells centroïd vector intersection).

### Integral flux

Integral flux are created by the `Salome-PFLOTRAN-Interface/Integral flux function`:
1. Select the mesh face group where you want to applied the integral flux
2. Select the output format between the three proposed. I recommend the use of the "Cell Ids" format for faces located between two volumes (i.e. in the model), and "Coordinates and direction" for faces on the boundary. Note I experience some unrecognized faces when running PFLOTRAN with the "Coordinates and direction" and "Vertices" formats.
3. Select the desired integral flux option (Signed, positive only or absolute flux).
4. Direction of the flux is determined by the left hand rule. Check "Reverse direction" to reverse the flux direction computation.
5. Select the output file and click on "Ok".
6. The integral flux file is created. The integral flux is included in your PFLOTRAN input file with:
```
INTEGRAL_FLUX
  NAME [name_of_the_integral_flux]
  EXTERNAL_FILE [salome_integral_flux_output]
END
```

### Excavated damage zone permeability dataset creator

Permeability dataset are created by the `Salome-PFLOTRAN-Interface/Create permeability dataset`:
1. Select the mesh group you want to assign the permeability dataset.
2. Select the surface mesh group from which distance and unit vector will be computed.
3. Select the output file
4. Enter the excavated zone properties: trace length, attenuation length, fracture radius, aperture and anisotropy.
5. Select the permeability model
6. Select the equivalent permeability coupling (only Standard - sum of fracture and matrix permeability - is implemented yet).
7. Enter the matrix permeability and click on "Ok".

The creation of the permeability dataset can be quite long. Salome need to compute for each point in the input mesh the distance to the surface. Performances on a single core i7-6820HQ machine: 200K elements per hour.

## Examples

Several example of Salome study is provided in the folder `Example` which can be loaded using `File / Load Script`. A small description is provided below:
* _compare-struct-unstruct-and-explicit-grid_: Contains three PFLOTRAN input files to compare pressure and concentration at three different points and according to three meshes: one generated by PFLOTRAN preprocessor, and the two last using the implicit/explicit export capacity of this suite of plugins. First load the script `salome_script.py` with Salome, go into the SMESH module and export the `quad_mesh` mesh. Second, run the three PFLOTRAN input files `ref.in`, `exp.in` and `imp.in` (you may probably have to change the name of your exported grids). Then, visualize the results with the Python script `plot_result.py`.
* _experimental-waste-rock-pile_: This Salome script create a 3D model and its spatial discretization of a experimental waste rock pile with a flow control layer [(Dubuc, 2018)](https://publications.polymtl.ca/3187/). Illustrate the use of the integral flux plugin to assess the amount of water which is diverted by the control layer.
* _tunnel_: Simple 3D model of a tunnel and the surrounding rock. Can be use as a starting point to create an excavated damaged zone permeability dataset. Starting point because the mesh need to be refined around the tunnel (with the viscous layer option from Salome for example), among other reason.
* _voronoi-mesh_: Illustrate a Voronoi mesh build as the dual of the tetrahedral mesh. Voronoi meshes can be exported to PFLOTRAN with the explicit format. The Voronoi mesher is available [here](https://github.com/MoiseRousseau/SALOME-Voronoi).

## Limitation

Salome software is not a geomodeler. This means its CAD capability is sometimes not adapted to represent topography or interface between geological layer, and may have some problem to deal with complex geological structure. Yet, for engineering applications like the above example, it should do the trick.


## Troubleshooting

If you got any difficulties in installing or using the plugin, or you would like new features to be implemented, feel free to email me. You could find my contact in header of `smesh_plugin.py` file.

## Authors

* **Moïse Rousseau** - *Initial work*

## Acknownlegment

* **Fabian Bottcher** - For its help in testing the plugin and its bugs reporting
* **Thomas Pabst** - My PhD supervisor
* All of you which will use the plugin and give me feedback to improve it

## License

This project is licensed under the GPL version 3 License - see the [LICENSE.md](LICENSE.md) file for details


