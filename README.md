# PFC Numerical Simulation Data Files

This repository contains a collection of discrete element method (DEM) simulation data files built upon Itasca PFC (Particle Flow Code) 6.0, covering both two-dimensional (PFC2D) and three-dimensional (PFC3D) environments. The collection spans tutorial walkthroughs, analytical verification cases, engineering application examples, and Python scripting interfaces, providing a comprehensive reference for PFC-based numerical modeling workflows.

## Repository Structure

The repository is organized into three top-level directories. The `data/` directory holds a self-developed anchor bolt pull-out simulation project, structured as a sequential seven-step workflow. The `datafiles2d/` directory contains PFC2D data files, including examples, Python scripts, thermal analysis files, tutorials, and verification cases. The `datafiles3d/` directory mirrors this organization for PFC3D, additionally featuring CFD-DEM coupling simulations, a broader range of engineering examples, and an extended set of verification benchmarks.

Within `data/`, the project follows a save/restore chain architecture where each step builds upon the saved state of the previous one. The files `01_sample_build.dat` through `07_free_balance.dat` correspond to specimen generation, anchor hole creation, particle bonding, anchor ball generation and rigidification, pull-out loading, grout interface bonding, and free equilibrium, respectively. A detailed methodology document, `PFC建模要点.md`, accompanies these files and documents the modeling conventions and empirical guidelines developed throughout the project.

The `datafiles2d/` directory is divided into five subdirectories. The `examples/` folder includes a granular biaxial test, a rock mechanics testing suite, and a simple bonded block model. The `python/` folder provides basic Python syntax demonstrations and a GUI example. The `thermal/` folder contains a transient heat conduction analysis. The `tutorials/` folder offers eight introductory exercises covering fundamental concepts such as the Contact Model Assignment Table (CMAT), attributes and properties, bonding, fractured rock, hopper flow, inclusions, joint slip, and shallow foundations. The `verifications/` folder presents six analytical verification cases covering adhesive rolling resistance, the Burger viscoelastic model, cantilever beams, measure logic, rolling resistance, and wave propagation.

The `datafiles3d/` directory is more extensive, reflecting the richer capabilities of the three-dimensional environment. The `ccfd/` folder addresses CFD-DEM coupling with cases including cylinder flow, drop tests, an elbow geometry, a fluidized bed, one-way coupling, and a porous medium simulation, each accompanied by GiD mesh files. The `examples/` folder contains twelve engineering application cases: a buttress retaining structure, discrete fracture network (DFN) generation, fragmentation simulation, hopper flow, punch indentation, a ribbon blender with STL geometry, rockslide simulation, rock mechanics testing, a simple bonded block model, a sleeved triaxial test, a soft-bonded model, and a tunnel bonded block model. The `python/` folder provides six Python interface examples covering array interfaces, basic Python usage, GUI development, Python-PFC integration, UCS testing, and SciPy integration. The `thermal/` folder includes constrained and free thermal expansion cases. The `tutorials/` folder offers eleven exercises, including a creative table tennis simulation that demonstrates FISH callbacks and contact detection. The `verifications/` folder presents twelve analytical benchmark cases covering adhesive rolling resistance, array strength, the Burger model, cantilever beams, the Hertz contact model, measure logic, restitution, rolling resistance, settlement, sliding wedge stability, wave propagation, and coupled wave analysis.

## File Types

The repository contains a variety of file types, each serving a specific role within the PFC ecosystem. The primary script files use the `.p3dat` and `.p2dat` extensions for PFC3D and PFC2D command data files, respectively, while `.dat` serves as a generic PFC command file extension. Project files are stored as `.p3prj` and `.p2prj` for PFC3D and PFC2D, respectively, with `.prj` as the generic project file format. For PFC-FLAC coupled simulations, `.f3dat` and `.f3prj` extensions are used for FLAC3D command and project files. FISH language scripts — PFC's built-in programming language — are stored with `.p3fis`, `.p2fis`, or `.fis` extensions. Python scripts that interface with PFC's embedded Python interpreter use the `.py` extension. Three-dimensional geometry files imported into simulations use the `.stl` format, while input configuration files use `.inp`. Documentation is provided in Markdown (`.md`) format.

## Technical Highlights

### Contact Models

The simulations in this repository employ several contact models, each suited to different physical scenarios. The `linear` contact model is used during specimen generation and in non-bonded stages where particles interact through simple elastic contacts. The `linearpbond` (linear parallel bond) model is the primary bonding model used for rock, anchor, and grout cementation, providing both normal and shear bond strengths. The `hertz` contact model appears in verification cases that require non-linear elastic contact mechanics. The `burger` viscoelastic model is used in stress relaxation verifications, and the `adhesive_rolling_resistance` model is employed in repose angle verification cases where both adhesion and rolling resistance are significant.

### CMAT Conventions

The Contact Model Assignment Table (CMAT) conventions documented in this repository represent a systematic approach to assigning contact models based on particle group membership. For intra-group contacts where both ends of a contact belong to the same group, the `range group '<group>' match 2` syntax is used to precisely select contacts. For inter-group interfaces where the two ends belong to different groups, a custom FISH function with `range fish @<function>` is required, as the `match 2` keyword cannot express cross-group conditions. Ball-facet (wall) contacts are assigned a stiffness three times that of ball-ball contacts, expressed as `emod_facet = 3 × emod_lin`, to approximate rigid boundary behavior. Stiffness parameters are defined using the `method deform emod/kratio` approach rather than directly specifying `kn/ks`, allowing PFC to automatically compute normal and shear stiffness based on local contact geometry.

### Python Integration

PFC 6.0 features an embedded Python interpreter that enables programmatic access to model state and FISH variables. The Python examples in this repository demonstrate several integration patterns: accessing and modifying model variables through the Python API, performing numerical data processing with NumPy and SciPy, implementing custom graphical user interfaces, and exchanging array data between PFC and NumPy through the array interface module.

## Usage

To use these data files, install PFC 6.0 or a later version. Project files (`.p3prj` or `.p2prj`) can be opened directly in the PFC graphical interface, or individual data files can be executed using the `call` command. For the anchor bolt pull-out project in the `data/` directory, the seven step files should be executed sequentially from `01_sample_build.dat` through `07_free_balance.dat`, as each step restores the saved state from the previous step. For tutorial and example files, they can generally be run independently by calling the corresponding `.p3dat` or `.p2dat` file from within the PFC console.

The following example illustrates how to run one of the PFC3D tutorials:

```
; Run the "Balls in a Box" tutorial in PFC3D
call 'datafiles3d/tutorials/balls_in_a_box/cmlinear_simple.p3dat'
```

## Related Resources

Additional documentation and community resources are available through the [Itasca Consulting Group website](https://www.itascacg.com/), the [PFC online documentation](https://docs.itascacg.com/pfc/), and the [Itasca user forum](https://forum.itascacg.com/).

## License

This repository is intended for educational and research purposes. The PFC data files are written using the command syntax of Itasca PFC software. PFC and all related trademarks are the property of Itasca Consulting Group, Inc.
