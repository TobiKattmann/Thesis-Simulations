# How to create the mesh

Excecute the `.geo` file with `gmsh *.geo` or open the file in the gmsh-GUI.

The script has to be run twice, with the option `Which_Mesh_Part=1` (creates fluid part) and `Which_Mesh_Part=2` (creates solid part).

Combine the 2 zonal meshes using the provided script
```bash
./combineSU2meshes.sh -f fluid_Res2.su2 -f solid_Res2.su2 -o 2D-PinArray_Res2.su2 -d 2
```
