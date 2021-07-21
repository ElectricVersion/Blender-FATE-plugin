from io_fate_mdl.util import *

def read_basic_info(rdr):
    rdr.mdlData.modelScale = rdr.read_num(FLOAT)
    rdr.mdlData.objectCount = rdr.read_num(UINT32)
    rdr.mdlData.lightsCount = rdr.read_num(UINT32)
    rdr.mdlData.pointsCount = rdr.read_num(UINT32)
    rdr.mdlData.pathsCount = rdr.read_num(UINT32)
    rdr.mdlData.materialCount = rdr.read_num(UINT32)
    rdr.mdlData.textureCount = rdr.read_num(UINT32)

def read_mesh_section(rdr):
        vertexReferences = []
        
        for i in range(rdr.mdlData.objectCount):
            pivotX = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            pivotY = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            pivotZ = rdr.read_num(FLOAT) * rdr.mdlData.modelScale
            vertexCount = rdr.read_num(SINT32) # just for this submesh
            rdr.mdlData.totalVertexCount += vertexCount
            for j in range(vertexCount):
                vertexReferences.append(rdr.read_num(UINT32))
            actualVertexCount = rdr.read_num(SINT32) # not sure what an "actual" vertex means here, but thats what the code refers to it as
            for j in range(actualVertexCount):
                x = (pivotX + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                y = (pivotY + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                z = (pivotZ + rdr.read_num(FLOAT)) * rdr.mdlData.modelScale
                rdr.mdlData.vertices.append( (x,y,z) )