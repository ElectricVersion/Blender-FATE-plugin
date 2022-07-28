from .util import *
from mathutils import *
#import mathutils

def write_basic_info(wtr):
    wtr.write_str("V2.0")
    wtr.write_num(1.0, FLOAT) #model scale
    wtr.write_num(1, UINT32) #mesh count (for now only one object can be exported per file)
    
    wtr.mdl_data.active_object = wtr.context.active_object
    material_slots = wtr.mdl_data.active_object.material_slots.values()
    
    wtr.mdl_data.active_mesh = wtr.mdl_data.active_object.to_mesh(preserve_all_data_layers=True)
    wtr.mdl_data.vertices = list(wtr.mdl_data.active_mesh.vertices)
    wtr.mdl_data.triangles = list(wtr.mdl_data.active_mesh.polygons)
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
        mesh_object = wtr.mdl_data.active_mesh
        vertices = list(mesh_object.vertices)
        faces = list(mesh_object.polygons)
        mesh_name = mesh_object.name.ljust(68, '\0')
        wtr.write_str(mesh_name, False)
        wtr.write_num(len(wtr.mdl_data.textures), UINT32)
        wtr.write_num(len(vertices), UINT32)
        wtr.write_num(len(faces), UINT32) #triangle count
        ptr_header_tri_start = len(wtr.txt_data) # save this address so we can go back and write it later
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
            wtr.write_num(j.vertices[0])
            wtr.write_num(j.vertices[1])
            wtr.write_num(j.vertices[2])
            wtr.write_num(j.material_index, SINT32)
        
        #start uv list
        header_uv_start = len(wtr.txt_data)
        
        uv_loops = mesh_object.uv_layers.active.data.values()
        mesh_loops = mesh_object.loops
        uvs = {}
        for loop_index in range(len(uv_loops)):
            j = uv_loops[loop_index]
            vert_index = mesh_loops[loop_index].vertex_index
            if vert_index not in uvs:
                uvs[vert_index]=j.uv
        print("UV LOOP COUNT", len(uv_loops))
        print("UVS COUNT", len(uvs))
        for j in uvs:
            wtr.write_num(uvs[j][0], FLOAT)
            wtr.write_num(uvs[j][1], FLOAT)
        
        #start vertex list
        header_vertex_start = len(wtr.txt_data)
        
        real_verts = mesh_object.vertices.values()
        
        armature = wtr.mdl_data.active_object.find_armature().data
        bones = list(armature.bones)
        #angle_correction = Matrix(((0,-1,0), (1,0,0), (0,0,1)))
        
        #first find every index
        bone_indices = {}
        for j in range(len(bones)):
            current_bone = bones[j]
            bone_indices[current_bone.name] = j
        #sort vertex groups
        vertex_groups = list(wtr.mdl_data.active_object.vertex_groups)
        group_bones = {}
        for j in vertex_groups:
            group_bones[j.index] = bone_indices[j.name]
        for j in vertices:
            vert = real_verts[j.index]
            groups = list(vert.groups)
            wtr.write_num(len(groups)) #bone count
            for k in groups:
                wtr.write_num(group_bones[k.group])
                current_bone = bones[group_bones[k.group]]
                parent_tfm = mathutils.Matrix.Identity(3)
                if current_bone.parent:
                    bone_parent = bone_indices[current_bone.parent.name]
                    parent_tfm = current_bone.parent.matrix_local.to_3x3() #bone_tfms[current_bone.parent.name]
                vert_rel = (parent_tfm.inverted() @ ( vert.co - current_bone.tail_local))
                wtr.write_num(vert_rel[0], FLOAT)
                wtr.write_num(vert_rel[1], FLOAT)
                wtr.write_num(vert_rel[2], FLOAT)
                blender_normal = vert.normal # the normal stored by blender
                au, av = compress_normal(blender_normal[0], blender_normal[1], blender_normal[2])
                wtr.write_num(au, BYTE)
                wtr.write_num(av, BYTE)
                wtr.write_num(k.weight, FLOAT)
        # skeleton time!
        
        wtr.write_num(len(bones))
        #now write the info
        for j in range(len(bones)):
            current_bone = bones[j]
            bone_name = current_bone.name
            bone_parent = -1
            parent_tfm = Matrix.Identity(3)
            parent_tail = Vector((0,0,0))
            if current_bone.parent:
                bone_parent = bone_indices[current_bone.parent.name]
                parent_tfm = current_bone.parent.matrix #bone_tfms[current_bone.parent.name]
            wtr.write_str(bone_name)
            wtr.write_num(bone_parent, SINT32)
            #position
            #bone_matrix = current_bone.matrix_local.inverted() @ parent_tfm#current_bone.matrix
            #bone_matrix = bone_matrix.to_3x3()
            #a = (current_bone.head @ mat) + mat.col[1]
            #bone_matrix = bpy.types.Bone.MatrixFromAxisRoll()
            bone_matrix = parent_tfm # current_bone.matrix
            #bone_pos = current_bone.tail_local - parent_tail #+ bone_matrix.col[1]# @ parent_tfm.inverted()#bone_matrix.translation#current_bone.head+
            bone_pos = parent_tfm @ current_bone.vector
            wtr.write_num(bone_pos[0], FLOAT)
            wtr.write_num(bone_pos[1], FLOAT)
            wtr.write_num(bone_pos[2], FLOAT)
            #transform
            # bone_matrix = bone_matrix@bone_matrix
            for matrix_row in bone_matrix.to_3x3().transposed():
                for matrix_col in matrix_row:
                    print(matrix_col)
                    wtr.write_num((round(matrix_col*32767)), SINT16)
        
    wtr.seek(ptr_header_tri_start)
    wtr.write_num(header_tri_start)
    wtr.seek(ptr_header_uv_start)
    wtr.write_num(header_uv_start)
    wtr.seek(ptr_header_vert_start)
    wtr.write_num(header_vertex_start)