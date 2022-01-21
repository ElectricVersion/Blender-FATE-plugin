from .util import *

def write_basic_info(wtr):
    wtr.write_str("V2.0")
    wtr.write_num(1.0, FLOAT) #model scale
    wtr.write_num(1, UINT32) #mesh count (for now only one object can be exported per file)
    
    wtr.mdl_data.active_object = wtr.context.active_object
    material_slots = wtr.mdl_data.active_object.material_slots.values()
    
    active_mesh = wtr.mdl_data.active_object.to_mesh(preserve_all_data_layers=True)
    wtr.mdl_data.vertices = active_mesh.loops.values()
    wtr.mdl_data.triangles = active_mesh.polygons.values()
    #get the number of materials
    for i in material_slots:
        material = i.material
        wtr.mdl_data.materials.append(material)
    
    #get the number of textures
    for i in wtr.mdl_data.materials:
        material_nodes = i.node_tree.nodes.values()
        for j in material_nodes:
            print(j.bl_idname)
            if j.bl_idname == "ShaderNodeTexImage":
                wtr.mdl_data.textures.append(j)
    
    
    wtr.write_num(len(wtr.mdl_data.vertices), UINT32) #vertex count
    wtr.write_num(0, UINT32) #tags count (I still dont know what this does oops so 0 for now)
    wtr.write_num(len(wtr.mdl_data.materials), UINT32) #materials count
    wtr.write_num(len(wtr.mdl_data.textures), UINT32) #textures count

def write_mesh_section(wtr):
    for i in range(1): # change later to be the number of objects
        mesh_object = wtr.mdl_data.active_object.to_mesh(preserve_all_data_layers=True)
        vertices = wtr.mdl_data.vertices
        faces = wtr.mdl_data.triangles
        mesh_name = mesh_object.name.ljust(68, '\0')
        wtr.write_str(mesh_name, False)
        wtr.write_num(len(wtr.mdl_data.textures), UINT32)
        wtr.write_num(len(wtr.mdl_data.vertices), UINT32)
        ptr_header_tri_start = len(wtr.txt_data) # save this address so we can go back and write it later
        wtr.write_num(len(wtr.mdl_data.triangles), UINT32) #triangle count
        wtr.write_num(0, UINT32) #triangle section start addr (maybe unused?)
        wtr.write_num(100, UINT32) #header size, idk why we need this (always the same)
        ptr_header_uv_start = len(wtr.txt_data) # save this address so we can go back and write it later
        wtr.write_num(0, UINT32) #location of UV header
        ptr_header_vert_start = len(wtr.txt_data) # save this address so we can go back and write it later
        wtr.write_num(0, UINT32) #location of verts header
        ptr_mesh_size = len(wtr.txt_data) # save this address so we can go back and write it later
        wtr.write_num(0, UINT32) #size of mesh
        
        #start triangle list
        header_tri_start = len(wtr.txt_data)
        for j in faces:
            wtr.write_num(j.loop_indices[0])
            wtr.write_num(j.loop_indices[1])
            wtr.write_num(j.loop_indices[2])
            wtr.write_num(j.material_index)
        
        #start uv list
        header_uv_start = len(wtr.txt_data)
        
        uv_loops = mesh_object.uv_layers.active.data.values()
        
        for j in uv_loops:
            wtr.write_num(j.uv[0], FLOAT)
            wtr.write_num(j.uv[1], FLOAT)
        
        #start vertex list
        header_vertex_start = len(wtr.txt_data)
        
        real_verts = mesh_object.vertices.values()
        
        for j in vertices:
            vert = real_verts[j.vertex_index]
            groups = vert.groups.values()
            wtr.write_num(len(groups)) #bone count
            for k in groups:
                wtr.write_num(k.group)
                wtr.write_num(vert[0], FLOAT)
                wtr.write_num(vert[1], FLOAT)
                wtr.write_num(vert[2], FLOAT)
                blender_normal = vertices[j].normal # the normal stored by blender
                au, av = compress_normal(blender_normal[1], blender_normal[2], blender_normal[0])
                wtr.write_num(au, BYTE)
                wtr.write_num(av, BYTE)
        
        # skip the light section since you cant currently export lights