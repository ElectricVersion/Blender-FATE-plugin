import struct

UINT32 = {"format": "L", "size": 4}
SINT32 = {"format": "l", "size": 4}
UINT16 = {"format": "H", "size": 2}
SINT16 = {"format": "h", "size": 2}
FLOAT  = {"format": "f", "size": 4}
BYTE  = {"format": "b", "size": 1}

class VertexData:
    def __init__(self):
        self.references = []
        self.uvPos = []
        self.pos = None

class ModelData:
    textureNames = {}
    materialNames = {}
    userData = {}
    uvs = []
    vertices = []
    triangles = []
    normals = []
    vertexColors = []
    uvReferences = []
    vertexReferences = []
    
    modelScale = 1.0
    objectCount = 0
    lightsCount = 0
    pointsCount = 0
    pathsCount = 0
    materialCount = 0
    textureCount = 0
    totalVertexCount = 0
    totalTriangleCount = 0
    
    def __init__(self):
        return

class Reader:
    filePosition = 0
    txtData = None
    mdlData = ModelData()
    
    def __init__(self, p_input):
        self.filePosition = 0
        self.txtData = p_input
        
    def read_num(self, p_type = UINT32):
        output = []
        for i in range(p_type["size"]):
            output.append(self.txtData[self.filePosition + i])
        
        self.filePosition += p_type["size"]
        output = struct.unpack(p_type["format"], bytes(output))[0]
        print("Read " + str(p_type["size"]) + " bytes: " + str(output))
        
        return output
        
    def read_str(self, p_delim = '\0'):
        output = ""
        currentChar = None
        while currentChar != p_delim:
            currentChar = bytes([self.txtData[self.filePosition]]).decode("utf-8")
            output += currentChar
            self.filePosition += 1
        print("Read string: " + output)
        return output
