from .util import *

def write_basic_info(wtr):
    wtr.write_num(1.0, FLOAT) #model scale
    wtr.write_num(1, UINT32) #objects count (for now only one object can be exported per file)
    wtr.write_num(0, UINT32) #lights count
    wtr.write_num(0, UINT32) #points count
    wtr.write_num(0, UINT32) #paths count
    
    wtr.mdl_data.active_object = wtr.context.active_object
    material_slots = wtr.mdl_data.active_object.material_slots.values()
    
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
    
    wtr.write_num(len(wtr.mdl_data.materials), UINT32) #materials count
    wtr.write_num(len(wtr.mdl_data.textures), UINT32) #textures count

def write_mesh_section(wtr):
    for i in range(1): # change later to be the number of objects
        wtr.write_num(0.0, FLOAT) #pivot x
        wtr.write_num(0.0, FLOAT) #pivot y
        wtr.write_num(0.0, FLOAT) #pivot z
        
        mesh_object = wtr.mdl_data.active_object.to_mesh(preserve_all_data_layers=True)
        vertices = mesh_object.vertices.values()
        
        normal_references = []
        vertex_references = []
        normal_references = []
        uv_references = []
        uv_loops = mesh_object.uv_layers.active.data.values()
        uvs = []
        for j in uv_loops:
            uvs.append(j.uv)
        faces = mesh_object.polygons.values()
        for j in faces:
            for k in j.vertices:
                vertex_references.append(k)
            for k in j.loop_indices:
                uv_references.append(k)
        print("UV COUNT")
        print(len(uvs))
        print("UV REF COUNT")
        print(len(uv_references))
        wtr.write_num(len(vertex_references))
        for j in vertex_references:
            wtr.write_num(j)
        
        wtr.write_num(len(vertices))
        for j in vertices:
            v = j
            index = v.index
            pos = v.co
            for k in pos:
                wtr.write_num(k, FLOAT)
        
        wtr.write_num(1, UINT16) #has UVs?
        for j in uv_references:
            wtr.write_num(j)
        
        wtr.write_num(len(uvs)) # actual UVs
        for j in uvs:
            for k in j:
                wtr.write_num(k, FLOAT)
        
        has_normals = 1
        wtr.write_num(has_normals, UINT16) # has normals? (yes)
        if has_normals > 0:
            for j in vertex_references:
                wtr.write_num(j)
            actual_normal_count = len(vertices)
            wtr.write_num(actual_normal_count, UINT32)
            for j in range(actual_normal_count):
                blender_normal = vertices[j].normal#.normalized() # the normal stored by blender
                print("NORMAL " + str(blender_normal))
                au, av = compress_normal(blender_normal[1], blender_normal[2], blender_normal[0])
                print(au, av)
                wtr.write_num(au, BYTE)
                wtr.write_num(av, BYTE)
        wtr.write_num(0, UINT32) # vertex color count (none temporarily)
        
        #triangles
        wtr.write_num(len(faces)) #triangle count
        wtr.write_num(1) #submodel segments
        for j in range(1):
            wtr.write_num(0, UINT16) #material index
            wtr.write_num(len(faces)) # face count
            for k in faces:
                wtr.write_num(k.loop_indices[0])
                wtr.write_num(k.loop_indices[1])
                wtr.write_num(k.loop_indices[2])
                
        # skip the light section since you cant currently export lights