# How to create the mesh

Excecute the `.geo` file with `gmsh *.geo` or open the file in the gmsh-GUI.

The script has to be run twice, with the option `Which_Mesh_Part=1` (creates fluid part) and `Which_Mesh_Part=2` (creates solid part).

Combine the 2 zonal meshes using the provided script
```bash
./combineSU2meshes.sh -f fluid.su2 -f solid.su2 -o MeshCHT.su2 -d 2
```

The necessary `.cfg` files to write the FFD-box into the fresh mesh can be found in this repo under `1__2D-cylinder-in-crossflow/3__transient-paperRes/0__mesh`.

