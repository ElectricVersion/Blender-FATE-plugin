from .util import *

def read_basic_info(rdr):
    rdr.mdlData.modelScale = rdr.read_num(FLOAT)
    rdr.mdlData.objectCount = rdr.read_num(UINT32)
    rdr.mdlData.lightsCount = rdr.read_num(UINT32)
    rdr.mdlData.pointsCount = rdr.read_num(UINT32)
    rdr.mdlData.pathsCount = rdr.read_num(UINT32)
    rdr.mdlData.materialCount = rdr.read_num(UINT32)
    rdr.mdlData.textureCount = rdr.read_num(UINT32)

def read_mesh_section(rdr):
        for i in range(rdr.mdlData.objectCount):
            uvsLoaded = len(rdr.mdlData.uvs)
            verticesLoaded = len(rdr.mdlData.vertices)
            vertexReferencesLoaded = len(rdr.mdlData.vertexReferences)
            pivotX = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            pivotY = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            pivotZ = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            #vertices
            vertexCount = rdr.read_num(SINT32) # just for this submesh
            rdr.mdlData.totalVertexCount += vertexCount
            for j in range(vertexCount):
                rdr.mdlData.vertexReferences.append(rdr.read_num(UINT32) + verticesLoaded)
            actualVertexCount = rdr.read_num(SINT32) # not sure what an "actual" vertex means here, but thats what the code refers to it as
            for j in range(actualVertexCount):
                x = (pivotX + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                y = (pivotY + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                z = (pivotZ + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                rdr.mdlData.vertices.append( (x,y,z) )
            #uvs
            hasUvs = rdr.read_num(SINT16)
            for j in range(vertexCount):
                uvIndex = 0
                if (hasUvs):
                    uvIndex = rdr.read_num(UINT32) + uvsLoaded
                rdr.mdlData.uvReferences.append(uvIndex)
            actualUvCount = 1
            if hasUvs == 1:
                actualUvCount = rdr.read_num(SINT32)
                print("ACTUALUVCOUNT " + str(actualUvCount))
                for j in range(actualUvCount):
                    u = rdr.read_num(FLOAT)
                    v = rdr.read_num(FLOAT)
                    rdr.mdlData.uvs.append( (u, v) )
            else:
                for j in range(actualUvCount):
                    rdr.mdlData.uvs.append( (0.0, 0.0) )
                
            #normals
            hasNormals = rdr.read_num(SINT16)
            print("HAS NORMALS? " + str(hasNormals))
            if hasNormals > 0:
                for j in range(vertexCount):
                    rdr.mdlData.normalReferences.append( rdr.read_num(UINT32) + len(rdr.mdlData.normals))
                print("NORMAL REFERENCES", len(rdr.mdlData.normalReferences))
                actualNormalCount = rdr.read_num(UINT32)
                print("ACTUAL NORMAL COUNT " + str(actualNormalCount))
                for j in range(actualNormalCount):
                    au = rdr.read_num(BYTE)
                    av = rdr.read_num(BYTE)
                    nx, ny, nz = decompress_normal(au, av)
                    print("NORMALS", nx, ny, nz)
                    rdr.mdlData.normals.append( (nx, nz, ny) ) # i figured out how to decompress em lol
            else:
                if len(rdr.mdlData.normals) == 0:
                    rdr.mdlData.normals.append( (0,0,1) )
                for j in range(vertexCount):
                    rdr.mdlData.normalReferences.append( len(rdr.mdlData.normals) - 1)
            #vertex colors
            actualVertexColorCount = rdr.read_num(SINT32)
            for j in range(vertexCount):
                if j >= actualVertexColorCount:
                    rdr.mdlData.vertexColors.append( (1, 1, 1) )
                else:
                    r = rdr.read_num(UINT16)
                    g = rdr.read_num(UINT16)
                    b = rdr.read_num(UINT16)
                    rdr.mdlData.vertexColors.append( (r, g, b) )
            totalTriangleCount = rdr.read_num(UINT32)
            print("TOTAL TRI COUNT " + str(rdr.mdlData.totalFaceCount))
            submeshCount = rdr.read_num(UINT32)
            print("SUBMESH COUNT " + str(submeshCount))
            for j in range(submeshCount):
                materialId = rdr.read_num(SINT16)
                actualTriangleCount = rdr.read_num(UINT32)
                rdr.mdlData.totalFaceCount += actualTriangleCount
                print("SUBMESH TRI COUNT " + str(actualTriangleCount))
                for k in range(actualTriangleCount):
                    a = rdr.mdlData.vertexReferences[rdr.read_num(UINT32) + vertexReferencesLoaded]
                    b =  rdr.mdlData.vertexReferences[rdr.read_num(UINT32) + vertexReferencesLoaded]
                    c = rdr.mdlData.vertexReferences[rdr.read_num(UINT32) + vertexReferencesLoaded]
                    rdr.mdlData.triangles.append( (a, b, c) )