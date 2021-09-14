from .util import *

def write_basic_info(wtr):
    wtr.write_num(1.0, FLOAT) #model scale
    wtr.write_num(1, UINT32) #objects count (for now only one object can be exported per file)
    wtr.write_num(0, UINT32) #lights count
    wtr.write_num(0, UINT32) #points count
    wtr.write_num(0, UINT32) #paths count
    
    wtr.mdlData.activeObject = wtr.context.active_object
    materialSlots = wtr.mdlData.activeObject.material_slots.values()
    
    #get the number of materials
    for i in materialSlots:
        material = i.material
        wtr.mdlData.materials.append(material)
    
    #get the number of textures
    for i in wtr.mdlData.materials:
        materialNodes = i.node_tree.nodes.values()
        for j in materialNodes:
            print(j.bl_idname)
            if j.bl_idname == "ShaderNodeTexImage":
                wtr.mdlData.textures.append(j)
    
    wtr.write_num(len(wtr.mdlData.materials), UINT32) #materials count
    wtr.write_num(len(wtr.mdlData.textures), UINT32) #textures count

def write_mesh_section(wtr):
    for i in range(1): # change later to be the number of objects
        wtr.write_num(0.0, FLOAT) #pivot x
        wtr.write_num(0.0, FLOAT) #pivot y
        wtr.write_num(0.0, FLOAT) #pivot z
        
        meshObject = wtr.mdlData.activeObject.to_mesh(preserve_all_data_layers=True)
        vertices = meshObject.vertices.values()
        
        normalReferences = []
        vertexReferences = []
        normalReferences = []
        uvReferences = []
        uvLoops = meshObject.uv_layers.active.data.values()
        uvs = []
        for j in uvLoops:
            uvs.append(j.uv)
        faces = meshObject.polygons.values()
        for j in faces:
            for k in j.vertices:
                vertexReferences.append(k)
            for k in j.loop_indices:
                uvReferences.append(k)
        print("UV COUNT")
        print(len(uvs))
        print("UV REF COUNT")
        print(len(uvReferences))
        wtr.write_num(len(vertexReferences))
        for j in vertexReferences:
            wtr.write_num(j)
        
        wtr.write_num(len(vertices))
        for j in vertices:
            v = j
            index = v.index
            pos = v.co
            for k in pos:
                wtr.write_num(k, FLOAT)
        
        wtr.write_num(1, UINT16) #has UVs?
        for j in uvReferences:
            wtr.write_num(j)
        
        wtr.write_num(len(uvs)) # actual UVs
        for j in uvs:
            for k in j:
                wtr.write_num(k, FLOAT)
        
        hasNormals = 1
        wtr.write_num(hasNormals, UINT16) # has normals? (yes)
        if hasNormals > 0:
            for j in vertexReferences:
                wtr.write_num(j)
            actualNormalCount = len(vertices)
            wtr.write_num(actualNormalCount, UINT32)
            for j in range(actualNormalCount):
                blenderNormal = vertices[j].normal # the normal stored by blender
                au = compress_normal(blenderNormal[1], 2)
                av = compress_normal(blenderNormal[2], 1)
                print("NORMAL " + str(blenderNormal))
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