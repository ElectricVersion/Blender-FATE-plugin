from io_fate_mdl.util import *
import mathutils

def read_basic_info(rdr):
    rdr.mdlData.version = rdr.read_str()
    rdr.mdlData.modelScale = rdr.read_num(FLOAT)
    rdr.mdlData.objectCount = rdr.read_num(UINT32)
    rdr.mdlData.totalVertexCount = rdr.read_num(UINT32)
    rdr.mdlData.tagCount = rdr.read_num(UINT32)
    rdr.mdlData.materialCount = rdr.read_num(UINT32)
    rdr.mdlData.textureCount = rdr.read_num(UINT32)
    
def read_mesh_section(rdr):
    for i in range(rdr.mdlData.tagCount):
        rdr.mdlData.tagNames.append(rdr.read_str())
        if rdr.mdlData.version == "V2.0":
            hasUserData = rdr.read_num(SINT16)
            if hasUserData > 0:
                rdr.mdlData.tagUserData.append(rdr.read_str())
    for i in range(rdr.mdlData.objectCount):
        # read the mesh header
        meshName = rdr.read_block(68)
        textureCount = rdr.read_num(UINT32)
        vertexCount = rdr.read_num(UINT32)
        triangleCount = rdr.read_num(UINT32)
        triangleStart = rdr.read_num(UINT32)
        headerSize = rdr.read_num(UINT32)
        uvStart = rdr.read_num(UINT32)
        verticesStart = rdr.read_num(UINT32)
        meshSize = rdr.read_num(UINT32)
        for j in range(triangleCount):
            a = rdr.read_num(UINT32)
            b = rdr.read_num(UINT32)
            c = rdr.read_num(UINT32)
            material = rdr.read_num(UINT32)
            rdr.mdlData.triangles.append((a,b,c))
        for j in range(vertexCount):
            u = rdr.read_num(FLOAT)
            v = 1.0 - rdr.read_num(FLOAT)
            rdr.mdlData.uvs.append((u,v))
        for j in range(vertexCount):
            currentVertex = VertexData()
            boneCount = rdr.read_num(UINT32)
            print("BONE COUNT" + str(boneCount))
            for k in range(boneCount):
                boneIndex = rdr.read_num(UINT32)
                print(boneIndex)
                x = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
                y = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
                z = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
                au = rdr.read_num(BYTE)
                av = rdr.read_num(BYTE)
                weight = rdr.read_num(FLOAT)
                if weight > 0.0:
                    print(weight)
                    currentVertex.bones.append(boneIndex)
                    currentVertex.boneOffsets[boneIndex] = [x,y,z]
                    currentVertex.boneWeights[boneIndex] = weight
            rdr.mdlData.vertices.append(currentVertex)
                
    # skeleton info
    boneCount = rdr.read_num(UINT32)
    for i in range(boneCount):
        bone = BoneData()
        bone.name = rdr.read_str()
        bone.parent = rdr.read_num(SINT32)
        transform = mathutils.Matrix.Identity(4)
        x = rdr.read_num(FLOAT) * rdr.mdlData.modelScale 
        y = rdr.read_num(FLOAT) * rdr.mdlData.modelScale 
        z = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
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
        #bone.localPos = position.copy()
        bone.transform = transform.to_4x4()
        bone.transform.translation = position
        bone.localTransform = bone.transform.copy()#.to_quaternion()
        #print(testMatrix)
        #print(testPosMatrix)
        rdr.mdlData.bones.append(bone)
        
    print("VERTEX COUNT" + str(vertexCount))