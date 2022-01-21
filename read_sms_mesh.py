from .util import *
import mathutils

def read_basic_info(rdr):
    rdr.mdl_data.version = rdr.read_str()
    rdr.mdl_data.model_scale = rdr.read_num(FLOAT)
    rdr.mdl_data.object_count = rdr.read_num(UINT32)
    rdr.mdl_data.total_vertex_count = rdr.read_num(UINT32)
    rdr.mdl_data.tag_count = rdr.read_num(UINT32)
    rdr.mdl_data.material_count = rdr.read_num(UINT32)
    rdr.mdl_data.texture_count = rdr.read_num(UINT32)
    
def read_mesh_section(rdr):
    for i in range(rdr.mdl_data.tag_count):
        rdr.mdl_data.tag_names.append(rdr.read_str())
        if rdr.mdl_data.version == "V2.0\0":
            has_user_data = rdr.read_num(SINT16)
            if has_user_data > 0:
                rdr.mdl_data.tag_user_data.append(rdr.read_str())
    for i in range(rdr.mdl_data.object_count):
        # read the mesh header
        mesh_name = rdr.read_block(68)
        rdr.mdl_data.object_names.append(mesh_name)
        texture_count = rdr.read_num(UINT32)
        vertex_count = rdr.read_num(UINT32)
        triangle_count = rdr.read_num(UINT32)
        triangle_start = rdr.read_num(UINT32)
        header_size = rdr.read_num(UINT32)
        uv_start = rdr.read_num(UINT32)
        vertices_start = rdr.read_num(UINT32)
        mesh_size = rdr.read_num(UINT32)
        existing_verts = len(rdr.mdl_data.vertices)
        for j in range(triangle_count):
            a = rdr.read_num(UINT32) + existing_verts
            b = rdr.read_num(UINT32) + existing_verts
            c = rdr.read_num(UINT32) + existing_verts
            material = rdr.read_num(UINT32)
            rdr.mdl_data.triangles.append((a,b,c))
        for j in range(vertex_count):
            u = rdr.read_num(FLOAT)
            v = 1.0 - rdr.read_num(FLOAT)
            rdr.mdl_data.uvs.append((u,v))
        for j in range(vertex_count):
            current_vertex = Vertex_Data()
            bone_count = rdr.read_num(UINT32)
            #print("BONE COUNT" + str(bone_count))
            for k in range(bone_count):
                bone_index = rdr.read_num(UINT32)
                #print(bone_index)
                x = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
                y = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
                z = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
                au = rdr.read_num(BYTE)
                av = rdr.read_num(BYTE)
                weight = rdr.read_num(FLOAT)
                if weight > 0.0:
                    #print(weight)
                    current_vertex.bones.append(bone_index)
                    current_vertex.bone_offsets[bone_index] = [x,y,z]
                    current_vertex.bone_weights[bone_index] = weight
            rdr.mdl_data.vertices.append(current_vertex)
                
    # skeleton info
    bone_count = rdr.read_num(UINT32)
    for i in range(bone_count):
        bone = Bone_Data()
        bone.name = rdr.read_str()
        bone.parent = rdr.read_num(SINT32)
        transform = mathutils.Matrix.Identity(4)
        x = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale 
        y = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale 
        z = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
        position = mathutils.Vector( (x,y,z) )
        
        transform[0][0] = rdr.read_num(SINT16) / 32767.0
        transform[0][1] = rdr.read_num(SINT16) / 32767.0
        transform[0][2] = rdr.read_num(SINT16) / 32767.0
        
        transform[1][0] = rdr.read_num(SINT16) / 32767.0
        transform[1][1] = rdr.read_num(SINT16) / 32767.0
        transform[1][2] = rdr.read_num(SINT16) / 32767.0
        
        transform[2][0] = rdr.read_num(SINT16) / 32767.0
        transform[2][1] = rdr.read_num(SINT16) / 32767.0
        transform[2][2] = rdr.read_num(SINT16) / 32767.0
        
        #transform[3][0] = x
        #transform[3][1] = y
        #transform[3][2] = z
        
        bone.pos = position
        #bone.local_pos = position.copy()
        bone.transform = transform.to_4x4()
        bone.transform.translation = position
        bone.local_transform = bone.transform.copy()#.to_quaternion()
        #print(test_matrix)
        #print(test_pos_matrix)
        rdr.mdl_data.bones.append(bone)
        
    #print("VERTEX COUNT" + str(vertex_count))