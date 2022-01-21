from .util import *

def read_basic_info(rdr):
    rdr.mdl_data.model_scale = rdr.read_num(FLOAT)
    rdr.mdl_data.object_count = rdr.read_num(UINT32)
    rdr.mdl_data.lights_count = rdr.read_num(UINT32)
    rdr.mdl_data.points_count = rdr.read_num(UINT32)
    rdr.mdl_data.paths_count = rdr.read_num(UINT32)
    rdr.mdl_data.material_count = rdr.read_num(UINT32)
    rdr.mdl_data.texture_count = rdr.read_num(UINT32)

def read_mesh_section(rdr):
        for i in range(rdr.mdl_data.object_count):
            uvs_loaded = len(rdr.mdl_data.uvs)
            vertices_loaded = len(rdr.mdl_data.vertices)
            vertex_references_loaded = len(rdr.mdl_data.vertex_references)
            pivot_x = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
            pivot_y = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
            pivot_z = rdr.read_num(FLOAT) * rdr.mdl_data.model_scale
            #vertices
            vertex_count = rdr.read_num(SINT32) # just for this submesh
            rdr.mdl_data.total_vertex_count += vertex_count
            for j in range(vertex_count):
                rdr.mdl_data.vertex_references.append(rdr.read_num(UINT32) + vertices_loaded)
            actual_vertex_count = rdr.read_num(SINT32) # not sure what an "actual" vertex means here, but thats what the code refers to it as
            for j in range(actual_vertex_count):
                x = (pivot_x + rdr.read_num(FLOAT)) * rdr.mdl_data.model_scale
                y = (pivot_y + rdr.read_num(FLOAT)) * rdr.mdl_data.model_scale
                z = (pivot_z + rdr.read_num(FLOAT)) * rdr.mdl_data.model_scale
                rdr.mdl_data.vertices.append( (x,y,z) )
            #uvs
            has_uvs = rdr.read_num(SINT16)
            for j in range(vertex_count):
                uv_index = 0
                if (has_uvs):
                    uv_index = rdr.read_num(UINT32) + uvs_loaded
                rdr.mdl_data.uv_references.append(uv_index)
            actual_uv_count = 1
            if has_uvs == 1:
                actual_uv_count = rdr.read_num(SINT32)
                print("ACTUALUVCOUNT " + str(actual_uv_count))
                for j in range(actual_uv_count):
                    u = rdr.read_num(FLOAT)
                    v = rdr.read_num(FLOAT)
                    rdr.mdl_data.uvs.append( (u, v) )
            else:
                for j in range(actual_uv_count):
                    rdr.mdl_data.uvs.append( (0.0, 0.0) )
                
            #normals
            has_normals = rdr.read_num(SINT16)
            print("HAS NORMALS? " + str(has_normals))
            if has_normals > 0:
                for j in range(vertex_count):
                    rdr.mdl_data.normal_references.append( rdr.read_num(UINT32) + len(rdr.mdl_data.normals))
                print("NORMAL REFERENCES", len(rdr.mdl_data.normal_references))
                actual_normal_count = rdr.read_num(UINT32)
                print("ACTUAL NORMAL COUNT " + str(actual_normal_count))
                for j in range(actual_normal_count):
                    au = rdr.read_num(BYTE)
                    av = rdr.read_num(BYTE)
                    nx, ny, nz = decompress_normal(au, av)
                    print("NORMALS", nx, ny, nz)
                    rdr.mdl_data.normals.append( (nx, nz, ny) ) # i figured out how to decompress em lol
            else:
                if len(rdr.mdl_data.normals) == 0:
                    rdr.mdl_data.normals.append( (0,0,1) )
                for j in range(vertex_count):
                    rdr.mdl_data.normal_references.append( len(rdr.mdl_data.normals) - 1)
            #vertex colors
            actual_vertex_color_count = rdr.read_num(SINT32)
            for j in range(vertex_count):
                if j >= actual_vertex_color_count:
                    rdr.mdl_data.vertex_colors.append( (1, 1, 1) )
                else:
                    r = rdr.read_num(UINT16)
                    g = rdr.read_num(UINT16)
                    b = rdr.read_num(UINT16)
                    rdr.mdl_data.vertex_colors.append( (r, g, b) )
            total_triangle_count = rdr.read_num(UINT32)
            print("TOTAL TRI COUNT " + str(rdr.mdl_data.total_face_count))
            submesh_count = rdr.read_num(UINT32)
            print("SUBMESH COUNT " + str(submesh_count))
            for j in range(submesh_count):
                material_id = rdr.read_num(SINT16)
                actual_triangle_count = rdr.read_num(UINT32)
                rdr.mdl_data.total_face_count += actual_triangle_count
                print("SUBMESH TRI COUNT " + str(actual_triangle_count))
                for k in range(actual_triangle_count):
                    a = rdr.mdl_data.vertex_references[rdr.read_num(UINT32) + vertex_references_loaded]
                    b =  rdr.mdl_data.vertex_references[rdr.read_num(UINT32) + vertex_references_loaded]
                    c = rdr.mdl_data.vertex_references[rdr.read_num(UINT32) + vertex_references_loaded]
                    rdr.mdl_data.triangles.append( (a, b, c) )